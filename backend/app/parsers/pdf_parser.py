# app/parsers/pdf_parser.py
import pymupdf
from pathlib import Path
from app.parsers.abstract_parser_base import BaseParser


class PdfParser(BaseParser):

    def parse(self, file_path: Path) -> str:
        text = []

        with pymupdf.open(file_path) as pdf:
            for page in pdf:
                text.append(page.get_text())

        return "\n".join(text)