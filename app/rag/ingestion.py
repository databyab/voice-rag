import os
from typing import List, Dict, Any
from pathlib import Path
import pypdf
import docx
from app.utils.logging import logger

class DocumentLoader:
    """Loads and extracts text content from PDF, DOCX, TXT, and MD files."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

    @classmethod
    def load_document(cls, file_path: str) -> List[Dict[str, Any]]:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension '{ext}'. Supported: {cls.SUPPORTED_EXTENSIONS}")

        filename = path.name
        logger.info(f"Loading document: {filename} ({ext})")

        if ext == ".pdf":
            return cls._parse_pdf(file_path, filename)
        elif ext == ".docx":
            return cls._parse_docx(file_path, filename)
        elif ext in {".txt", ".md"}:
            return cls._parse_text(file_path, filename, ext)
        else:
            raise ValueError(f"Unhandled extension {ext}")

    @staticmethod
    def _parse_pdf(file_path: str, filename: str) -> List[Dict[str, Any]]:
        pages = []
        try:
            reader = pypdf.PdfReader(file_path)
            for i, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                cleaned_text = text.strip()
                if cleaned_text:
                    pages.append({
                        "content": cleaned_text,
                        "metadata": {
                            "source": filename,
                            "page": i,
                            "file_type": "pdf"
                        }
                    })
        except Exception as e:
            logger.error(f"Error extracting text from PDF {filename}: {e}")
            raise RuntimeError(f"Failed to process PDF {filename}: {e}")
        return pages

    @staticmethod
    def _parse_docx(file_path: str, filename: str) -> List[Dict[str, Any]]:
        pages = []
        try:
            doc = docx.Document(file_path)
            full_text = []
            for p in doc.paragraphs:
                if p.text.strip():
                    full_text.append(p.text.strip())
            
            combined_text = "\n\n".join(full_text)
            if combined_text:
                pages.append({
                    "content": combined_text,
                    "metadata": {
                        "source": filename,
                        "page": 1,
                        "file_type": "docx"
                    }
                })
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {filename}: {e}")
            raise RuntimeError(f"Failed to process DOCX {filename}: {e}")
        return pages

    @staticmethod
    def _parse_text(file_path: str, filename: str, ext: str) -> List[Dict[str, Any]]:
        pages = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                if content:
                    pages.append({
                        "content": content,
                        "metadata": {
                            "source": filename,
                            "page": 1,
                            "file_type": ext.lstrip(".")
                        }
                    })
        except Exception as e:
            logger.error(f"Error reading text file {filename}: {e}")
            raise RuntimeError(f"Failed to read file {filename}: {e}")
        return pages
