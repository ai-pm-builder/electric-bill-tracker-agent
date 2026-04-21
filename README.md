# UPPCL Daily Tracker Setup

I have created all the necessary files for your agent! 
Because this agent uses OCR (Optical Character Recognition) to automatically bypass the CAPTCHA, there is one system dependency you must install manually, and a few credentials you need to provide.

## Step 1: Install Tesseract OCR (Required for Captcha)
1. Download the Tesseract-OCR installer for Windows from here: [UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer. Note the installation path (usually `C:\Program Files\Tesseract-OCR`).
3. Add the installation folder to your Windows `PATH` environment variable.
   *(Or, edit `scrapers/uppcl_scraper.py` and uncomment the `pytesseract.pytesseract.tesseract_cmd` line and set the correct path).*

## Step 2: Configure Credentials
1. Rename `.env.example` to `.env`.
2. Open `.env` and fill in your:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `UPPCL_ACCOUNT_1_DISTRICT` (e.g., Unnao)
   - `UPPCL_ACCOUNT_1_DISCOM` (e.g., MVVNL)
   - `UPPCL_ACCOUNT_1_NUMBER`

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
