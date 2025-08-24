import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import dropbox
from io import BytesIO

# Setup Dropbox client using secrets
dbx = dropbox.Dropbox(st.secrets["DROPBOX_ACCESS_TOKEN"])
dropbox_folder = st.secrets["DROPBOX_PDF_FOLDER"]  # e.g., "/guidelines"

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
user_pdf_text = ""

if uploaded_file:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            user_pdf_text += page.get_text()
    st.markdown("✅ PDF content successfully extracted and will be included in your prompt.")

# Load guidelines and context from Dropbox folder
dropbox_pdf_text = load_dropbox_pdf_texts(dropbox_folder)

# Construct system prompt
system_prompt = (
    "You are an expert real estate investor. Use the following context documents to guide every response.\n\n"
    "=== Dropbox PDFs (guidelines, policies, references) ===\n"
    f"{dropbox_pdf_text}\n\n"
)

# Append user-uploaded PDF if present
if user_pdf_text:
    system_prompt += (
        "=== Uploaded PDF (deal-specific) ===\n"
        f"{user_pdf_text}\n\n"
    )

system_prompt += "Now, answer user questions using all the above as background. Be precise, professional, and thorough."

# 🔹 Initialize Gemini chat
if "chat" not in st.session_state:
    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system_prompt)
    st.session_state.chat = model.start_chat()

# 🔹 Text input
user_input = st.text_input("Ask your real estate question:")

if user_input:
    response = st.session_state.chat.send_message(user_input)
    st.markdown(f"**You:** {user_input}")
    st.markdown(f"**Gemini:** {response.text}")
