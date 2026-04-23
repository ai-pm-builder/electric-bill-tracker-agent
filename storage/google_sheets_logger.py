import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

class GoogleSheetsLogger:
    def __init__(self, sheet_id=None):
        self.sheet_id = sheet_id or os.getenv("GOOGLE_SHEET_ID")
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        if not self.sheet_id:
            raise ValueError("GOOGLE_SHEET_ID environment variable is missing.")
        self._authenticate()

    def _authenticate(self):
        creds_json = os.getenv("GOOGLE_CREDENTIALS")
        creds_dict = None
        
        # Check if they have the JSON file locally to avoid .env string parsing headaches
        if os.path.exists("google_credentials.json"):
            print("GoogleSheetsLogger: Loading credentials from local google_credentials.json file...")
            with open("google_credentials.json", "r") as f:
                creds_dict = json.load(f)
        elif creds_json:
            try:
                creds_dict = json.loads(creds_json)
            except json.JSONDecodeError:
                raise Exception("The GOOGLE_CREDENTIALS string in your .env is corrupted (invalid JSON syntax). Please use a file instead.")
                
        if not creds_dict:
            raise ValueError("Missing GOOGLE_CREDENTIALS. Provide it via .env or save the file as google_credentials.json in the project root!")
        
        try:
            credentials = Credentials.from_service_account_info(creds_dict, scopes=self.scopes)
            self.client = gspread.authorize(credentials)
            self.sheet = self.client.open_by_key(self.sheet_id).sheet1
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Sheets: {e}")

    def log_balance(self, account_no: str, current_balance: float) -> float:
        """
        Appends the new record and calculates the difference from the LAST appended record for this account.
        """
        date = datetime.now().strftime("%Y-%m-%d")
        try:
            records = self.sheet.get_all_records()
        except Exception:
            # If the sheet is empty or headers are missing, get_all_records() will throw an error.
            # Initialize the headers.
            self.sheet.append_row(["Date", "Account Number", "Balance"])
            records = []
            
        previous_balance = None
        # Go backwards through records to find the last match for this account
        for row in reversed(records):
            if str(row.get("Account Number", "")) == str(account_no):
                try:
                    previous_balance = float(row.get("Balance", 0))
                    break
                except ValueError:
                    continue
                    
        # Append the new daily row
        self.sheet.append_row([date, str(account_no), current_balance])
        
        if previous_balance is not None:
            # E.g. Previous balance = 500, Current = 450 -> Daily Spend = 50
            daily_spend = previous_balance - current_balance
            return daily_spend
        else:
            return 0.0
