import streamlit as st
from requests import HTTPError

from auth.service import AuthService
from chat.service import ChatService


class ChatView:

    def __init__(self, chat_service: ChatService, auth_service: AuthService, user):
        self.service = chat_service
        self.auth_service = auth_service
        self.user = user

    def render(self) -> None:
        # ── Sidebar ──────────────────────────────────────────────────────────
        with st.sidebar:
            st.markdown("### 🤖 AI Support")
            st.divider()

            if self.service.has_document():
                doc_name = st.session_state.get("document_name", "Document")
                st.success(f"📄 {doc_name}")
                if st.button("📤 Upload New Document", use_container_width=True):
                    st.session_state.pop("document_id", None)
                    st.session_state.pop("document_name", None)
                    st.session_state.pop("messages", None)
                    st.rerun()
            else:
                st.info("Upload a document to start chatting.")

            st.divider()
            name = self.user.name if self.user else "User"
            st.markdown(f"👤 **{name}**")
            if st.button("🚪 Logout", use_container_width=True):
                self.auth_service.logout()
                st.session_state["auth_page"] = "login"
                st.rerun()


        # ── Main area ────────────────────────────────────────────────────────
        if not self.service.has_document():
            self._render_upload()
        else:
            self._render_chat()

    # ── Upload / pick stage ───────────────────────────────────────────────────

    def _render_upload(self) -> None:
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.markdown("## 📂 Choose a Document")
            st.markdown("Pick an existing document or upload a new one.")
            st.divider()

            tab_existing, tab_new = st.tabs(["📋 My Documents", "📤 Upload New"])

            # ── Tab 1: pick from existing ─────────────────────────────────────
            with tab_existing:
                try:
                    docs = self.service.api.list_documents()
                except Exception as e:
                    docs = []
                    st.error(f"Could not load documents: {e}")

                if not docs:
                    st.info("No documents uploaded yet. Use the 'Upload New' tab to add one.")
                else:
                    for doc in docs:
                        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                        c1.markdown(f"**{doc['original_filename']}**\n\n*Uploaded by: {doc.get('owner_name', 'Unknown')}*")
                        c2.caption(doc.get("document_type", ""))
                        if c3.button("Chat →", key=f"pick_{doc['id']}"):
                            st.session_state["document_id"] = doc["id"]
                            st.session_state["document_name"] = doc["original_filename"]
                            st.session_state.pop("messages", None)
                            st.rerun()
                        if c4.button("🗑️", key=f"del_{doc['id']}", help="Delete document completely"):
                            try:
                                self.service.delete_document(doc["id"])
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {e}")

            # ── Tab 2: upload new ──────────────────────────────────────────────
            with tab_new:
                file = st.file_uploader(
                    "Choose a file",
                    type=["pdf", "docx", "txt"],
                    label_visibility="collapsed",
                )
                if file and st.button("🚀 Upload & Process", use_container_width=True, type="primary"):
                    owner = self.user.name if self.user else "unknown"
                    with st.spinner("Processing your document… this may take a moment."):
                        try:
                            self.service.upload_and_process(
                                file_bytes=file.read(),
                                filename=file.name,
                            )
                            st.success("✅ Document ready! You can now start chatting.")
                            st.rerun()
                        except HTTPError as e:
                            st.error(f"Upload failed: {e.response.text if e.response else str(e)}")
                        except Exception as e:
                            st.error(f"Something went wrong: {e}")

    # ── Chat stage ────────────────────────────────────────────────────────────


    def _render_chat(self) -> None:
        c1, c2 = st.columns([8, 2])
        c1.markdown(f"## 💬 Chat — *{st.session_state.get('document_name', 'Document')}*")
        
        if c2.button("← Back to docs", use_container_width=True):
            st.session_state.pop("document_id", None)
            st.session_state.pop("document_name", None)
            st.session_state.pop("messages", None)
            st.rerun()
            
        st.divider()

        # Initialise history
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "👋 Hi! I've read your document. Ask me anything about it."}
            ]

        # Replay history
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # New input
        if prompt := st.chat_input("Ask a question about your document…"):
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        answer = self.service.ask(prompt)
                    except HTTPError as e:
                        answer = f"⚠️ Error: {e.response.text if e.response else str(e)}"
                    except Exception as e:
                        answer = f"⚠️ Something went wrong: {e}"
                st.markdown(answer)

            st.session_state["messages"].append({"role": "assistant", "content": answer})
