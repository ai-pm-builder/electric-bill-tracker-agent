import os
import requests

class TelegramBot:
    def __init__(self, token=None, chat_id=None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def auto_discover_chat_id(self):
        """Attempts to find the chat_id from recent bot messages."""
        print("TelegramBot: Attempting to auto-discover Chat ID from recent messages...")
        try:
            resp = requests.get(f"https://api.telegram.org/bot{self.token}/getUpdates")
            data = resp.json()
            if data.get("ok") and len(data.get("result", [])) > 0:
                # Find the latest message and extract its chat ID
                for update in reversed(data["result"]):
                    if "message" in update and "chat" in update["message"]:
                        found_id = update["message"]["chat"]["id"]
                        print(f"TelegramBot: Auto-discovered Chat ID: {found_id}")
                        return found_id
            print("TelegramBot: Could not find any recent messages. Make sure you sent a message to the bot first!")
        except Exception as e:
            print(f"TelegramBot: Failed to auto-discover chat ID: {e}")
        return None

    def send_message(self, text: str) -> bool:
        if not self.token:
            print("TelegramBot: Missing token. Cannot send message.")
            return False
            
        if not self.chat_id:
            self.chat_id = self.auto_discover_chat_id()
            if not self.chat_id:
                return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response_data = response.json()
            
            # If the chat wasn't found, maybe they provided a username or a bad ID. Let's auto-discover.
            if not response_data.get("ok") and "chat not found" in response_data.get("description", "").lower():
                 print("TelegramBot: 'Chat not found' error. Trying to auto-discover the Chat ID...")
                 new_id = self.auto_discover_chat_id()
                 if new_id and str(new_id) != str(self.chat_id):
                     self.chat_id = new_id
                     payload["chat_id"] = self.chat_id
                     response = requests.post(self.api_url, json=payload)
                     response_data = response.json()
            
            response.raise_for_status()
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
