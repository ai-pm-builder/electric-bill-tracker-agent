import csv
import os
from datetime import datetime

class CSVLogger:
    def __init__(self, filepath="output/bill_log.csv"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Account_No", "Balance", "Daily_Spend_Diff"])

    def get_last_balance(self, account_no: str) -> float:
        last_balance = None
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row["Account_No"] == account_no:
                            last_balance = float(row["Balance"])
            except Exception as e:
                print(f"Error reading {self.filepath}: {e}")
        return last_balance

    def log_balance(self, account_no: str, current_balance: float) -> float:
        """Logs the balance and returns the diff from the previous balance.
        If diff > 0, it means the balance decreased (money spent).
        If diff < 0, it means the balance increased (recharged).
        """
        last_balance = self.get_last_balance(account_no)
        
        diff = 0.0
        if last_balance is not None:
            diff = last_balance - current_balance
        
        timestamp = datetime.now().isoformat()
        
        with open(self.filepath, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, account_no, f"{current_balance:.2f}", f"{diff:.2f}"])
            
        return diff
