import os
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="Medical Multi-Agent Chatbot",
    page_icon="🩺",
    layout="wide",
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "uploaded_files_cache" not in st.session_state:
    st.session_state.uploaded_files_cache = set()

st.title("🩺 Medical Multi-Agent Chatbot")
st.markdown(
    """
Answers only medical questions.

Sources:
- PubMed · MedlinePlus · WebMD · Mayo Clinic · Healthline
- NIH · WHO · CDC · Cleveland Clinic · Johns Hopkins Medicine

Supports document-based RAG.
"""
)

with st.sidebar:
    st.header("Configuration")
    mode = st.radio("Select Mode", ["web", "rag"])

    st.markdown("---")
    st.subheader("Session")
    st.code(st.session_state.session_id)

    st.markdown("---")
    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
    )

    st.markdown("---")
    st.subheader("Uploaded Documents")
    try:
        docs = requests.get(
            f"{API_URL}/documents/{st.session_state.session_id}"
        ).json()
        for doc in docs:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(doc["filename"])
            with col2:
                if st.button("Delete", key=doc["filename"]):
                    requests.delete(
                        f"{API_URL}/documents/"
                        f"{st.session_state.session_id}/"
                        f"{doc['filename']}"
                    )
                    st.session_state.uploaded_files_cache.discard(doc["filename"])
                    st.rerun()
    except Exception:
        pass

if uploaded_files:
    new_files = [
        f for f in uploaded_files
        if f.name not in st.session_state.uploaded_files_cache
    ]
    if new_files:
        try:
            with st.spinner("Uploading and indexing documents..."):
                files_payload = [
                    ("files", (f.name, f, f.type)) for f in new_files
                ]
                response = requests.post(
                    f"{API_URL}/upload",
                    data={"session_id": st.session_state.session_id},
                    files=files_payload,
                    timeout=300,
                )
                response.raise_for_status()
                result = response.json()

                # Track successfully uploaded files
                uploaded_names = result.get("uploaded", [])
                for name in uploaded_names:
                    # Strip the "(already exists)" suffix if present
                    clean_name = name.replace(" (already exists)", "").strip()
                    st.session_state.uploaded_files_cache.add(clean_name)

                errors = result.get("errors", [])
                if errors:
                    st.warning(f"Some files failed: {', '.join(errors)}")
                else:
                    st.success(f"{len(uploaded_names)} document(s) uploaded and indexed.")

                st.session_state.uploader_key += 1
                st.rerun()
        except Exception as e:
            st.error(f"Upload failed: {e}")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            _sources = message["sources"]
            st.markdown("---")
            st.subheader("Sources")
            if _sources and isinstance(_sources[0], dict):
                for source in _sources:
                    title = source.get("title", "Source")
                    url = source.get("url", "")
                    if url:
                        st.markdown(f"- [{title}]({url})")
                    else:
                        st.markdown(f"- {title}")
            else:
                for source in _sources:
                    st.markdown(f"- {source}")

prompt = st.chat_input("Ask a medical question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    answer = ""
    sources = []

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{API_URL}/chat",
                    data={
                        "query": prompt,
                        "mode": mode,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=300,
                )
                response.raise_for_status()
                result = response.json()

            raw_answer = result.get("answer", "")
            sources = result.get("sources", [])

            if debug_mode:
                st.caption(f"Raw answer length: {len(raw_answer)}")
                st.code(repr(raw_answer))

            answer = raw_answer.strip()

            st.markdown(answer)

            if sources:
                st.markdown("---")
                st.subheader("Sources")
                if isinstance(sources[0], dict):
                    for source in sources:
                        title = source.get("title", "Source")
                        url = source.get("url", "")
                        if url:
                            st.markdown(f"- [{title}]({url})")
                        else:
                            st.markdown(f"- {title}")
                else:
                    for source in sources:
                        st.markdown(f"- {source}")

    except requests.exceptions.Timeout:
        answer = "⚠️ Request timed out. Please try again."
        with st.chat_message("assistant"):
            st.error(answer)
    except requests.exceptions.ConnectionError:
        answer = "⚠️ Cannot connect to the backend API."
        with st.chat_message("assistant"):
            st.error(answer)
    except Exception as e:
        answer = f"⚠️ Error: {str(e)}"
        with st.chat_message("assistant"):
            st.error(answer)

    if answer:
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )