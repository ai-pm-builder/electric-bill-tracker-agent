import os
from dotenv import load_dotenv
from scrapers.uppcl_scraper import UPPCLScraper
from storage.csv_logger import CSVLogger
from integrations.telegram_bot import TelegramBot

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    scraper = UPPCLScraper(headless=True) # set to False if you want to see the browser
    
    # Automatically switch between Cloud Storage and Local storage
    if os.getenv("GOOGLE_CREDENTIALS"):
        from storage.google_sheets_logger import GoogleSheetsLogger
        print("Using Google Sheets for cloud state tracking...")
        logger = GoogleSheetsLogger()
    else:
        print("Using local CSV for state tracking...")
        logger = CSVLogger()
        
    bot = TelegramBot()
    
    # Read configuration from .env or defaults
    district = os.getenv("UPPCL_ACCOUNT_1_DISTRICT", "Unnao")
    discom = os.getenv("UPPCL_ACCOUNT_1_DISCOM", "MVVNL")
    account_no = os.getenv("UPPCL_ACCOUNT_1_NUMBER", "4102342000")
    
    print(f"Starting bill tracking for Account: {account_no} in {district}...")
    
    try:
        # 1. Scrape Current Balance
        current_balance = scraper.get_remaining_balance(district, discom, account_no)
        print(f"Successfully retrieved current balance: ₹ {current_balance}")
        
        # 2. Log and Calculate Daily Spend
        daily_spend = logger.log_balance(account_no, current_balance)
        print(f"Calculated Daily Spend: ₹ {daily_spend}")
        
        # 3. Send Telegram Notification
        success = bot.send_bill_update(account_no, current_balance, daily_spend)
        if success:
            print("Telegram notification sent successfully!")
        else:
            print("Failed to send Telegram notification.")
            
    except Exception as e:
        error_msg = f"❌ Error in UPPCL Tracker for Account {account_no}: {e}"
        print(error_msg)
        bot.send_message(error_msg)

if __name__ == "__main__":
    main()
