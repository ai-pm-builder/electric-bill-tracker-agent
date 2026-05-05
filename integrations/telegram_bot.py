import os
import requests

class TelegramBot:
    def __init__(self, token=None, chat_id=None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        # Validate chat_id is a numeric value
        if self.chat_id and not str(self.chat_id).lstrip("-").isdigit():
            print(f"WARNING: TELEGRAM_CHAT_ID '{self.chat_id}' does not look like a numeric ID.")
            print("Run 'python get_chat_id.py' to discover your correct numeric chat ID.")

    def send_message(self, text: str) -> bool:
        if not self.token:
            print("TelegramBot: Missing token. Cannot send message.")
            return False
            
        if not self.chat_id:
            print("TelegramBot: Missing chat_id. Run 'python get_chat_id.py' to find it.")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response_data = response.json()
            
            if not response_data.get("ok"):
                print(f"TelegramBot: API error - {response_data.get('description', 'Unknown error')}")
                return False
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"Telegram API Error: {e}")
            if 'response' in locals() and response is not None:
                print(f"Response: {response.text}")
            return False

    def send_bill_update(self, account_no: str, current_balance: float, daily_spend: float):
        spend_text = f"₹ {daily_spend:.2f}"
        if daily_spend < 0:
            spend_text = f"₹ {abs(daily_spend):.2f} (Account Recharged/Increased)"
        
        if current_balance < 0:
            balance_text = f"₹ {abs(current_balance):.2f} (Due)"
        else:
            balance_text = f"₹ {current_balance:.2f}"
        
        msg = (
            f"⚡️ *UPPCL Daily Bill Update*\n\n"
            f"👤 *Account:* `{account_no}`\n"
            f"💸 *Daily Spend:* {spend_text}\n"
            f"💰 *Remaining Balance:* {balance_text}"
        )
        return self.send_message(msg)
