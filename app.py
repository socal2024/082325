import os
import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gemini Chatbot", page_icon="💬", layout="centered")

st.title("💬 Gemini Chatbot (Streamlit)")
st.caption("A minimal chat wrapper around Google Gemini 1.5")

# --- API key loading (prefer Streamlit Secrets in Cloud; env var also works locally)
api_key = os.getenv("GEMINI_API_KEY", "")
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    st.info(
        "Set GEMINI_API_KEY in Streamlit Cloud → App settings → Secrets (or locally via .streamlit/secrets.toml)."
    )
    st.stop()

# --- Configure Gemini SDK
genai.configure(api_key=api_key)

# Sidebar controls
st.sidebar.header("⚙️ Settings")
model_name = st.sidebar.selectbox(
    "Model", ["gemini-1.5-flash", "gemini-1.5-pro"], index=0
)

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
system_instruction = st.sidebar.text_area(
    "System instruction",
    value="You are a helpful assistant. Be concise and accurate.",
    height=120,
)

# Recreate the chat session when core settings change
recreate = (
    st.session_state.get("model_name") != model_name
    or st.session_state.get("system_instruction") != system_instruction
)

# Instantiate model and chat session
model = genai.GenerativeModel(model_name, system_instruction=system_instruction)

if "chat" not in st.session_state or recreate:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    st.session_state.model_name = model_name
    st.session_state.system_instruction = system_instruction

# Render previous messages
for m in st.session_state.get("messages", []):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Chat input
prompt = st.chat_input("Ask me anything…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        try
