from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    BACKEND_URL: str = os.getenv("BACKEND_URL","http://localhost:8000")

    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 30))


settings = Settings()