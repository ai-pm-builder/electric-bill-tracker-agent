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
    
    # Extract account configurations from environment
    accounts = []
    
    # Account 1
    dist1 = os.getenv("UPPCL_ACCOUNT_1_DISTRICT", "Unnao")
    disc1 = os.getenv("UPPCL_ACCOUNT_1_DISCOM", "MVVNL")
    acc1 = os.getenv("UPPCL_ACCOUNT_1_NUMBER", "4102342000")
    if dist1 and disc1 and acc1:
        accounts.append((dist1, disc1, acc1))
        
    # Account 2
    dist2 = os.getenv("UPPCL_ACCOUNT_2_DISTRICT")
    disc2 = os.getenv("UPPCL_ACCOUNT_2_DISCOM")
    acc2 = os.getenv("UPPCL_ACCOUNT_2_NUMBER")
    if dist2 and disc2 and acc2:
        accounts.append((dist2, disc2, acc2))
    
    for district, discom, account_no in accounts:
        print(f"\n--- Starting bill tracking for Account: {account_no} in {district} ---")
        
        try:
            # 1. Scrape Current Balance
            current_balance = scraper.get_remaining_balance(district, discom, account_no)
            balance_display = f"₹ {current_balance}" if current_balance >= 0 else f"₹ {abs(current_balance)} (Due)"
            print(f"Successfully retrieved current balance: {balance_display}")
            
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
            error_msg = f"Error in UPPCL Tracker for Account {account_no}: {e}"
            print(error_msg)
            bot.send_message(error_msg)

if __name__ == "__main__":
    main()
