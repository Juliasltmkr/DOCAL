
import streamlit as st
import ollama
from pypdf import PdfReader
from io import BytesIO
import hashlib


st.title("📄 DOCAL")
st.subheader("Your AI-powered document assistant")
st.write("Upload a PDF and let DOCAL help you understand it.")


# SESSION MEMORY

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

if "document_hash" not in st.session_state:
    st.session_state.document_hash = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = ""


# PDF UPLOAD AND EXTRACTION

uploaded_file = st.file_uploader(
    "Upload your PDF document",
    type=["pdf"]
)

if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()
    current_hash = hashlib.sha256(file_bytes).hexdigest()

    if current_hash != st.session_state.document_hash:

        try:
            pdf_reader = PdfReader(BytesIO(file_bytes))

            pages_text = []

            for page in pdf_reader.pages:
                pages_text.append(page.extract_text() or "")

            full_text = "\n\n".join(pages_text)

            st.session_state.document_text = full_text[:15000]
            st.session_state.document_hash = current_hash
            st.session_state.messages = []
            st.session_state.summary = ""

            st.success("PDF successfully uploaded!")

        except Exception as e:
            st.error(f"Could not read the PDF: {e}")


    # DOCUMENT INFORMATION


    st.divider()
    st.subheader("Document information")

    col1, col2 = st.columns(2)

    col1.metric(
        "Total pages",
        len(PdfReader(BytesIO(file_bytes)).pages)
    )

    col2.metric(
        "Characters extracted",
        len(st.session_state.document_text)
    )

    if len(st.session_state.document_text) >= 15000:
        st.warning(
            "DOCAL currently uses a maximum of "
            "15,000 characters from the document."
        )

    if not st.session_state.document_text.strip():
        st.warning(
            "No readable text was found. "
            "This PDF may contain scanned images."
        )


    # AI SUMMARISATION


    st.divider()
    st.subheader("Document summary")

    if st.button("Summarise my document"):

        if not st.session_state.document_text.strip():
            st.warning("There is no readable text to summarise.")

        else:
            with st.spinner("DOCAL is analysing your document..."):

                try:
                    response = ollama.chat(
                        model="llama3.2:3b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are DOCAL, a professional document "
                                    "analysis assistant. Create accurate, "
                                    "well-structured summaries. Only use "
                                    "information from the supplied document."
                                )
                            },
                            {
                                "role": "user",
                                "content": (
                                    "Summarise this document. Include its "
                                    "main arguments, important information "
                                    "and conclusions:\n\n"
                                    + st.session_state.document_text
                                )
                            }
                        ]
                    )

                    st.session_state.summary = (
                        response["message"]["content"]
                    )

                except Exception as e:
                    st.error(f"AI error: {e}")

    if st.session_state.summary:
        st.markdown(st.session_state.summary)


    # CHAT WITH YOUR DOCUMENT

    st.divider()
    st.subheader("💬 Chat with your document")

    st.write(
        "Ask DOCAL anything about the information "
        "in your uploaded PDF."
    )

    # Display previous messages

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Question input

    user_question = st.text_input(
        "Your question:",
        placeholder="What is this document about?",
        key="document_question"
    )

    send_question = st.button(
        "Send question",
        key="send_document_question"
    )

    # Process question

    if send_question and user_question.strip():

        if not st.session_state.document_text.strip():
            st.warning("Your PDF contains no readable text.")

        else:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_question
                }
            )

            with st.chat_message("user"):
                st.markdown(user_question)

            system_prompt = """
            You are DOCAL, a professional document analysis assistant.

            Answer questions using the supplied document.
            Be clear, accurate and helpful.
            Do not invent information.
            If the answer is not in the document, say so.
            """

            messages = [
                {
                    "role": "system",
                    "content": (
                        system_prompt
                        + "\n\nDOCUMENT CONTENT:\n"
                        + st.session_state.document_text
                    )
                }
            ]

            messages.extend(st.session_state.messages)

            with st.chat_message("assistant"):

                with st.spinner("DOCAL is thinking..."):

                    try:
                        response = ollama.chat(
                            model="llama3.2:3b",
                            messages=messages
                        )

                        answer = response["message"]["content"]

                        st.markdown(answer)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer
                            }
                        )

                        st.rerun()

                    except Exception as e:
                        st.error(f"AI error: {e}")

else:
    st.info("Upload a PDF to get started with DOCAL.")
