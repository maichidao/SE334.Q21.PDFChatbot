import re
from dataclasses import dataclass
from typing import Tuple, Optional
from .gemini_client import ask_gemini

# Giới hạn token cho Gemini API
MAX_INPUT_TOKENS = 100000
CHARS_PER_TOKEN = 3.5
WARNING_THRESHOLD = 0.8

# Token tối đa có thể sử dụng cho nội dung PDF 
MAX_PDF_TOKENS = int(MAX_INPUT_TOKENS * 0.8)
MAX_PDF_CHARS = int(MAX_PDF_TOKENS * CHARS_PER_TOKEN)

@dataclass
class TokenCheckResult:
    original_char_count: int         
    original_token_count: int         
    is_within_limit: bool            
    warning_message: str             
    status: str                       # "ok" | "warning" | "exceeded"


@dataclass
class TokenProcessResult:
    processed_text: str               
    processed_char_count: int         
    processed_token_count: int        
    processing_method: str            # "none" | "truncated" | "summarized"
    messages: list                    # Danh sách thông báo cho người dùng


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, int(len(text) / CHARS_PER_TOKEN))


def count_characters(text: str) -> int:
    return len(text) if text else 0

def check_token_limit(text: str) -> TokenCheckResult:
    if not text:
        return TokenCheckResult(
            original_char_count=0,
            original_token_count=0,
            is_within_limit=True,
            warning_message="",
            status="ok"
        )
    
    char_count = count_characters(text)
    token_count = estimate_tokens(text)
    
    if token_count > MAX_PDF_TOKENS:
        exceeded_percentage = ((token_count - MAX_PDF_TOKENS) / MAX_PDF_TOKENS) * 100
        warning_msg = (
            f"Cảnh báo: Nội dung PDF vượt quá giới hạn.\n"
            f"   • Giới hạn: {MAX_PDF_TOKENS:,} tokens ({MAX_PDF_CHARS:,} ký tự)\n"
            f"   • Hiện tại: {token_count:,} tokens ({char_count:,} ký tự)\n"
            f"   • Vượt quá: {exceeded_percentage:.1f}%\n"
            f"   • Hệ thống sẽ tự động cắt ngắn hoặc tóm tắt nội dung."
        )
        return TokenCheckResult(
            original_char_count=char_count,
            original_token_count=token_count,
            is_within_limit=False,
            warning_message=warning_msg,
            status="exceeded"
        )
    
    elif token_count > int(MAX_PDF_TOKENS * WARNING_THRESHOLD):
        remaining_percentage = ((MAX_PDF_TOKENS - token_count) / MAX_PDF_TOKENS) * 100
        warning_msg = (
            f"Cảnh báo: Nội dung PDF gần đạt giới hạn.\n"
            f"   • Giới hạn: {MAX_PDF_TOKENS:,} tokens ({MAX_PDF_CHARS:,} ký tự)\n"
            f"   • Hiện tại: {token_count:,} tokens ({char_count:,} ký tự)\n"
            f"   • Còn lại: {remaining_percentage:.1f}%"
        )
        return TokenCheckResult(
            original_char_count=char_count,
            original_token_count=token_count,
            is_within_limit=True,
            warning_message=warning_msg,
            status="warning"
        )
    
    else:
        return TokenCheckResult(
            original_char_count=char_count,
            original_token_count=token_count,
            is_within_limit=True,
            warning_message="",
            status="ok"
        )

def truncate_text(text: str, max_chars: Optional[int] = None) -> str:

    if max_chars is None:
        max_chars = MAX_PDF_CHARS
    
    if not text or len(text) <= max_chars:
        return text
    
    truncated = text[:max_chars]
    
    for end_char in [".", "!", "?"]:
        last_pos = truncated.rfind(end_char)
        if last_pos > max_chars * 0.8:  
            return truncated[:last_pos + 1]
    
    last_newline = truncated.rfind("\n")
    if last_newline > max_chars * 0.8:
        return truncated[:last_newline]
    
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.8:
        return truncated[:last_space]
    
    return truncated + "..."


