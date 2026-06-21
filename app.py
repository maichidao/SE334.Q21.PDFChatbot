import streamlit as st
from components.upload_page import show_upload_page
from components.chat_page import show_chat_page
from utils.styles import load_css

st.set_page_config(
    page_title="PDF Chatbot - Hỏi đáp thông minh",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="auto",
)

load_css()

if "page" not in st.session_state:
    st.session_state.page = "upload"

if st.session_state.page == "upload":
    show_upload_page()
else:
    show_chat_page()
