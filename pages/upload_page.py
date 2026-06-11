import streamlit as st
from modules.pdf_reader import extract_text


def show_upload_page():
    st.title("Upload tài liệu PDF")

    uploaded_file = st.file_uploader("Chọn file PDF", type="pdf")

    if uploaded_file is not None:
        st.write(f"**Tên file:** {uploaded_file.name}")

        with st.spinner("Đang đọc file PDF..."):
            result = extract_text(uploaded_file)

        if result.success:
            st.write(f"**Số trang:** {result.total_pages}")
            st.write(f"**Trang đọc được:** {result.extracted_pages}")
            if result.skipped_pages:
                st.info(f"Trang bỏ qua (ít nội dung): {result.skipped_pages}")
            st.success("Upload thành công!")

            st.session_state.pdf_text = result.text
            st.session_state.messages = []

            if st.button(" Bắt đầu hỏi đáp", type="primary"):
                st.session_state.page = "chat"
                st.rerun()
        else:
            st.error(result.error)
