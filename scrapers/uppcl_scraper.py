import os
import re
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
            page = browser.new_page()
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"Attempt {attempt + 1}: Navigating to {self.url}...")
                    page.goto(self.url, timeout=30000)
                    page.wait_for_load_state('networkidle')
                    
                    # 1. Select District
                    print(f"Selecting district: {district}...")
                    page.locator("mat-select[name='discomSelect']").click()
                    page.get_by_text(district, exact=True).click()
                    
                    # Wait a bit for DISCOM to auto-populate
                    page.wait_for_timeout(1500)
                    
                    # 2. Enter Account Number
                    print(f"Entering account number: {account_no}...")
                    page.fill("input#kno", account_no)
                    
                    # 3. Handle Captcha
                    print("Capturing CAPTCHA image...")
                    # The captcha is inside a canvas with id 'captcha'
                    captcha_img_locator = page.locator("canvas#captcha").first 
                    
                    captcha_path = "output/temp_captcha.png"
                    os.makedirs("output", exist_ok=True)
                    
                    # Wait for captcha to load
                    page.wait_for_selector("canvas#captcha", state="visible")
                    page.wait_for_timeout(1000) # Give it an extra second to render
                    
                    captcha_img_locator.screenshot(path=captcha_path)
                    
                    answer = self.solve_captcha(captcha_path)
                    if not answer:
                        print("Failed to solve captcha. Retrying...")
                        continue
                        
                    print(f"Solved Captcha Answer: {answer}")
                    page.fill("input#captchaInput", answer)
                    
                    # 4. Click View Button
                    print("Submitting form...")
                    page.locator("button.btn-prim:has-text('View')").click()
                    
                    # 5. Wait for result or error
                    # Check if error message appeared (captcha failed, invalid account, etc.)
                    try:
                        error_msg = page.locator("simple-snack-bar, .error-message").text_content(timeout=5000)
                        if error_msg:
                            print(f"Portal Error: {error_msg.strip()}")
                            if "captcha" in error_msg.lower():
                                print("Captcha was wrong. Retrying...")
                                continue
                    except PlaywrightTimeoutError:
                        pass # No error message appeared, good
                    
                    # Extract Balance
                    print("Looking for balance...")
                    try:
                        # Find the label "Prepaid Meter Balance" and get its parent's full text
                        parent_element = page.locator("text='Prepaid Meter Balance'").locator("xpath=..")
                        
                        if not parent_element.is_visible():
                            # Alternative fallback
                            parent_element = page.locator(".bill-info-val").locator("xpath=..")
                            
                        balance_text = parent_element.text_content(timeout=10000)
                    except PlaywrightTimeoutError:
                        print("Timeout waiting for balance element to appear on the page.")
                        # Dump some of the dom to see what happened
                        print("Page content snapshot: ", page.locator("body").inner_text()[:500])
                        raise Exception("Balance element not found")
                        
                    print(f"Raw parent text extracted: {balance_text}")
                    
                    # Clean up and parse to float (we want the amount, which might have commas)
                    # For example "Prepaid Meter Balance ₹ 342.48"
                    # We reverse find the decimal number to avoid date or account numbers if any.
                    matches = re.findall(r'[\d\,]+\.\d{2}', balance_text)
                    if matches:
                        # Usually the last monetary value is the balance
                        balance_val = float(matches[-1].replace(',', ''))
                        print(f"Parsed Balance: {balance_val}")
                        browser.close()
                        return balance_val
                    else:
                        print(f"Could not find a valid number format (e.g., 123.45) in: {balance_text}")
                        # Fallback parsing just any digits
                        match = re.search(r'(\d+)', balance_text)
                        if match:
                             balance_val = float(match.group(1))
                             print(f"Parsed Fallback Balance: {balance_val}")
                             browser.close()
                             return balance_val
                        else:
                             print("Could not find any digits at all.")
                        
                except Exception as e:
                    print(f"An error occurred during attempt {attempt + 1}: {e}")
                    
            browser.close()
            raise Exception("Failed to scrape balance after maximum retries.")

if __name__ == "__main__":
    # Test block
    # You need Tesseract installed!
    scraper = UPPCLScraper(headless=False)
    # try running scraper.get_remaining_balance('Unnao', 'MVVNL', '4102342000')
