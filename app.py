import streamlit as st
import google.generativeai as genai

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

st.title("💬 Gemini Chatbot")

user_input = st.text_input("Ask me anything:")

if user_input:
    response = st.session_state.chat.send_message(user_input)
    st.markdown(f"**You:** {user_input}")
    st.markdown(f"**Gemini:** {response.text}")
