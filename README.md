# SE334.Q21.PDFChatbot
Chatbot hỏi đáp tài liệu PDF sử dụng Python, Streamlit và Gemini API.

## Cấu trúc thư mục
```text
pdf-chatbot/
│
├── app.py
│   # Entry point - chạy ứng dụng Streamlit
│
├── modules/
│   ├── pdf_reader.py      # Đọc PDF, trích xuất văn bản
│   ├── gemini_client.py   # Kết nối Gemini API
│   ├── prompt_builder.py  # Xây dựng Prompt Template
│   ├── token_handler.py   # Xử lý token limit
│
├── components/
│   ├── upload_page.py     # Giao diện upload PDF
│   ├── chat_page.py       # Giao diện hỏi đáp
|
├── data/                  # chưa có thêm 
│   ├── uploads/           # PDF người dùng upload
│
├── tests/
│   ├── sample_pdfs/       # Bộ PDF kiểm thử
│   ├── test_questions.txt # Danh sách câu hỏi kiểm thử
│   ├── test_results.md    # Ghi nhận kết quả test
│   └── bug_log.md         # Nhật ký lỗi phát hiện được
│
├── .env
│   # GEMINI_API_KEY
│
├── .gitignore
│   # .env
│   # __pycache__/
│   # .streamlit/
│
├── requirements.txt    
│   # streamlit
│   # PyPDF2
│   # google-generativeai
│   # python-dotenv
│
└── README.md              # Hướng dẫn cài đặt và chạy dự án
```

## Install PyPDF2
Cách 1
```bash
py -m pip install -r requirements.txt
```
Cách 2
```bash
python -m pip install -r requirements.txt
```

