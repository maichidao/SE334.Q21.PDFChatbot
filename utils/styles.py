import streamlit as st


def load_css():
    st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .main-header .subtitle {
        font-size: 0.95rem;
        color: #888;
        margin-top: 0;
    }
    .instruction-box {
        background: #f0f2f6;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #4CAF50;
    }
    .instruction-box h4 {
        margin: 0 0 0.5rem 0;
        color: #333;
        font-size: 1rem;
    }
    .instruction-box ol, .instruction-box ul {
        margin: 0.25rem 0;
        padding-left: 1.2rem;
        font-size: 0.9rem;
        color: #444;
    }
    .instruction-box li {
        margin: 0.2rem 0;
    }
    .info-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    .tip-box {
        background: #e8f5e9;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.85rem;
        color: #2e7d32;
        margin-bottom: 1rem;
        border-left: 3px solid #4CAF50;
    }
    .tip-box::before {
        content: "💡 ";
        font-weight: 600;
    }
    .warning-box {
        background: #fff3e0;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.85rem;
        color: #e65100;
        margin-bottom: 1rem;
        border-left: 3px solid #FF9800;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
    .stChat {
        border-radius: 10px;
    }

    .msg-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 10px;
        padding: 0 0.5rem;
    }
    .msg-user .msg-bubble {
        max-width: 75%;
        padding: 8px 14px;
        border-radius: 18px 18px 4px 18px;
        line-height: 1.45;
        word-wrap: break-word;
        font-size: 0.95rem;
        background: #0084ff;
        color: #fff;
    }
    .msg-ai {
        text-align: justify;
        margin: 12px 0;
        padding: 0 0.5rem;
        line-height: 1.6;
        font-size: 0.95rem;
        color: #050505;
    }
    .msg-actions {
        display: flex;
        justify-content: flex-start;
        gap: 6px;
        margin: 2px 0 10px 0;
    }
    .msg-actions .msg-action-btn {
        background: none;
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.8rem;
        cursor: pointer;
        color: #666;
        line-height: 1.6;
    }
    .msg-actions .msg-action-btn:hover {
        background: #f0f0f0;
        border-color: #999;
    }

    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 8px 14px;
        margin: 12px 0;
    }
    .typing-indicator span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #888;
        display: inline-block;
        animation: typing-bounce 1.4s infinite ease-in-out both;
    }
    .typing-indicator span:nth-child(1) { animation-delay: 0s; }
    .typing-indicator span:nth-child(2) { animation-delay: 0.16s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.32s; }
    @keyframes typing-bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }


    .chat-header-info {
        text-align: center;
        font-size: 0.85rem;
        color: #666;
        padding: 0.3rem 0;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #eee;
    }
    button[data-testid="stElementToolbarButton"] { display: none; }
    div[data-testid="stSidebar"] .sidebar-content {
        padding-top: 0.5rem;
    }
    div[data-testid="stSidebar"] hr {
        margin: 0.4rem 0;
    }
    .sidebar-section {
        margin-bottom: 0.6rem;
    }
    .sidebar-section h4 {
        font-size: 1rem;
        margin-bottom: 0.2rem;
        color: #333;
    }
    .sidebar-section p, .sidebar-section li {
        font-size: 0.9rem;
        color: #555;
        margin: 0.1rem 0;
    }
    .sidebar-section ul {
        padding-left: 1rem;
        margin: 0.2rem 0;
    }
    .file-section {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        margin-bottom: 0.6rem;
        border: 1px solid #dee2e6;
    }
    .file-section h4 {
        font-size: 1rem;
        margin: 0 0 0.2rem 0;
        color: #333;
        font-weight: 600;
    }
    .file-section ul {
        margin: 0;
        padding-left: 1.2rem;
    }
    .file-section li {
        font-size: 0.9rem;
        color: #444;
        margin: 0.3rem 0;
        line-height: 1.4;
        word-break: break-all;
    }
    .file-status {
        font-size: 0.85rem;
        color: #555;
        margin-top: 0.25rem;
    }
    @media (prefers-color-scheme: dark) {
        .instruction-box {
            background: #262730;
            border-left-color: #66bb6a;
        }
        .instruction-box h4 { color: #ddd; }
        .instruction-box ol, .instruction-box ul { color: #bbb; }
        .info-card {
            background: #1e1e1e;
            border-color: #333;
        }
        .tip-box {
            background: #1b3a1b;
            color: #a5d6a7;
        }
        .warning-box {
            background: #3a2a1b;
            color: #ffcc80;
        }
        .msg-ai {
            color: #e4e6eb;
        }
        .msg-actions .msg-action-btn {
            border-color: #555;
            color: #999;
        }
        .msg-actions .msg-action-btn:hover {
            background: #333;
            border-color: #777;
        }

        .chat-header-info { color: #999; border-bottom-color: #333; }
        .sidebar-section h4 { color: #ccc; }
        .sidebar-section p, .sidebar-section li { color: #999; }
        .file-section {
            background: #1e1e1e;
            border-color: #333;
        }
        .file-section h4 { color: #ddd; }
        .file-section li { color: #bbb; }
        .file-status { color: #999; }
    }
</style>
""", unsafe_allow_html=True)
