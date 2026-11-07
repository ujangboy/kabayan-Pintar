import os

try:
    import pymupdf as fitz  # PyMuPDF (paket `fitz` lama sudah deprecated)
except ImportError:
    fitz = None
try:
    import docx
except ImportError:
    docx = None

_DOCS_MISSING_MSG = "fitur documents belum terpasang. Jalankan 'kp feature documents'."

def extract_text(file_path: str) -> str:
    """
    Extracts text from PDF, DOCX, TXT, PPTX, XLSX, and CSV files.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    # Legacy formats check
    if ext in ['.doc', '.ppt', '.xls']:
        raise ValueError(f"Format lama {ext} tidak didukung. Silakan 'Save As' file Anda ke format modern (.docx, .pptx, .xlsx).")
        
    if ext == '.pdf':
        return extract_from_pdf(file_path)
    elif ext == '.docx':
        return extract_from_docx(file_path)
    elif ext in ['.txt', '.csv', '.md']:
        return extract_from_txt(file_path)
    elif ext == '.pptx':
        try:
            from . import pptx_parser
        except ImportError:
            return f"Error membaca PPTX: {_DOCS_MISSING_MSG}"
        return pptx_parser.parse_pptx(file_path)
    elif ext == '.xlsx':
        try:
            from . import xlsx_parser
        except ImportError:
            return f"Error membaca XLSX: {_DOCS_MISSING_MSG}"
        return xlsx_parser.extract_text(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def extract_from_pdf(file_path: str) -> str:
    if fitz is None:
        return f"Error membaca PDF: {_DOCS_MISSING_MSG}"
    try:
        doc = fitz.open(file_path)
        full_text = []
        for page in doc:
            blocks = page.get_text("blocks")
            for block in blocks:
                if block[6] == 0:  # text block
                    text = block[4].strip()
                    if text:
                        full_text.append(text)
        return "\n\n".join(full_text)
    except Exception as e:
        return f"Error membaca PDF: {e}"

def extract_from_docx(file_path: str) -> str:
    if docx is None:
        return f"Error membaca DOCX: {_DOCS_MISSING_MSG}"
    try:
        doc = docx.Document(file_path)
        full_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        return "\n\n".join(full_text)
    except Exception as e:
        return f"Error membaca DOCX: {e}"

def extract_from_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        return f"Error membaca TXT: {e}"
