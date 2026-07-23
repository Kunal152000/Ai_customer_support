# app/chunking/recursive_chunker.py

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.chunking.abstract_chunking_base import BaseChunker


class RecursiveChunker(BaseChunker):

    def __init__( self,chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)

    def chunk(self, text: str) -> list[str]:
        return self.splitter.split_text(text)