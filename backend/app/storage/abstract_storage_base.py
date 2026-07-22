from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile


class StorageService(ABC):

    @abstractmethod
    async def save(self,file: UploadFile,filename: str,
    ) -> str:
        """
        Save file and return its relative storage path.
        """
        pass

    @abstractmethod
    def read(self,relative_path: str,
    ) -> Path:
        """
        Return absolute path to stored file.
        """
        pass

    @abstractmethod
    def delete(self,relative_path: str,
    ) -> None:
        """
        Delete stored file.
        """
        pass

    @abstractmethod
    def exists(self,relative_path: str,
    ) -> bool:
        """
        Check whether a file exists.
        """
        pass