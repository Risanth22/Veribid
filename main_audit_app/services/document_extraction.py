"""
Document Text Extraction Service.
Extracts text from multiple uploaded files (PDF, DOCX, TXT)
and maintains document-level tracking for traceability.
"""

import os
from pathlib import Path
from pypdf import PdfReader

try:
    import docx
except ImportError:
    docx = None

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None


def extract_text_from_pdf(filepath):
    """Extracts text from a PDF file using PyMuPDF or PyPDF fallback."""
    text = ""
    # Try PyMuPDF first (faster, handles layouts better)
    if fitz:
        try:
            doc = fitz.open(str(filepath))
            for page in doc:
                text += page.get_text() + "\n"
            if text.strip():
                return text.strip()
        except Exception:
            pass

    # PyPDF fallback
    try:
        reader = PdfReader(str(filepath))
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    except Exception as e:
        text = f"[PDF Extraction Error: {str(e)}]"
        
    return text.strip()


def extract_text_from_docx(filepath):
    """Extracts text from a Microsoft Word .docx document."""
    if not docx:
        return "[python-docx not installed]"
    try:
        doc = docx.Document(str(filepath))
        full_text = []
        for p in doc.paragraphs:
            if p.text:
                full_text.append(p.text)
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))
        return "\n".join(full_text).strip()
    except Exception as e:
        return f"[DOCX Extraction Error: {str(e)}]"


def extract_text_from_txt(filepath):
    """Extracts text from a plain text file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except Exception as e:
        return f"[TXT Extraction Error: {str(e)}]"


def extract_documents_corpus(saved_files):
    """
    Extracts text from all uploaded files and returns:
    1. doc_records: list of {filename, original_name, path, text, size}
    2. combined_text: aggregated document text for LLM parsing
    """
    doc_records = []
    combined_parts = []

    for file_info in saved_files:
        path = Path(file_info["path"])
        ext = path.suffix.lower()
        extracted = ""

        if ext == ".pdf":
            extracted = extract_text_from_pdf(path)
        elif ext in [".docx", ".doc"]:
            extracted = extract_text_from_docx(path)
        elif ext in [".txt", ".csv", ".json", ".xml"]:
            extracted = extract_text_from_txt(path)
        else:
            extracted = f"[Unsupported document format: {ext}]"

        record = {
            "filename": file_info.get("filename", path.name),
            "original_name": file_info.get("original_name", path.name),
            "path": str(path),
            "size": file_info.get("size", path.stat().st_size if path.exists() else 0),
            "text": extracted
        }
        doc_records.append(record)

        combined_parts.append(
            f"--- START OF DOCUMENT: {record['original_name']} ---\n"
            f"{extracted}\n"
            f"--- END OF DOCUMENT: {record['original_name']} ---\n"
        )

    return doc_records, "\n\n".join(combined_parts)
