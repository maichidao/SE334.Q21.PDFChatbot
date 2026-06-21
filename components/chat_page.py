import streamlit as st
from modules.prompt_builder import build_prompt
from modules.gemini_client import ask_gemini_stream
from modules.token_handler import get_token_stats
from urllib.parse import quote


def copy_button(text):
    encoded = quote(text, safe='')
    st.html(
        f"""
<style>
.btn-copy:hover {{ background:#f0f0f0; }}
</style>
<button class="btn-copy" onclick="(function(){{try{{var ta=document.createElement('textarea');ta.value=decodeURIComponent('{encoded}');document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);this.textContent='✅';var self=this;setTimeout(function(){{self.textContent='📋 Sao chép';}},2000);}}catch(e){{this.textContent='❌';}}}})()" style="background:none;border:1px solid #ccc;border-radius:6px;padding:2px 8px;cursor:pointer;font-size:0.8rem;color:#666;line-height:1.6;font-family:inherit;" title="Sao chép nội dung">📋 Sao chép</button>
"""
    )


def show_chat_page():
    with st.sidebar:
        if st.button("⬅ Quay lại trang upload", type="secondary", use_container_width=True, help="Quay lại trang upload để chọn file PDF khác"):
            st.session_state.page = "upload"
            st.rerun()

        st.markdown('<hr>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section"><h4>📄 PDF Chatbot</h4><p>Trò chuyện với tài liệu PDF của bạn</p></div>', unsafe_allow_html=True)

        if "uploaded_file_names" in st.session_state:
            names = st.session_state.uploaded_file_names
            file_list = "".join(f'<li>{n}</li>' for n in names)
            st.markdown(f'<div class="file-section"><h4>📁 File đã tải</h4><ul>{file_list}</ul></div>', unsafe_allow_html=True)

        st.markdown('<hr>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section"><h4>💡 Mẹo sử dụng</h4><ul><li>Đặt câu hỏi cụ thể, rõ ràng</li><li>Hỏi về nội dung trong tài liệu</li><li>Yêu cầu tóm tắt từng phần</li><li>Đặt câu hỏi tiếp nối để trao đổi sâu hơn</li></ul></div>', unsafe_allow_html=True)

        st.markdown('<hr>', unsafe_allow_html=True)

        if "pdf_text" in st.session_state:
            char_count = len(st.session_state.pdf_text)
            st.markdown(f'<div class="file-status">📊 Dung lượng: {char_count:,} ký tự</div>', unsafe_allow_html=True)

        st.markdown('<hr>', unsafe_allow_html=True)

    st.markdown('<div class="main-header"><h1>💬 PDF Chatbot</h1><p class="subtitle">Hỏi đáp thông minh dựa trên nội dung tài liệu của bạn</p></div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "pdf_text" not in st.session_state:
        st.warning("⚠️ Chưa có tài liệu PDF. Vui lòng upload file trước.")
        if st.button(" Quay lại upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    if len(st.session_state.messages) == 0:
        st.info("""💬 **Bắt đầu đặt câu hỏi về tài liệu PDF của bạn**

Nhập câu hỏi ở ô bên dưới. Ví dụ:
— *Nội dung chính của tài liệu là gì?*
— *Tóm tắt chương 2 cho tôi*
— *Liệt kê các số liệu quan trọng*""")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-user"><div class="msg-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)
            copy_button(msg["content"])

    if prompt := st.chat_input("Nhập câu hỏi về tài liệu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="msg-user"><div class="msg-bubble">{prompt}</div></div>', unsafe_allow_html=True)

        stream_place = st.empty()
        stream_place.markdown('<div class="typing-indicator"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
        try:
            full_prompt = build_prompt(
                context=st.session_state.pdf_text,
                question=prompt,
            )

            prompt_stats = get_token_stats(full_prompt)
            if not prompt_stats["is_within_limit"]:
                stream_place.empty()
                error_msg = (
                    f"❌ Prompt vượt giới hạn token!\n\n"
                    f"Token hiện tại: {prompt_stats['estimated_tokens']:,} / {prompt_stats['max_tokens_allowed']:,}\n"
                    f"Vui lòng upload file PDF khác hoặc đặt câu hỏi ngắn hơn."
                )
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
            else:
                response = ""
                for chunk in ask_gemini_stream(full_prompt):
                    response += chunk
                    stream_place.markdown(f'<div class="msg-ai">{response}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response})
                copy_button(response)
        except Exception as e:
            stream_place.empty()
            err = str(e)
            if "429" in err and "RESOURCE_EXHAUSTED" in err:
                error_msg = "❌ **Đã hết lượt sử dụng Gemini API hôm nay.**\n\nAPI miễn phí chỉ giới hạn 20 câu hỏi/ngày. Vui lòng thử lại vào ngày mai hoặc liên hệ quản trị viên để nâng cấp API key."
            else:
                error_msg = f"❌ Lỗi: {e}"
            st.error(error_msg)
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )
