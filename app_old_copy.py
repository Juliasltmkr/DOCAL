
import streamlit as st
from pypdf import PdfReader
from io import BytesIO

# -------------------------
# Page configuration
# -------------------------

st.set_page_config(
    page_title="DOCAL",
    page_icon="📄",
    layout="centered"
)

# -------------------------
# Main interface
# -------------------------

st.title("📄 DOCAL")

st.subheader("Your AI-powered document assistant")

st.write(
    "Upload a document and let DOCAL help you understand it."
)

st.divider()

# -------------------------
# PDF upload
# -------------------------

uploaded_file = st.file_uploader(
    "Upload your PDF document",
    type=["pdf"]
)

# -------------------------
# PDF processing
# -------------------------

if uploaded_file is not None:

    st.success(f"{uploaded_file.name} uploaded successfully!")

    try:
        # Read the uploaded PDF
        pdf_reader = PdfReader(
            BytesIO(uploaded_file.getvalue())
        )

        # Extract text from every page
        pages_text = []

        for page_number, page in enumerate(
            pdf_reader.pages, start=1
        ):

            text = page.extract_text() or ""

            pages_text.append({
                "page": page_number,
                "text": text
            })

        # Combine extracted text
        full_text = "\n\n".join(
            page["text"] for page in pages_text
        )

        # -------------------------
        # Document information
        # -------------------------

        st.divider()
        st.subheader("Document information")

        col1, col2 = st.columns(2)

        col1.metric(
            "Total pages",
            len(pdf_reader.pages)
        )

        col2.metric(
            "Characters extracted",
            len(full_text)
        )

        # -------------------------
        # Document preview
        # -------------------------

        st.subheader("Document preview")

        if full_text.strip():

            with st.expander("View extracted text"):
                st.text(full_text[:10000])

            st.success(
                "DOCAL successfully read your document!"
            )

        else:

            st.warning(
                "No readable text was found. "
                "This PDF may contain scanned images. "
                "OCR support will be added later."
            )

    except Exception as e:

        st.error(
            f"Something went wrong while reading the PDF: {e}"
        )
