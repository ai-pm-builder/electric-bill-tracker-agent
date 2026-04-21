# ⚡ Autonomous Electric Bill Tracking Agent

## Overview

This project is an **Autonomous Agent** designed to help you track your daily electricity consumption and spending effortlessly. It automatically checks the Smart Meter portal everyday, retrieves your latest pre-paid smart meter balance, calculates your daily electricity spend, and sends a summarized report directly to your Telegram.

### Why use this Agent?
- **AI-Powered CAPTCHA Solver:** This agent uses a lightweight, built-in AI (ONNX model) to automatically solve the CAPTCHA locally on your machine—no expensive external OCR APIs required!
- **Daily Spend Tracking:** It calculates exactly how much you spent on electricity by fetching yesterday's balance and doing the math.
- **Automated Telegram Alerts:** Delivers your daily balance and spend right to your phone so you never have to manually log in to the portal again.
- **Flexible Execution:** Run it manually on your machine, schedule it via Windows Task Scheduler, OR deploy it 100% free to the cloud using **GitHub Actions**.

## Getting Started

### Local Setup (Windows/Mac)
If you want to run this directly on your own computer:

1. Open a terminal and run:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   playwright install chromium
   ```
2. Rename `.env.example` to `.env` and fill in your electric account details and Telegram details.
   *(Note: The script can auto-discover your Telegram Chat ID automatically if you send a message to your bot first!)*
3. To run it once, execute `python main.py`.

### Cloud Deployment (GitHub Actions + Google Sheets)
Because GitHub Actions servers are wiped clean after every run, you cannot store your local `.csv` file there. To run this completely headlessly in the cloud, we use **Google Sheets** as a database!

#### 1. Setup Google Sheets
1. Create a blank Google Sheet and note the `GOOGLE_SHEET_ID` from the URL.
2. Go to the [Google Cloud Console](https://console.cloud.google.com/), create a project, and enable the **Google Sheets API** and **Google Drive API**.
3. Create a **Service Account** and generate a JSON Key file.
4. **Share** your Google Sheet with the Service Account email address as an Editor.
5. Copy the entire raw JSON text from your key file—this will be your `GOOGLE_CREDENTIALS`.

#### 2. Configure GitHub Secrets
Go to your **Private GitHub Repository** -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**.

Add ALL the following secrets:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID` (*Optional*)
- `UPPCL_ACCOUNT_1_DISTRICT`
- `UPPCL_ACCOUNT_1_DISCOM`
- `UPPCL_ACCOUNT_1_NUMBER`
- `GOOGLE_SHEET_ID`
- `GOOGLE_CREDENTIALS` (Paste the absolute raw JSON string here)

#### 3. Run it!
Once your secrets are set in GitHub, the bot will automatically run every single morning at **9:00 AM IST**! 
You can manually trigger a run immediately by going to the **Actions** tab -> **UPPCL Daily Tracker** -> **Run workflow**.

---
**Disclaimer:** This tool is an independent personal assistant to help track your own meter's usage. It is not affiliated with or endorsed by any organisation.
