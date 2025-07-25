# ===========================
# 📦 Imports
# ===========================
import streamlit as st
import zipfile
import os
import tempfile
import traceback
import hashlib
from docling.document_converter import DocumentConverter
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


# ===========================
# 🧠 Streamlit App Title
# ===========================
st.set_page_config(page_title="Ask GPT About PDFs", layout="wide")
st.title("📂 Ask GPT About Your Folder of PDFs")


# ===========================
# 🔧 Helper Functions
# ===========================
@st.cache_data(show_spinner="🔍 Extracting text...")
def extract_text_from_pdf(filepath):
    converter = DocumentConverter()
    result = converter.convert(filepath)
    return result.document.export_to_markdown()


def file_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


# ===========================
# 📁 File Upload Section
# ===========================
uploaded_zip = st.file_uploader("Upload a .zip file of your PDFs (can include subfolders)", type="zip")


# ===========================
# 📂 ZIP Extraction & Processing
# ===========================
if uploaded_zip:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getbuffer())

        # Unzip into temp directory
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # 🧠 Text Extraction
        all_text = ""
        for root, _, files in os.walk(temp_dir):
            for filename in files:
                if filename.lower().endswith(".pdf"):
                    filepath = os.path.join(root, filename)
                    try:
                        key = file_hash(filepath)
                        doc_text = extract_text_from_pdf(filepath)
                        all_text += f"\n\n# {filename}\n" + doc_text
                        st.markdown(f"✅ Processed: `{filename}`")
                        st.text_area(f"Preview of {filename}", doc_text[:500], height=150)
                    except Exception as e:
                        st.warning(f"❌ Failed to process {filename}: {e}")

        # 🔔 Notify if nothing extracted
        if not all_text.strip():
            st.warning("⚠️ No text was extracted. PDFs may contain scanned images only.")

        # ===========================
        # 💬 Question + LLM Section
        # ===========================
        question = st.text_input("Ask a question about the uploaded documents:")

        if question and all_text.strip():
            try:
                llm = OpenAI(
                    temperature=0.3,
                    openai_api_key="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"
                )

                prompt = PromptTemplate.from_template(
                    "You are an assistant that reads construction documents. Answer the question below using the information provided.\n\n{context}\n\nQuestion: {question}"
                )

                chain = LLMChain(llm=llm, prompt=prompt)
                st.info("🤖 GPT is thinking...")
                response = chain.run({
                    "context": all_text[:5000],  # Truncated for GPT input size
                    "question": question
                })

                st.markdown("### 🧠 GPT's Answer:")
                st.write(response)

            except Exception as e:
                st.error("❌ GPT Error. See details below:")
                st.text(traceback.format_exc())


# ===========================
# 🪪 Notes for Developer
# ===========================
# 🔧 To revise or add features:
# - Add UI elements in the "Streamlit App Title" or "File Upload" sections
# - Add logic under "Helper Functions" or create new utility sections
# - Add new processing steps inside the "ZIP Extraction & Processing" block
# - Integrate other LLM chains or tools inside the "LLM Section"

# ✅ Tip: Replace 'YOUR-KEY-HERE' with your actual OpenAI key safely via secrets or env vars
