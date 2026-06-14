import io
import streamlit as st
from modules.pdf_reader import extract_text, MAX_FILE_SIZE_MB
from modules.token_handler import get_token_stats, format_token_stats, process_pdf_content


def show_upload_page():
    st.title("Upload PDF")

    uploaded_file = st.file_uploader(
        f"Chọn file PDF (tối đa {MAX_FILE_SIZE_MB} MB)",
        type="pdf",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Kiểm tra kích thước
        size_bytes = getattr(uploaded_file, "size", None)
        file_stream = uploaded_file

        if size_bytes is None:
            data = uploaded_file.read()
            size_bytes = len(data)
            file_stream = io.BytesIO(data)

        size_mb = size_bytes / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File quá lớn: {size_mb:.1f} MB (Giới hạn: {MAX_FILE_SIZE_MB} MB)")
            return

        # Đọc PDF
        with st.spinner("Đang đọc PDF..."):
            result = extract_text(file_stream)

        if result.success:
            # Hiển thị thông tin PDF
            st.markdown("**Thông tin tài liệu**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"- Trang: **{result.total_pages}**")
            with col2:
                st.write(f"- Đọc được: **{result.extracted_pages}**")

            # Kiểm tra token
            stats = get_token_stats(result.text)
            
            if not stats["is_within_limit"]:
                st.warning("Nội dung vượt giới hạn token, vui lòng xử lý.")
                
                with st.expander("Chi tiết token"):
                    st.code(format_token_stats(stats), language="")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    btn_summarize = st.button("Tóm tắt", use_container_width=True)
                with col2:
                    btn_truncate = st.button("Cắt ngắn", use_container_width=True)
                with col3:
                    btn_cancel = st.button("Hủy", use_container_width=True)
                
                if btn_cancel:
                    st.info("Đã hủy.")
                    return
                
                if btn_summarize or btn_truncate:
                    prefer_summarize = btn_summarize
                    with st.spinner("Đang xử lý..."):
                        proc = process_pdf_content(result.text, prefer_summarize=prefer_summarize)
                    
                    with st.expander("Log xử lý"):
                        for msg in proc.messages:
                            st.info(msg)
                    
                    st.session_state.pdf_text = proc.processed_text
                    st.success(f"Xử lý xong ({proc.processing_method})")
            else:
                st.success("Sẵn sàng sử dụng")
                st.session_state.pdf_text = result.text
            
            # Button chuyển sang chat
            st.session_state.messages = []
            if st.button("Bắt đầu hỏi đáp", type="primary", use_container_width=True):
                st.session_state.page = "chat"
                st.rerun()
        else:
            st.error(f"Lỗi: {result.error}")
