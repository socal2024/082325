import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF

# Load Gemini API key from secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Define system prompt
system_prompt = (
    "You are an expert real estate investor with decades of experience in both residential "
    "and commercial markets across different geographies. You provide detailed, data-driven, "
    "and strategic advice on topics such as property valuation, market trends, deal structuring, "
    "real estate finance, portfolio diversification, negotiation tactics, and risk management. "
    "You answer with authority, clarity, and precision, tailored to users who are serious about "
    "real estate investing."
)

# Initialize chat with system prompt
if "chat" not in st.session_state:
    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system_prompt)
    st.session_state.chat = model.start_chat()

st.title("🏘️ Real Estate Investor Chatbot")

# 🔹🔹 NEW: File uploader for PDF
uploaded_file = st.file_uploader("Upload a PDF (e.g., property documents, investment memo):", type=["pdf"])
pdf_text = ""

if uploaded_file:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            pdf_text += page.get_text()
    st.markdown("✅ PDF content successfully extracted and will be included in your prompt.")

# Ask user for a real estate question
user_input = st.text_input("Ask your real estate question:")

# 🔹🔹 CHANGED: Combine user input with PDF content
if user_input:
    combined_prompt = user_input
    if pdf_text:
        combined_prompt = (
            "Here is a PDF document relevant to this question:\n\n"
            + pdf_text
            + "\n\nNow, based on that document, answer the following:\n"
            + user_input
        )

    response = st.session_state.chat.send_message(combined_prompt)
    st.markdown(f"**You:** {user_input}")
    st.markdown(f"**Gemini:** {response.text}")
