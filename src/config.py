import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Централізоване зберігання налаштувань"""
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "")
    GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME", "AI Requests Classification")
    SEM_LIMIT: int = int(os.getenv("SEM_LIMIT", "3"))
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.0-flash")
    INPUT_CSV: str = os.getenv("INPUT_CSV", "input_requests.csv")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")


settings = Settings()