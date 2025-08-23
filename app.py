import streamlit as st
import google.generativeai as genai

# Load Gemini API key from secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize chat
if "chat" not in st.session_state:
    st.session_state.chat = genai.GenerativeModel("gemini-pro").start_chat()

st.title("💬 Gemini Chatbot")

user_input = st.text_input("Ask me anything:")

if user_input:
    response = st.session_state.chat.send_message(user_input)
    st.markdown(f"**You:** {user_input}")
    st.markdown(f"**Gemini:** {response.text}")
