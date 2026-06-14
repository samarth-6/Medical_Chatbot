import os,uuid
import requests
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="Medical Multi-Agent Chatbot",
    page_icon="🩺",
    layout="wide"
)

if "session_id" not in st.session_state:

    st.session_state.session_id = str(
        uuid.uuid4()
    )


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

- PubMed
- MedlinePlus
- WebMD

Supports document-based RAG.
"""
)

with st.sidebar:

    st.header("Configuration")

    mode = st.radio(
        "Select Mode",
        [
            "web",
            "rag"
        ]
    )

    st.markdown("---")

    st.subheader("Session")

    st.code(
        st.session_state.session_id
    )

    st.markdown("---")

    uploaded_files = st.file_uploader(
    "Upload Documents",
    type=[
        "pdf",
        "txt",
        "md"
    ],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
    )

    st.markdown("---")

    st.subheader(
        "Uploaded Documents"
    )

    try:

        docs = requests.get(
            f"{API_URL}/documents/{st.session_state.session_id}"
        ).json()

        for doc in docs:

            col1, col2 = st.columns(
                [4, 1]
            )

            with col1:

                st.write(
                    doc["filename"]
                )

            with col2:

                if st.button(
                    "Delete",
                    key=doc["filename"]
                ):

                    requests.delete(
                        f"{API_URL}/documents/"
                        f"{st.session_state.session_id}/"
                        f"{doc['filename']}"
                    )

                    st.session_state.uploaded_files_cache.discard(
                        doc["filename"]
                    )

                    st.rerun()

    except Exception:

        pass


if (
    mode == "rag"
    and uploaded_files
):

    new_files = [
        file
        for file in uploaded_files
        if file.name
        not in st.session_state.uploaded_files_cache
    ]

    if new_files:

        try:

            with st.spinner(
                "Uploading and indexing..."
            ):

                files = []

                for file in new_files:

                    files.append(
                        (
                            "files",
                            (
                                file.name,
                                file,
                                file.type
                            )
                        )
                    )

                response = requests.post(
                    f"{API_URL}/upload",
                    data={
                        "session_id":
                        st.session_state.session_id
                    },
                    files=files,
                    timeout=300
                )

                response.raise_for_status()

                for file in new_files:

                    st.session_state.uploaded_files_cache.add(
                        file.name
                    )

                st.success( f"{len(new_files)} document(s) uploaded.")

                st.session_state.uploader_key += 1

                st.rerun()

        except Exception as e:

            st.error(
                f"Upload failed: {e}"
            )

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

prompt = st.chat_input(
    "Ask a medical question..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    try:

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Thinking..."
            ):

                response = requests.post(
                    f"{API_URL}/chat",
                    data={
                        "query": prompt,
                        "mode": mode,
                        "session_id":
                        st.session_state.session_id
                    },
                    timeout=300
                )

                response.raise_for_status()

                result = response.json()

                answer = result.get(
                    "answer",
                    ""
                )

                sources = result.get(
                    "sources",
                    []
                )

                st.markdown(answer)

                if sources:

                    st.markdown("---")
                    st.subheader(
                        "Sources"
                    )

                    if (
                        isinstance(
                            sources[0],
                            dict
                        )
                    ):

                        for source in sources:

                            title = source.get(
                                "title",
                                "Source"
                            )

                            url = source.get(
                                "url",
                                ""
                            )

                            st.markdown(
                                f"- [{title}]({url})"
                            )

                    else:

                        for source in sources:

                            st.markdown(
                                f"- {source}"
                            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except requests.exceptions.Timeout:

        st.error(
            "Request timed out."
        )

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to API_URL."
        )

    except Exception as e:

        st.error(str(e))