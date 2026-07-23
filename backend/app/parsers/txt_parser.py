# app/parsers/txt_parser.py

from pathlib import Path

from app.parsers.abstract_parser_base import BaseParser


class TxtParser(BaseParser):

    def parse(self, file_path: Path) -> str:
        return file_path.read_text(encoding="utf-8")