from typing import List, Dict, Any
import PyPDF2 # type: ignore
import docx # type: ignore
from pathlib import Path
from app.core.exceptions import DocumentProcessingError


class DocumentProcessor:
    def __init__(self):
        self.supported_formats = {'.pdf', '.txt', '.docx', '.md'}
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        try:
            path = Path(file_path)
            
            if file_type == '.pdf':
                return self._extract_from_pdf(path)
            elif file_type == '.txt' or file_type == '.md':
                return self._extract_from_text(path)
            elif file_type == '.docx':
                return self._extract_from_docx(path)
            else:
                raise DocumentProcessingError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            raise DocumentProcessingError(f"Error extracting text: {str(e)}")
    
    def _extract_from_pdf(self, path: Path) -> str:
        text = ""
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def _extract_from_text(self, path: Path) -> str:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_from_docx(self, path: Path) -> str:
        doc = docx.Document(path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()