import logging
from typing import List

from config import settings

logger = logging.getLogger(__name__)


def write_to_google_sheets(results: List[dict]) -> None:
    """
    Записує результати в Google Sheets (опціональна фіча).
    Працює через сервісний акаунт Google.
    """
    if not settings.GOOGLE_SHEETS_CREDENTIALS_FILE:
        logger.info("Google Sheets credentials не вказано. Пропускаю запис.")
        return

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=scopes
        )
        gc = gspread.authorize(creds)

        try:
            sheet = gc.open(settings.GOOGLE_SHEET_NAME).sheet1
        except gspread.SpreadsheetNotFound:
            sheet = gc.create(settings.GOOGLE_SHEET_NAME).sheet1

        sheet.clear()

        headers = [
            "ID", "Channel", "Timestamp", "Category", "Department",
            "Priority", "Summary", "Actions", "Needs Clarification",
            "Language", "Reasoning",
        ]
        sheet.append_row(headers)

        for r in results:
            row = [
                r.get("id", ""),
                r.get("channel", ""),
                r.get("timestamp", ""),
                r.get("category", ""),
                r.get("target_department") or "",
                r.get("priority", ""),
                r.get("short_summary", ""),
                "; ".join(r.get("requested_actions", [])),
                "Так" if r.get("needs_clarification") else "Ні",
                r.get("suggested_language", ""),
                r.get("reasoning") or "",
            ]
            sheet.append_row(row)

        logger.info(f"✅ Дані записано в Google Sheet: {settings.GOOGLE_SHEET_NAME}")

    except ImportError:
        logger.warning("gspread не встановлено. Пропускаю запис в Google Sheets.")
    except Exception as e:
        logger.error(f"Помилка запису в Google Sheets: {e}")