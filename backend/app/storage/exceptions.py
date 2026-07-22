from pathlib import Path


class StorageError(Exception):
    """Base exception for storage operations."""


class FileSaveError(StorageError):
    def __init__(self, filename: str):
        super().__init__(f"Failed to save file: {filename}")


class FileReadError(StorageError):
    def __init__(self, path: Path):
        super().__init__(f"Failed to read file: {path}")


class FileDeleteError(StorageError):
    def __init__(self, path: Path):
        super().__init__(f"Failed to delete file: {path}")


class FileNotFoundError(StorageError):
    def __init__(self, path: Path):
        super().__init__(f"File not found: {path}")