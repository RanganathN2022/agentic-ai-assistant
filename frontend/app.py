import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Chatbot", layout="wide")

st.title("🤖 Enterprise Agentic AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "doc_id" not in st.session_state:
    st.session_state.doc_id = None


# Upload
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    files = {"file": uploaded_file.getvalue()}
    res = requests.post(f"{API_URL}/upload/", files=files)

    if res.status_code == 200:
        st.success("Uploaded!")
        st.session_state.doc_id = uploaded_file.name


# Chat display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# Input
if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        res = requests.post(
            f"{API_URL}/chat/",
            json={
                "query": prompt,
                "session_id": "user1",
                "doc_id": st.session_state.doc_id
            }
        )

        answer = res.json().get("response", "Error")

        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})