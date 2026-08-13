import streamlit as st

from chat.api import ChatAPI


class ChatService:
    def __init__(self, api: ChatAPI):
        self.api = api

    def upload_and_process(self, file_bytes: bytes, filename: str) -> None:
        doc = self.api.upload(file_bytes, filename)
        self.api.process(doc.id)
        st.session_state["document_id"] = str(doc.id)
        st.session_state["document_name"] = doc.original_filename

    def ask(self, question: str) -> str:
        document_id = st.session_state.get("document_id")
        return self.api.chat(question, document_id=document_id).answer

    @staticmethod
    def has_document() -> bool:
        return bool(st.session_state.get("document_id"))
