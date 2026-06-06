import io
import re
from dataclasses import dataclass, field
from typing import Union

try:
    from PyPDF2 import PdfReader
    from PyPDF2.errors import PdfReadError, PdfStreamError
except ImportError:
    raise ImportError(
        "PyPDF2 chưa được cài. Chạy: pip install PyPDF2"
    )

MAX_FILE_SIZE_MB = 20          
MIN_CHARS_PER_PAGE = 20       
REPLACEMENT_CHAR = ""         

@dataclass
class PDFResult:
    """Kết quả trả về từ extract_text()."""
    success: bool
    text: str = ""
    total_pages: int = 0
    extracted_pages: int = 0
    skipped_pages: list = field(default_factory=list)  
    is_scanned: bool = False    
    error: str = ""            

    def to_dict(self) -> dict:
        return {
            "success":         self.success,
            "text":            self.text,
            "total_pages":     self.total_pages,
            "extracted_pages": self.extracted_pages,
            "skipped_pages":   self.skipped_pages,
            "is_scanned":      self.is_scanned,
            "error":           self.error,
        }


def _clean_text(raw: str) -> str:
    """
    - Bỏ ký tự NULL và control characters (trừ newline, tab)
    - Chuẩn hoá khoảng trắng thừa
    - Giữ nguyên dấu câu và ký tự đặc biệt hợp lệ
    """
    if not raw:
        return ""

    # Bỏ ký tự NULL
    text = raw.replace("\x00", "")

    # Bỏ control characters bất hợp lệ (giữ \n, \t, \r)
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Chuẩn hoá: nhiều dòng trống liên tiếp 
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Chuẩn hoá: nhiều khoảng trắng trên cùng dòng
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def _extract_page_text(page) -> str:
    """
    Trích xuất text từ một trang, xử lý encoding lỗi.
    Trả về chuỗi rỗng nếu trang không có text.
    """
    try:
        text = page.extract_text()
        if text is None:
            return ""
        return text

    except UnicodeDecodeError:
        try:
            raw_text = page.extract_text(errors="ignore")
            return raw_text if raw_text else ""
        except Exception:
            return ""

    except Exception:
        # Mọi lỗi khác (lỗi font, cấu trúc PDF lạ, ...) 
        return ""


def _is_scanned_pdf(reader: "PdfReader", sample_pages: int = 3) -> bool:
    """
    Kiểm tra xem PDF có phải bản scan (chỉ có ảnh, không có text layer) không.
    Lấy mẫu tối đa `sample_pages` trang đầu để kiểm tra.
    """
    pages_to_check = min(sample_pages, len(reader.pages))
    total_chars = 0

    for i in range(pages_to_check):
        text = _extract_page_text(reader.pages[i])
        total_chars += len(text.strip())

    avg_chars = total_chars / pages_to_check if pages_to_check > 0 else 0
    return avg_chars < 50


