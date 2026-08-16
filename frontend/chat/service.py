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

    def ask_stream(self, question: str):
        document_id = st.session_state.get("document_id")
        return self.api.chat_stream(question, document_id=document_id)

    def delete_document(self, document_id: str) -> None:
        self.api.delete_document(document_id)
        if st.session_state.get("document_id") == str(document_id):
            st.session_state.pop("document_id", None)
            st.session_state.pop("document_name", None)
            st.session_state.pop("messages", None)

    @staticmethod
    def has_document() -> bool:
        return bool(st.session_state.get("document_id"))
