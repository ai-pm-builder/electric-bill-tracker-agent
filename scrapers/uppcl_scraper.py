import os
import re
import time
from PIL import Image
import ddddocr
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class UPPCLScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.url = "https://consumer.uppcl.org/wss/smart_bill_pay_home"
        self.ocr = ddddocr.DdddOcr(show_ad=False, old=True)

    def solve_captcha(self, image_path: str) -> str:
        """Reads a math captcha (e.g., '12 + 5 =') from an image and solves it."""
        try:
            with open(image_path, 'rb') as f:
                img_bytes = f.read()
            
            text = self.ocr.classification(img_bytes)
            text = text.strip()
            print(f"OCR extracted text: '{text}'")
            
            # Parse the math equation
            match = re.search(r'(\d+)\s*[\+\*x]\s*(\d+)', text) 
            if match:
                num1 = int(match.group(1))
                num2 = int(match.group(2))
                return str(num1 + num2)
            else:
                print("Could not parse math from OCR result.")
                return ""
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    def get_remaining_balance(self, district: str, discom: str, account_no: str) -> float:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            
            max_retries = 3
            for attempt in range(max_retries):
                # Create a fresh context and page on every attempt
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                
                try:
                    print(f"Attempt {attempt + 1}: Navigating to {self.url}...")
                    page.goto(self.url, wait_until='domcontentloaded', timeout=60000)
                    
                    # Wait explicitly for 3 seconds after load
                    print("Page loaded. Waiting for 3 seconds to let scripts initialize...")
                    time.sleep(3)
                    
                    # 1. Select District
                    print(f"Selecting district: {district}...")
                    page.wait_for_selector("mat-select[name='discomSelect']", state="visible", timeout=20000)
                    page.locator("mat-select[name='discomSelect']").click(delay=150)
                    time.sleep(1) # Human pause
                    page.get_by_text(district, exact=True).click(delay=100)
                    
                    # Wait a bit for DISCOM to auto-populate
                    time.sleep(2)
                    
                    # 2. Enter Account Number (Human-like typing)
                    print(f"Entering account number: {account_no}...")
                    page.locator("input#kno").press_sequentially(account_no, delay=150)
                    time.sleep(1)
                    
                    # 3. Handle Captcha
                    print("Capturing CAPTCHA image...")
                    captcha_img_locator = page.locator("canvas#captcha").first 
                    
                    captcha_path = "output/temp_captcha.png"
                    os.makedirs("output", exist_ok=True)
                    
                    page.wait_for_selector("canvas#captcha", state="visible")
                    time.sleep(1.5) # Let captcha fully draw
                    
                    captcha_img_locator.screenshot(path=captcha_path)
                    
                    answer = self.solve_captcha(captcha_path)
                    if not answer:
                        print("Failed to solve captcha. Retrying...")
                        context.close()
                        time.sleep(5)
                        continue
                        
                    print(f"Solved Captcha Answer: {answer}")
                    page.locator("input#captchaInput").press_sequentially(answer, delay=200)
                    
                    time.sleep(1) # Pause before clicking View
                    
                    # 4. Click View Button
                    print("Submitting form...")
                    page.locator("button.btn-prim:has-text('View')").click(delay=250)
                    
                    # 5. Wait for result or error
                    print("Form submitted. Waiting for 10 seconds for the processing to finish...")
                    time.sleep(10) # As requested, wait 10s because processing takes time
                    
                    # Check if error message appeared (captcha failed, invalid account, etc.)
                    try:
                        error_msg = page.locator("simple-snack-bar, .error-message").text_content(timeout=5000)
                        if error_msg:
                            print(f"Portal Error: {error_msg.strip()}")
                            if "captcha" in error_msg.lower() or "invalid" in error_msg.lower() or "wrong" in error_msg.lower():
                                print("Captcha or input error. Retrying...")
                                context.close()
                                time.sleep(5)
                                continue
                    except PlaywrightTimeoutError:
                        pass # No simple error toast appeared
                    
                    # Save a debug screenshot of the results page
                    page.screenshot(path="output/last_result_page.png")
                    
                    # Extract Balance
                    print("Looking for balance...")
                    try:
                        parent_element = page.locator("text='Prepaid Meter Balance'").locator("xpath=..")
                        
                        if not parent_element.is_visible():
                            parent_element = page.locator(".bill-info-val").locator("xpath=..")
                            
                        balance_text = parent_element.text_content(timeout=10000)
                    except PlaywrightTimeoutError:
                        print("Timeout waiting for balance element.")
                        print("Page content snippet: ", page.locator("body").inner_text()[:500])
                        raise Exception("Balance element not found")
                        
                    print(f"Raw parent text extracted: {balance_text}")
                    
                    # Parsing (supports negative balances e.g. -1,234.56)
                    matches = re.findall(r'-?\s*[\d\,]+\.\d{2}', balance_text)
                    if matches:
                        raw = matches[-1].replace(',', '').replace(' ', '')
                        balance_val = float(raw)
                        print(f"Parsed Balance: {balance_val}")
                        context.close()
                        browser.close()
                        return balance_val
                    else:
                        print(f"Could not find standard number format in: {balance_text}")
                        match = re.search(r'(-?\s*\d+)', balance_text)
                        if match:
                             raw = match.group(1).replace(' ', '')
                             balance_val = float(raw)
                             print(f"Parsed Fallback Balance: {balance_val}")
                             context.close()
                             browser.close()
                             return balance_val
                        else:
                             print("Could not find any digits.")
                             raise Exception("No digits parsing successful.")
                             
                except Exception as e:
                    print(f"An error occurred during attempt {attempt + 1}: {e}")
                    context.close()
                    time.sleep(5) # backoff before trying again
                    
            browser.close()
            raise Exception("Failed to scrape balance after maximum retries.")

if __name__ == "__main__":
    # Test block
    # You need Tesseract installed!
    scraper = UPPCLScraper(headless=False)
    # try running scraper.get_remaining_balance('Unnao', 'MVVNL', '4102342000')
