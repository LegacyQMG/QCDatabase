
import streamlit as st
import zipfile
import os
import tempfile
import traceback
import time
from docling.document_converter import DocumentConverter
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

st.set_page_config(page_title="PDF GPT Assistant", layout="wide")
st.title("📄 GPT Construction Document Assistant")

all_text = ""
pdf_count = 0

uploaded_zip = st.file_uploader("📁 Upload a .zip file of your PDFs", type="zip")

if uploaded_zip:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getbuffer())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        converter = DocumentConverter()

        for root, _, files in os.walk(temp_dir):
            for filename in files:
                if filename.lower().endswith(".pdf"):
                    pdf_count += 1
                    filepath = os.path.join(root, filename)
                    try:
                        result = converter.convert(filepath)
                        doc_text = result.document.export_to_markdown()
                        all_text += f"\n\n# {filename}\n" + doc_text
                        st.markdown(f"✅ **Loaded**: `{filename}`")
                        st.text_area(f"📄 Preview of {filename}", doc_text[:500])
                    except Exception as e:
                        st.warning(f"⚠️ Failed to process {filename}: {e}")

        st.markdown(f"🔍 Found `{pdf_count}` PDFs. Total extracted characters: `{len(all_text)}`")

        if not all_text.strip():
            st.warning("⚠️ No readable text was extracted. Are your PDFs image-based (scans)?")

# --- Chatbox Section ---
question = st.text_input("💬 Ask a question about the uploaded documents:")

if question:
    if not all_text.strip():
        st.warning("⚠️ You're asking a question, but no document text is available to analyze.")

    try:
        st.info("🧠 GPT is thinking... please wait a few seconds.")
        start_time = time.time()

        llm = OpenAI(
            temperature=0.3,
            openai_api_key="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",
            timeout=60  # 1 minute timeout
        )

        prompt = PromptTemplate.from_template(
            "You are an assistant that reads construction documents. Answer the question below using the information provided.\n\n{context}\n\nQuestion: {question}"
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run({
            "context": all_text[:5000],
            "question": question
        })

        end_time = time.time()
        st.success(f"✅ Response received in {round(end_time - start_time, 2)} seconds.")
        st.markdown("### 🧠 GPT's Answer:")
        st.write(response)

    except Exception as e:
        st.error("❌ GPT Error. See details below:")
        st.text(traceback.format_exc())
