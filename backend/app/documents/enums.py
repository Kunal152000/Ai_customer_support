from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"

class DocumentType(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    DOC = "DOC"
    TXT = "TXT"
    CSV = "CSV"
    XLS = "XLS"
    XLSX = "XLSX"
    # PPT = "PPT"
    # PPTX = "PPTX"
    # MARKDOWN = "MARKDOWN"
    # IMAGE = "IMAGE"
    # JSON = "JSON"
    # XML = "XML"
    # HTML = "HTML"
    URL = "URL"