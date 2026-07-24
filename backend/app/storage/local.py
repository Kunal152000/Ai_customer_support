from pathlib import Path
import shutil

from fastapi import UploadFile

from app.storage.abstract_storage_base import StorageService
from app.storage.exceptions import (
    FileDeleteError,
    FileNotFoundError,
    FileReadError,
    FileSaveError,
)

class LocalStorageService(StorageService):

    def __init__(self, storage_root: str = "storage/documents"):
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)

    async def save(self,file: UploadFile,filename: str,) -> str:
        destination = self.storage_root / filename
        try:
            with destination.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            return str(destination.relative_to("storage"))

        except Exception as exc:
            raise FileSaveError(filename) from exc

    def read(self,relative_path: str,) -> Path:
        path = Path("storage") / relative_path
        if not path.exists():
            raise FileNotFoundError(path)
        return path

    def delete(self,relative_path: str,) -> None:
        path = Path("storage") / relative_path
        try:
            if not path.exists():
                raise FileNotFoundError(path)
            path.unlink()
        except Exception as exc:
            raise FileDeleteError(path) from exc

    def exists(self,relative_path: str,) -> bool:
        path = Path("storage") / relative_path
        return path.exists()