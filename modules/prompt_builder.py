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
Lưu ý: Nếu tài liệu không đề cập, hãy nói rõ "Tài liệu không đề cập đến vấn đề này."
""",

    PromptStyle.STRICT: """\
Chỉ được trả lời dựa trên tài liệu sau, không dùng kiến thức bên ngoài:
\"\"\"
{context}
\"\"\"
Câu hỏi: {question}
Nếu tài liệu không có thông tin → trả lời: "Tài liệu không cung cấp thông tin về câu hỏi này."
""",

    PromptStyle.ACADEMIC: """\
Bạn là trợ lý học thuật. Đọc tài liệu và trả lời chính xác, trích dẫn rõ nguồn:
\"\"\"
{context}
\"\"\"
Câu hỏi: {question}
Trả lời bằng tiếng Việt, trình bày theo từng điểm nếu có nhiều khía cạnh.
""",

    PromptStyle.SIMPLE: """\
Tài liệu: {context}
Câu hỏi: {question}
Trả lời ngắn gọn bằng tiếng Việt:
""",
        }


def build_prompt(
    context: str,
    question: str,
    style: PromptStyle = PromptStyle.STANDARD,
    max_context_chars: int = 30000,
) -> str:
    if not context or not context.strip():
        raise ValueError("context không được để trống.")
    if not question or not question.strip():
        raise ValueError("question không được để trống.")

    if len(context) > max_context_chars:
        context = context[:max_context_chars] + "\n\n[...Tài liệu bị cắt bớt do quá dài...]"

    return TEMPLATES[style].format(context=context.strip(), question=question.strip())


def get_style_description(style: PromptStyle) -> str:
    return {
        PromptStyle.STANDARD: "Trả lời rõ ràng, báo khi không có thông tin",
        PromptStyle.STRICT:   "Chỉ dùng tài liệu, không sáng tác thêm",
        PromptStyle.ACADEMIC: "Trích dẫn rõ ràng, trình bày theo điểm",
        PromptStyle.SIMPLE:   "Ngắn gọn, dùng để test nhanh",
    }.get(style, "")