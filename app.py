import streamlit as st
from pages.upload_page import show_upload_page
from pages.chat_page import show_chat_page

if "page" not in st.session_state:
    st.session_state.page = "upload"

if st.session_state.page == "upload":
    show_upload_page()
else:
    show_chat_page()
