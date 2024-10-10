import os

import streamlit as st

from streamlit_ace import st_ace
from langchain_ollama import OllamaLLM
import json

import streamlit.components.v1 as components

root_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(root_dir, "frontend/build")

concept_view = components.declare_component(
    "ConceptView",
    path=build_dir
)

# concept_view = components.declare_component(
#     "ConceptView",
#     url="http://localhost:3001"
# )



# lm = OllamaLLM(model="mistral:latest", base_url="http://172.17.0.1:11434") # docker port
lm = OllamaLLM(model="mistral:latest")

def code_note(note: str):
    print("Thinking...")
    output = lm.invoke(
        'You are a clinical coder. You are accurate and only return concepts found in the note you read. You structure your outputs as JSON, following this schema, where <CONCEPT-CODE> is the numeric SNOMED-CT code, and <PREFFERED-NAME> is the preferred name according to SNOMED: `{"problems": [{"id": <CONCEPT-CODE>, "name": <PREFFERED-NAME>}]}`. PROVIDE NO OTHER OUTPUT THAN VALID JSON. If there is no text, return an empty `{}`. Code a problem list from this clinical note with snomed-ct: ' + note
        )
    print(output)
    return {"structured_data": json.loads(output)}

st.set_page_config(layout="wide")

left_column, right_column = st.columns(2)

with right_column:
    st.header("Note")
    content = st_ace()

with left_column:
    st.header("Suggested Data")
    # st.write(code_note(content))
    st.subheader("Problems")
    for concept in code_note(content)["structured_data"]["problems"]:
        concept_view(object=concept)
