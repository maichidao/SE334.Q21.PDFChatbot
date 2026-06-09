import streamlit as st
import PyPDF2

def show_upload_page():
    st.title("Upload tài liệu PDF")
    
    uploaded_file = st.file_uploader("Chọn file PDF", type="pdf")
    
    if uploaded_file is not None:
        # Hiển thị tên file
        st.write(f"**Tên file:** {uploaded_file.name}")
        
        # Đọc số trang
        reader = PyPDF2.PdfReader(uploaded_file)
        st.write(f"**Số trang:** {len(reader.pages)}")
        
        st.success("Upload thành công!")

show_upload_page()