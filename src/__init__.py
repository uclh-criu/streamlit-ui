import streamlit.components.v1 as components

objectview = components.declare_component(
    "objectview",
    url="http://localhost:3001"
)

objectview(object={"test-key": "test-value", "test-two": {"subkey": "subval"}})
