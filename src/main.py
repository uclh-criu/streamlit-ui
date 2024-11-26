import os

import streamlit as st

from streamlit_ace import st_ace
from langchain_ollama import OllamaLLM
import json
import streamlit.components.v1 as components
from pathlib import Path
import re
from tkinter.constants import S


st.set_page_config(layout="wide")

root_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(root_dir, "frontend/build")

data_dir = Path.cwd() / Path("data")


# concept_view = components.declare_component(
#     "ConceptView",
#     path=build_dir
# )

concept_view = components.declare_component(
    "ConceptView",
    url="http://localhost:3001"
)


@st.cache_resource
def load_model():
    # return OllamaLLM(model="mistral:latest", base_url="http://172.17.0.1:11434") # docker port
    return OllamaLLM(model="mistral:latest")


lm = load_model()


@st.cache_data
def code_note(note: str):
    print("Thinking...")
    output = lm.invoke(
        'You are a clinical coder. You are accurate and only return concepts found in the note you read. You structure your outputs as JSON, following this schema, where <CONCEPT-CODE> is the numeric SNOMED-CT code, and <PREFFERED-NAME> is the preferred name according to SNOMED: `{"problems": [{"id": <CONCEPT-CODE>, "name": <PREFFERED-NAME>}]}`. PROVIDE NO OTHER OUTPUT THAN VALID JSON. If there is no text, return an empty `{}`. Code a problem list from this clinical note with snomed-ct: ' + note
        )
    print(output)
    return {"structured_data": json.loads(output)}



left_column, right_column = st.columns(2)

with right_column:
    content = st_ace()

with left_column:
    # st.write(code_note(content))
    st.subheader("Problems")

    problem_list = []
    for concept in code_note(content)["structured_data"]["problems"]:
        val = concept_view(object=concept)
        problem_list.append({"concept": concept, "accepted": val})

doc = {"text": content, "data": problem_list}


def default_filename(dir="data"):
    n = 0
    filenames_in_pattern = list(Path(dir).glob("doc_*.json"))
    if filenames_in_pattern:
        n = max(
            [
                int(s.stem.split('_')[1])
                for s
                in filenames_in_pattern
            ]
    ) + 1
    return f"doc_{n}.json"

def save_doc(filename):
    with open(data_dir / Path(filename), 'w') as file:
        file.write(json.dumps(doc, indent=2))

with st.form("Save"):
    filename = st.text_input("Filename", value=default_filename())
    submitted = st.form_submit_button("save", on_click=save_doc, kwargs={"filename": filename})
    if submitted:
        st.write("saved")

st.download_button("download", json.dumps(doc, indent=2), file_name="note.json")
