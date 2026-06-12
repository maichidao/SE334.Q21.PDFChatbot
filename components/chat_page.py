import streamlit as st
from modules.prompt_builder import build_prompt
from modules.gemini_client import ask_gemini


def show_chat_page():
    st.title("PDF Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "pdf_text" not in st.session_state:
        st.warning("Chưa có tài liệu PDF. Vui lòng upload file trước.")
        if st.button(" Quay lại upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Nhập câu hỏi về tài liệu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                try:
                    full_prompt = build_prompt(
                        context=st.session_state.pdf_text,
                        question=prompt,
                    )
                    response = ask_gemini(full_prompt)
                    st.markdown(response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    error_msg = f"Lỗi: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
