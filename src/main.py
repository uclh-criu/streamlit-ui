import os

import streamlit as st

from streamlit_quill import st_quill
from langchain_ollama import OllamaLLM
import json
import streamlit.components.v1 as components
from pathlib import Path
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-d', '--dir', default='data')
args = parser.parse_args()
data_dir = Path(args.dir)
if not data_dir.is_absolute():
    data_dir = Path.cwd() / data_dir


root_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(root_dir, "frontend/build")

# data_dir = Path.cwd() / Path("data")

st.set_page_config(layout="wide")

concept_view = components.declare_component(
    "ConceptView",
    path=build_dir
)

# concept_view = components.declare_component("ConceptView", url="http://localhost:3001")


@st.cache_resource
def model():
    # return OllamaLLM(model="mistral:latest", base_url="http://172.17.0.1:11434") # docker port
    return OllamaLLM(model="mistral:latest")


model()

if "problem_list" not in st.session_state:
    st.session_state["problem_list"] = []
if "note_content" not in st.session_state:
    st.session_state["note_content"] = ""

displayed_problem_list = []


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
                    "data": displayed_problem_list,
                },
                indent=2,
            )
        )


def load_document(filename):
    print(f"Opening: {filename}")
    with open(data_dir / Path(filename), "r") as file:
        json_content = json.load(file)
        st.session_state["problem_list"] = json_content["data"]
        st.session_state["note_content"] = json_content["text"]


@st.cache_data
def code_note(note: str):
    print("Thinking...")
    print(note)
    output = model().invoke(
        'You are a clinical coder. You are accurate and only return concepts found in the note you read. You structure your outputs as JSON, following this schema, where <CONCEPT-CODE> is the numeric SNOMED-CT code, and <PREFFERED-NAME> is the preferred name according to SNOMED: `{"problems": [{"id": <CONCEPT-CODE>, "name": <PREFFERED-NAME>}]}`. PROVIDE NO OTHER OUTPUT THAN VALID JSON. If there is no text, return an empty `{}`. Code a problem list from this clinical note with snomed-ct: '
        + note
    )
    print(output)
    return {"structured_data": json.loads(output)}


def handle_code_button(content: str = ""):
    st.session_state["note_content"] = content
    st.session_state["problem_list"] = [
        {"concept": concept, "accepted": False}
        for concept in code_note(content)["structured_data"]["problems"]
    ]


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
    st.subheader("Problems")
    key = 0
    for concept in st.session_state["problem_list"]:
        concept_data = concept["concept"]
        concept_col, accept_col = st.columns(2)
        with concept_col:
            concept_view(
                object=concept_data,
            )
        with accept_col:
            accepted = st.checkbox(
                "accept suggestion",
                value=True if concept.get("accepted") else False,
                key=key,
            )
        displayed_problem_list.append({"concept": concept_data, "accepted": accepted})
        key = key + 1

with right_column:
    content = st_quill(value=st.session_state["note_content"])
    st.button("Code", on_click=handle_code_button, kwargs={"content": content})
