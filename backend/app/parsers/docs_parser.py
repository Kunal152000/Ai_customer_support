# app/parsers/docx_parser.py

from pathlib import Path

from docx import Document

from app.parsers.abstract_parser_base import BaseParser


class DocxParser(BaseParser):

    def parse(self, file_path: Path) -> str:
        document = Document(file_path)

        return "\n".join(paragraph.text for paragraph in document.paragraphs)
        