def summarize_text(text: str, max_length: str = "medium") -> Optional[str]:

    if not text:
        return None
    
    length_prompt = {
        "short": "1-2 đoạn",
        "medium": "3-5 đoạn",
        "long": "5-10 đoạn"
    }.get(max_length, "3-5 đoạn")
    
    prompt = (
        f"Hãy tóm tắt nội dung sau trong {length_prompt} rõ ràng, "
        f"giữ lại những thông tin quan trọng nhất:\n\n{text}"
    )
    
    try:
        summary = ask_gemini(prompt)
        return summary if summary else None
    except Exception as e:
        print(f"❌ Lỗi khi tóm tắt: {str(e)}")
        return None


def process_pdf_content(text: str, prefer_summarize: bool = True) -> TokenProcessResult:

    messages = []
    
    if not text:
        return TokenProcessResult(
            processed_text="",
            processed_char_count=0,
            processed_token_count=0,
            processing_method="none",
            messages=["Nội dung PDF rỗng."]
        )
    
    check_result = check_token_limit(text)
    
    if check_result.is_within_limit and check_result.status != "warning":
        return TokenProcessResult(
            processed_text=text,
            processed_char_count=check_result.original_char_count,
            processed_token_count=check_result.original_token_count,
            processing_method="none",
            messages=[]
        )
    
    if not check_result.is_within_limit:
        messages.append(check_result.warning_message)

        if prefer_summarize:
            messages.append("Hệ thống đang tóm tắt nội dung...")
            summary = summarize_text(text, max_length="long")
            
            if summary:
        
                summary_check = check_token_limit(summary)
                
                if summary_check.is_within_limit:
                    messages.append(
                        f"Đã tóm tắt thành công.\n"
                        f"   • Giảm từ {check_result.original_token_count:,} "
                        f"xuống {summary_check.original_token_count:,} tokens"
                    )
                    return TokenProcessResult(
                        processed_text=summary,
                        processed_char_count=summary_check.original_char_count,
                        processed_token_count=summary_check.original_token_count,
                        processing_method="summarized",
                        messages=messages
                    )
                else:
                    messages.append("Tóm tắt vẫn quá lớn, sẽ cắt ngắn thêm.")
            else:
                messages.append("Tóm tắt không thành công, sẽ cắt ngắn nội dung.")
        
        truncated = truncate_text(text, MAX_PDF_CHARS)
        truncated_check = check_token_limit(truncated)
        
        messages.append(
            f"Đã cắt ngắn nội dung.\n"
            f"   • Từ {check_result.original_token_count:,} "
            f"xuống {truncated_check.original_token_count:,} tokens"
        )
        
        return TokenProcessResult(
            processed_text=truncated,
            processed_char_count=truncated_check.original_char_count,
            processed_token_count=truncated_check.original_token_count,
            processing_method="truncated",
            messages=messages
        )
    
    if check_result.status == "warning":
        messages.append(check_result.warning_message)
        return TokenProcessResult(
            processed_text=text,
            processed_char_count=check_result.original_char_count,
            processed_token_count=check_result.original_token_count,
            processing_method="none",
            messages=messages
        )
    
    return TokenProcessResult(
        processed_text=text,
        processed_char_count=check_result.original_char_count,
        processed_token_count=check_result.original_token_count,
        processing_method="none",
        messages=[]
    )



def get_token_stats(text: str) -> dict:

    char_count = count_characters(text)
    token_count = estimate_tokens(text)
    
    return {
        "character_count": char_count,
        "estimated_tokens": token_count,
        "max_tokens_allowed": MAX_PDF_TOKENS,
        "max_chars_allowed": MAX_PDF_CHARS,
        "usage_percentage": (token_count / MAX_PDF_TOKENS * 100) if MAX_PDF_TOKENS > 0 else 0,
        "is_within_limit": token_count <= MAX_PDF_TOKENS
    }


def format_token_stats(stats: dict) -> str:

    return (
        f"Thống kê token:\n"
        f"   • Ký tự: {stats['character_count']:,} / {stats['max_chars_allowed']:,}\n"
        f"   • Token: {stats['estimated_tokens']:,} / {stats['max_tokens_allowed']:,}\n"
        f"   • Mức sử dụng: {stats['usage_percentage']:.1f}%\n"
        f"   • Trạng thái: {'OK' if stats['is_within_limit'] else 'Vượt quá'}"
    )
