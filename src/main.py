import os
import requests

import streamlit as st

from streamlit_quill import st_quill
import json
import streamlit.components.v1 as components
from pathlib import Path
from argparse import ArgumentParser

import logging

logger = logging.getLogger(__name__)

parser = ArgumentParser()
parser.add_argument("-d", "--dir", default="data")
parser.add_argument("-b", "--backend")
parser.add_argument("-l", "--loglevel", default="INFO")
args = parser.parse_args()

data_dir = Path(args.dir)
if not data_dir.is_absolute():
    data_dir = Path.cwd() / data_dir

logging.basicConfig(
    format="%(levelname)s %(asctime)s: %(message)s", level=args.loglevel
)

backend = args.backend

root_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(root_dir, "frontend/build")

st.set_page_config(layout="wide")

concept_view = components.declare_component("ConceptView", path=build_dir)
# concept_view = components.declare_component("ConceptView", url="http://localhost:3001")

models = requests.get(f"{backend}/models").json()["model_endpoints"]
endpoints = {model["name"]: f"{backend}/{model['endpoint']}" for model in models}

if "concept_lists" not in st.session_state:
    st.session_state["concept_lists"] = {}
if "note_content" not in st.session_state:
    st.session_state["note_content"] = ""

displayed_concept_list = {}


def default_filename(dir: Path):
    n = 0
    filenames_in_pattern = list(dir.glob("doc_*.json"))
    if filenames_in_pattern:
        n = max([int(s.stem.split("_")[1]) for s in filenames_in_pattern]) + 1
    return f"doc_{n}.json"


def save_document(filename):
    data_dir.mkdir(exist_ok=True)
    with open(data_dir / Path(filename), "w") as file:
        file.write(
            json.dumps(
                {
                    "text": st.session_state["note_content"],
                    "data": displayed_concept_list,
                },
                indent=2,
            )
        )


def load_document(filename):
    logger.info(f"Opening: {filename}")
    with open(data_dir / Path(filename), "r") as file:
        json_content = json.load(file)
        st.session_state["concept_lists"] = json_content["data"]
        st.session_state["note_content"] = json_content["text"]


@st.cache_data
def code_note(note: str) -> dict[str, dict]:
    logger.info(f"coding note with {model}")
    logger.info(note)
    output = requests.post(endpoints[model], json={"input": {"note": note}}).json()[
        "output"
    ]
    logger.info(output)
    return output


def handle_code_button(content: str = ""):
    st.session_state["note_content"] = content
    st.session_state["concept_lists"] = {
        concept_list_name: [
            {"concept": concept, "accepted": False} for concept in concept_list
        ]
        for concept_list_name, concept_list in code_note(content).items()
    }


st.title("Miade Automated Coding Playground")
st.header(
    "All data is sent to third-party LLM providers, who may train their models on the data and/or publish it. DO NOT include any real patient information or sensitive data of any kind."
)


@st.dialog("open")
def open_dialog():
    filename = st.selectbox(
        "Filename",
        options=[filepath.name for filepath in list(Path(data_dir).glob("doc_*.json"))],
    )
    if st.button("open", on_click=load_document, args=(filename,)):
        st.rerun()


@st.dialog("save as")
def save_dialog():
    filename = st.text_input("Filename", value=default_filename(data_dir))
    if st.button("save", on_click=save_document, args=(filename,)):
        st.write("saved")


left_column, right_column = st.columns(2)
with left_column:
    st.button("open", key="open-button", use_container_width=True, on_click=open_dialog)
with right_column:
    st.button("save", key="save-button", use_container_width=True, on_click=save_dialog)

left_column, right_column = st.columns(2)

with left_column:
    key = 0
    for concept_list_name, concept_list in st.session_state["concept_lists"].items():
        st.subheader(concept_list_name)
        for concept in concept_list:
            concept_data = concept["concept"]
            concept_col, accept_col = st.columns([3,1])
            with concept_col:
                concept_view(
                    object=concept_data,
                )
            with accept_col:
                accepted = st.checkbox(
                    "accept",
                    value=True if concept.get("accepted") else False,
                    key=key,
                )
            if not displayed_concept_list.get(concept_list_name):
                displayed_concept_list[concept_list_name] = []
            displayed_concept_list[concept_list_name].append({"concept": concept_data, "accepted": accepted})
            key = key + 1

with right_column:
    content = st_quill(value=st.session_state["note_content"])
    model = st.segmented_control(
        "Choose model:",
        [model["name"] for model in models],
        default=[model["name"] for model in models][0],
    )
    st.button("Code", on_click=handle_code_button, kwargs={"content": content})
