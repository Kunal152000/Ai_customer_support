import os
from pathlib import Path
from fastapi import UploadFile
from supabase import create_client, Client
from app.storage.abstract_storage_base import StorageService
from app.storage.exceptions import FileSaveError, FileNotFoundError, FileDeleteError

class SupabaseStorageService(StorageService):
    def __init__(self, bucket_name: str = None):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        self.client: Client = create_client(supabase_url, supabase_key)
        self.bucket = bucket_name or os.getenv("SUPABASE_BUCKET", "ai_customer_support")

    async def save(self, file: UploadFile, filename: str) -> str:
        try:
            file.file.seek(0)
            file_bytes = await file.read()
            # Upload bytes directly to the cloud bucket
            self.client.storage.from_(self.bucket).upload(
                path=filename,
                file=file_bytes,
                file_options={"content-type": file.content_type or "application/pdf"}
            )
            # The storage_location stored in DB will just be the raw filename inside the bucket
            return filename
        except Exception as exc:
            print(f"DEBUG SUPABASE UPLOAD FAIL: {exc}")
            raise FileSaveError(filename) from exc

    def read(self, relative_path: str) -> Path:
        """
        Parsers (like PyMuPDF) require local file handles. 
        We securely download the cloud blob to a short-lived tempfile.
        """
        try:
            file_bytes = self.client.storage.from_(self.bucket).download(relative_path)
            
            import tempfile
            temp_path = Path(tempfile.gettempdir()) / relative_path
            with open(temp_path, "wb") as f:
                f.write(file_bytes)
                
            return temp_path
        except Exception as exc:
            print(f"DEBUG SUPABASE DOWNLOAD FAIL: {exc}")
            raise FileNotFoundError(relative_path) from exc

    def delete(self, relative_path: str) -> None:
        try:
            # Wipe the remote file immediately
            self.client.storage.from_(self.bucket).remove([relative_path])
            
            # Wipe the local cached payload if it exists
            import tempfile
            temp_path = Path(tempfile.gettempdir()) / relative_path
            if temp_path.exists():
                temp_path.unlink()
        except Exception as exc:
            raise FileDeleteError(relative_path) from exc

    def exists(self, relative_path: str) -> bool:
        # Not heavily utilized; fallback
        return True
