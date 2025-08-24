import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import dropbox
from io import BytesIO
import sys

def _dbg(label, value):
    print(f"{label}: {repr(value)} (len={0 if value is None else len(str(value))})",
          file=sys.stderr, flush=True)

# Setup Dropbox client using secrets
dbx = dropbox.Dropbox(st.secrets["DROPBOX_ACCESS_TOKEN"])
dropbox_folder = st.secrets["DROPBOX_PDF_FOLDER"]

# Load Gemini API key from secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Upload files into chatbot memory
@st.cache_data
def load_dropbox_pdf_texts(folder_path):
    """Load and combine all PDF texts from a Dropbox folder."""
    combined_text = ""
    res = dbx.files_list_folder(folder_path)
    for entry in res.entries:
        if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith(".pdf"):
            _, response = dbx.files_download(entry.path_lower)
            with fitz.open(stream=BytesIO(response.content), filetype="pdf") as doc:
                for page in doc:
                    combined_text += page.get_text()
                combined_text += "\n\n"
    return combined_text.strip()

st.title("🏘️ Real Estate Investor Chatbot")

# 🔹🔹 NEW: File uploader for PDF
uploaded_file = st.file_uploader("Upload a PDF (e.g., property documents, investment memo):", type=["pdf"])

if uploaded_file:
    text_chunks = []
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text_chunks.append(page.get_text())
    # Save in session so it survives reruns
    st.session_state.uploaded_pdf_text = "\n".join(text_chunks)
    st.markdown("✅ PDF content successfully extracted and will be included in your prompt.")

# Always read from session (empty if none)
user_pdf_text = st.session_state.get("uploaded_pdf_text", "")

# Load guidelines and context from Dropbox folder
dropbox_pdf_text = load_dropbox_pdf_texts(dropbox_folder)

# Construct system prompt
system_prompt = (
    "You are an expert real estate investor advising other investors. Use the following context documents as background knowledge. Use them only as background knowledge, do not directly refer to their contents unless asked to. \n\n"
    "=== Dropbox PDFs (guidelines, policies, references) ===\n"
    f"{dropbox_pdf_text}\n\n"
)

# Append user-uploaded PDF if present
if user_pdf_text:
    system_prompt += (
        "=== Uploaded PDF (deal-specific) ===\n"
        f"{user_pdf_text}\n\n"
    )

system_prompt += (
    "Now, answer user questions using all the above as background. Be precise, professional, and thorough. "
    "You do not need to reference the initially loaded PDFs unless the user asks.  If the user uploads a new PDF, focus on that. "
    "Act as an expert real estate investor. You are serving experienced real estate investors with questions. "
    "They invest in commercial real estate including multifamily and industrial properties. "
    "They also invest as limited partners in multifamily and real estate syndications. "
    "Act as an experienced investors providing honest and helpful feedback that's helpful for investors. "
    "Use a critical eye when reviewing materials from GPs, brokers, and sellers, taking the investor or LP's side and point of view."
)

# 🔹 Text input
user_input = st.text_input("Ask your real estate question:")

if user_input:
    base_system_prompt = (
        "You are an expert real estate investor advising other investors. "
        "Use the following context documents as background knowledge. "
        "Use them only as background knowledge; do not directly quote unless asked.\n\n"
        "=== Dropbox PDFs (guidelines, policies, references) ===\n"
        f"{dropbox_pdf_text}\n\n"
        "Now, answer user questions using all the above as background. "
        "If the user uploads a new PDF, focus on that for deal-specific analysis. "
        "Be candid, critical, and helpful for experienced investors."
    )

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=base_system_prompt
    )

    parts = []
    if uploaded_pdf_text:
        parts.extend([
            "Use this uploaded, deal-specific PDF text as additional context:",
            uploaded_pdf_text
        ])
    parts.append(f"Question:\n{user_input}")

    response = model.generate_content(parts)
    st.markdown(f"**You:** {user_input}")
    st.markdown(f"**Gemini:** {response.text}")
