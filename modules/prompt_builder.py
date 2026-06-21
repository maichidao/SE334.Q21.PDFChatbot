from enum import Enum


class PromptStyle(Enum):
    STANDARD = "standard"   
    STRICT   = "strict"     
    ACADEMIC = "academic"   
    SIMPLE   = "simple"     


TEMPLATES = {

    PromptStyle.STANDARD: """\
Bạn là trợ lý hỏi đáp tài liệu. Dưới đây là nội dung tài liệu PDF:
\"\"\"
{context}
\"\"\"
Dựa vào tài liệu trên, hãy trả lời câu hỏi sau bằng tiếng Việt:
{question}
Quy tắc:
- Có thông tin -> trả lời rõ ràng, trích dẫn phần liên quan trong tài liệu.
- Câu hỏi mơ hồ -> hỏi lại người dùng để làm rõ, ví dụ: "Bạn muốn hỏi về khía cạnh nào: X hay Y?"
- Không có thông tin -> trả lời đúng 1 câu: "Tài liệu không đề cập đến vấn đề này." Không được tự bịa thêm.
""",

    PromptStyle.STRICT: """\
Chỉ được trả lời dựa trên tài liệu sau, không dùng kiến thức bên ngoài:
\"\"\"
{context}
\"\"\"
Câu hỏi: {question}
Quy tắc:
- Câu hỏi mơ hồ -> hỏi lại để làm rõ.
- Không có thông tin -> trả lời: "Tài liệu không cung cấp thông tin về câu hỏi này."
- Không suy luận, không đoán mò, không bổ sung kiến thức ngoài tài liệu.
""",

    PromptStyle.ACADEMIC: """\
Bạn là trợ lý học thuật. Đọc tài liệu và trả lời chính xác, trích dẫn rõ nguồn:
\"\"\"
{context}
\"\"\"
Câu hỏi: {question}
Hướng dẫn:
- Trích dẫn rõ phần nào trong tài liệu hỗ trợ câu trả lời.
- Trình bày theo từng điểm nếu có nhiều khía cạnh.
- Câu hỏi mơ hồ -> nêu các cách hiểu có thể rồi trả lời từng cách.
- Không có thông tin -> ghi rõ, không bổ sung kiến thức ngoài.
- Trả lời bằng tiếng Việt.
""",

    PromptStyle.SIMPLE: """\
Tài liệu: {context}
Câu hỏi: {question}
Trả lời ngắn gọn bằng tiếng Việt. Nếu không có thông tin, nói rõ.
""",
        }


def build_prompt(
    context: str,
    question: str,
    style: PromptStyle = PromptStyle.STANDARD,
) -> str:
    """
    Xây dựng prompt từ context và question.
    Không cắt context ở đây — token_handler đã đảm bảo context nằm trong giới hạn.
    """
    if not context or not context.strip():
        raise ValueError("context không được để trống.")
    if not question or not question.strip():
        raise ValueError("question không được để trống.")

    return TEMPLATES[style].format(context=context.strip(), question=question.strip())


def get_style_description(style: PromptStyle) -> str:
    return {
        PromptStyle.STANDARD: "Trả lời rõ ràng, báo khi không có thông tin",
        PromptStyle.STRICT:   "Chỉ dùng tài liệu, không sáng tác thêm",
        PromptStyle.ACADEMIC: "Trích dẫn rõ ràng, trình bày theo điểm",
        PromptStyle.SIMPLE:   "Ngắn gọn, dùng để test nhanh",
    }.get(style, "")