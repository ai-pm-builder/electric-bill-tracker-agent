# UPPCL Daily Tracker Setup

This agent uses a lightweight, built-in AI (ONNX) to automatically bypass the CAPTCHA and fetch your electricity bill. No heavy external OCR engines are required!

## Step 1: Configure Credentials
1. Rename `.env.example` to `.env`.
2. Open `.env` and fill in your:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID` *(Optional: If you don't know it, just leave it blank or dummy text. The script will auto-discover it!)*
   - `UPPCL_ACCOUNT_1_DISTRICT` 
   - `UPPCL_ACCOUNT_1_DISCOM` 
   - `UPPCL_ACCOUNT_1_NUMBER`

## Step 2: Initialize Telegram
Telegram bots **cannot** send you messages until you message them first. 
Open the Telegram app, search for your bot, and send it a quick message (like "Hello"). Our script will automatically detect this message and find your Chat ID.

## Step 3: Test the Scraper
To test if it works natively on your machine, open a terminal in this folder and run:
```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

## Step 4: Setup Daily Schedule
Once the test works, simply run the PowerShell script I provided to set up the daily task:
1. Right-click `setup_scheduler.ps1` and select **Run with PowerShell**.
   *(Note: You will need to edit this script slightly to point `$Action = New-ScheduledTaskAction -Execute "python_executable_path_here"` to the python.exe inside your `.venv\Scripts\` folder).*
