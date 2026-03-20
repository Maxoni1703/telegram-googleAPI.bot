import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SheetsService:
    def __init__(self):
        # Scopes for Google Sheets and Google Drive
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.credentials_file = os.getenv("CREDENTIALS_FILE", "service_account.json")
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        
        if not self.spreadsheet_id:
            raise ValueError("SPREADSHEET_ID not found in environment variables.")
        
        self.client = self._authenticate()
        self.sheet = self.client.open_by_key(self.spreadsheet_id).sheet1

    def _authenticate(self):
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Credentials file '{self.credentials_file}' not found.")
        
        credentials = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=self.scopes
        )
        return gspread.authorize(credentials)

    def append_data(self, mechanic_name: str, consumable: str, quantity: str):
        """Appends a new row to the Google Sheet."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        row = [date_str, mechanic_name, consumable, quantity]
        self.sheet.append_row(row)
        return True
