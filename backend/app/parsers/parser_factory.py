# app/parsers/parser_factory.py

from pathlib import Path

from app.parsers.pdf_parser import PdfParser
from app.parsers.docs_parser import DocxParser
from app.parsers.txt_parser import TxtParser


class ParserFactory:

    @staticmethod
    def get_parser(file_path: Path):
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return PdfParser()

        if suffix == ".docx":
            return DocxParser()

        if suffix == ".txt":
            return TxtParser()

        raise ValueError(f"Unsupported file type: {suffix}")