def extract_text(
    pdf_source: Union[str, bytes, io.BytesIO],
    page_separator: str = "\n\n--- Trang {page} ---\n\n",
    include_page_numbers: bool = True,
) -> PDFResult:
    try:
        if isinstance(pdf_source, str):
            # Đường dẫn file
            reader = PdfReader(pdf_source)

        elif isinstance(pdf_source, bytes):
            # Bytes thô
            if len(pdf_source) > MAX_FILE_SIZE_MB * 1024 * 1024:
                return PDFResult(
                    success=False,
                    error=f"File quá lớn. Tối đa {MAX_FILE_SIZE_MB}MB."
                )
            stream = io.BytesIO(pdf_source)
            reader = PdfReader(stream)

        elif isinstance(pdf_source, io.BytesIO):
            reader = PdfReader(pdf_source)

        else:
            # Streamlit UploadedFile — có .read() giống BytesIO
            try:
                data = pdf_source.read()
                if len(data) > MAX_FILE_SIZE_MB * 1024 * 1024:
                    return PDFResult(
                        success=False,
                        error=f"File quá lớn. Tối đa {MAX_FILE_SIZE_MB}MB."
                    )
                reader = PdfReader(io.BytesIO(data))
            except AttributeError:
                return PDFResult(
                    success=False,
                    error="Định dạng đầu vào không hỗ trợ. Dùng đường dẫn, bytes hoặc BytesIO."
                )

    except PdfReadError as e:
        return PDFResult(success=False, error=f"File PDF bị hỏng hoặc không đọc được: {e}")
    except PdfStreamError as e:
        return PDFResult(success=False, error=f"Lỗi đọc stream PDF: {e}")
    except FileNotFoundError:
        return PDFResult(success=False, error="Không tìm thấy file PDF.")
    except Exception as e:
        return PDFResult(success=False, error=f"Lỗi không xác định khi mở file: {e}")

    if reader.is_encrypted:
        try:
            reader.decrypt("")         
        except Exception:
            return PDFResult(
                success=False,
                error="PDF được bảo vệ bằng mật khẩu. Vui lòng nhập mật khẩu để mở khoá."
            )

    total_pages = len(reader.pages)
    if total_pages == 0:
        return PDFResult(success=False, error="File PDF không có trang nào.")

    is_scanned = _is_scanned_pdf(reader)

    pages_text = []
    skipped_pages = []

    for page_num, page in enumerate(reader.pages, start=1):
        raw_text = _extract_page_text(page)
        cleaned  = _clean_text(raw_text)

        if len(cleaned) < MIN_CHARS_PER_PAGE:
            skipped_pages.append(page_num)
            continue

        if include_page_numbers and page_separator:
            header = page_separator.format(page=page_num)
            pages_text.append(header + cleaned)
        else:
            pages_text.append(cleaned)

    full_text = "\n".join(pages_text)
    extracted_pages = total_pages - len(skipped_pages)

    if not full_text.strip():
        msg = (
            "Không trích xuất được text. PDF này có thể là bản scan (chỉ có ảnh). "
            "Cần OCR để đọc loại file này."
            if is_scanned else
            "Không tìm thấy nội dung text trong file PDF."
        )
        return PDFResult(
            success=False,
            total_pages=total_pages,
            is_scanned=is_scanned,
            error=msg,
        )

    return PDFResult(
        success=True,
        text=full_text,
        total_pages=total_pages,
        extracted_pages=extracted_pages,
        skipped_pages=skipped_pages,
        is_scanned=is_scanned,
    )


def get_pdf_info(pdf_source) -> dict:
    try:
        if isinstance(pdf_source, bytes):
            reader = PdfReader(io.BytesIO(pdf_source))
        elif isinstance(pdf_source, str):
            reader = PdfReader(pdf_source)
        else:
            data = pdf_source.read()
            reader = PdfReader(io.BytesIO(data))

        meta = reader.metadata or {}
        return {
            "total_pages":  len(reader.pages),
            "title":        meta.get("/Title"),
            "author":       meta.get("/Author"),
            "is_encrypted": reader.is_encrypted,
            "error":        None,
        }
    except Exception as e:
        return {
            "total_pages":  0,
            "title":        None,
            "author":       None,
            "is_encrypted": False,
            "error":        str(e),
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Cách dùng: py pdf_reader.py <đường_dẫn_file.pdf>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"\n Đọc file: {path}")

    info = get_pdf_info(path)
    print(f"   Số trang  : {info['total_pages']}")
    print(f"   Tiêu đề   : {info['title'] or '(không có)'}")
    print(f"   Tác giả   : {info['author'] or '(không có)'}")
    print(f"   Mã hoá    : {'Có' if info['is_encrypted'] else 'Không'}")

    result = extract_text(path)

    if not result.success:
        print(f"\nLỗi: {result.error}")
        sys.exit(1)

    print(f"\nTrích xuất thành công!")
    print(f"  Tổng trang   : {result.total_pages}")
    print(f"  Trang đọc được: {result.extracted_pages}")
    if result.skipped_pages:
        print(f"Trang bỏ qua : {result.skipped_pages}")
    if result.is_scanned:
        print("Phát hiện trang scan (ảnh) — chất lượng text có thể thấp")
    # print(f"\n── Nội dung (500 ký tự đầu) ──")
    # print(result.text[:500])
    print("...")