import io
import streamlit as st
from modules.pdf_reader import extract_text, MAX_FILE_SIZE_MB
from modules.token_handler import get_token_stats, format_token_stats, process_pdf_content


def show_upload_page():
    st.markdown('<div class="main-header"><h1>📄 PDF Chatbot</h1><p class="subtitle">Tải lên tài liệu PDF để bắt đầu hỏi đáp thông minh với AI</p></div>', unsafe_allow_html=True)

    with st.expander("📖 Hướng dẫn sử dụng", expanded=False):
        st.markdown("""
1. **Tải file PDF** lên từ máy tính (tối đa {0} MB mỗi file)
2. Có thể tải **nhiều file** cùng lúc - nhấn nút **+** để thêm file
3. Hệ thống sẽ **trích xuất văn bản** từ tất cả file và kiểm tra dung lượng token
4. Nếu văn bản quá dài, bạn có thể **Tóm tắt** hoặc **Cắt ngắn**
5. Nhấn **"Bắt đầu hỏi đáp"** để sang trang chat và đặt câu hỏi về nội dung tài liệu

> 💡 **Mẹo:** File càng ít trang, tốc độ xử lý và chất lượng trả lời càng cao.
""".format(MAX_FILE_SIZE_MB))

    uploaded_files = st.file_uploader(
        f"Chọn file PDF (tối đa {MAX_FILE_SIZE_MB} MB mỗi file)",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        combined_text = ""
        total_pages = 0
        total_extracted = 0
        file_names = []
        errors = []

        for uploaded_file in uploaded_files:
            size_bytes = getattr(uploaded_file, "size", None)
            file_stream = uploaded_file

            if size_bytes is None:
                data = uploaded_file.read()
                size_bytes = len(data)
                file_stream = io.BytesIO(data)

            size_mb = size_bytes / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                errors.append(f"❌ {uploaded_file.name}: File quá lớn ({size_mb:.1f} MB) - Giới hạn {MAX_FILE_SIZE_MB} MB")
                continue

            file_names.append(uploaded_file.name)

            with st.spinner(f"📖 Đang đọc {uploaded_file.name}..."):
                result = extract_text(file_stream)

            if result.success:
                combined_text += f"\n\n=== {uploaded_file.name} ===\n\n{result.text}"
                total_pages += result.total_pages
                total_extracted += result.extracted_pages
            else:
                errors.append(f"❌ {uploaded_file.name}: {result.error}")

        if not combined_text and not errors:
            st.warning("⚠️ Không có file nào được tải lên thành công.")
            return

        if combined_text:
            file_list = ", ".join(file_names)
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown(f"**📋 Thông tin tài liệu**")
            st.markdown(f"- 📁 File: **{file_list}**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"- 📄 Tổng số trang: **{total_pages}**")
            with col2:
                st.markdown(f"- ✅ Đọc được: **{total_extracted}** trang")
            st.markdown('</div>', unsafe_allow_html=True)

            stats = get_token_stats(combined_text)

            if not stats["is_within_limit"]:
                st.markdown('<div class="warning-box">Nội dung vượt giới hạn token, vui lòng xử lý bên dưới.</div>', unsafe_allow_html=True)

                with st.expander("📊 Chi tiết token", expanded=True):
                    st.code(format_token_stats(stats), language="")

                col1, col2, col3 = st.columns(3)
                with col1:
                    btn_summarize = st.button("📝 Tóm tắt", use_container_width=True)
                with col2:
                    btn_truncate = st.button("✂️ Cắt ngắn", use_container_width=True)
                with col3:
                    btn_cancel = st.button("🗑️ Hủy", use_container_width=True)

                if btn_cancel:
                    st.info("Đã hủy.")
                    return

                if btn_summarize or btn_truncate:
                    prefer_summarize = btn_summarize
                    with st.spinner("⏳ Đang xử lý..."):
                        proc = process_pdf_content(combined_text, prefer_summarize=prefer_summarize)

                    with st.expander("📝 Log xử lý"):
                        for msg in proc.messages:
                            st.info(msg)

                    st.session_state.pdf_text = proc.processed_text
                    st.success(f"✅ Xử lý xong ({proc.processing_method})")
            else:
                st.markdown('<div class="tip-box">Văn bản trong giới hạn token, sẵn sàng sử dụng!</div>', unsafe_allow_html=True)
                st.session_state.pdf_text = combined_text

            st.session_state.uploaded_file_names = file_names
            st.session_state.messages = []
            if st.button("🚀 Bắt đầu hỏi đáp", type="primary", use_container_width=True):
                st.session_state.page = "chat"
                st.rerun()

        for err in errors:
            st.error(err)
