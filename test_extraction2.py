import ddddocr, re
from playwright.sync_api import sync_playwright

def test():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://consumer.uppcl.org/wss/smart_bill_pay_home')
    
    page.locator("mat-select[name='discomSelect']").click()
    page.get_by_text('Unnao', exact=True).click()
    page.wait_for_timeout(1500)
    
    page.fill('input#kno', '4102342000')
    page.wait_for_selector('canvas#captcha', state='visible')
    page.wait_for_timeout(1000)
    
    page.locator('canvas#captcha').first.screenshot(path='output/test_captcha2.png')
    ocr = ddddocr.DdddOcr(show_ad=False, old=True)
    text = ocr.classification(open('output/test_captcha2.png', 'rb').read())
    match = re.search(r'(\d+)\s*[\+\*x]\s*(\d+)', text)
    if match:
        ans = str(int(match.group(1)) + int(match.group(2)))
        page.fill('input#captchaInput', ans)
        page.locator("button.btn-prim:has-text('View')").click()
        
        try:
            page.wait_for_selector("text='Prepaid Meter Balance'", timeout=10000)
            element = page.locator("text='Prepaid Meter Balance'").first
            parent = element.locator("xpath=..")
            print("--- PARENT HTML ---")
            print(parent.inner_html())
            print("--- GRANDPARENT HTML ---")
            print(parent.locator("xpath=..").inner_html())
        except Exception as e:
            print(f"Error: {e}")
            print(page.locator("simple-snack-bar, .error-message").text_content(timeout=2000))
    browser.close()
    p.stop()

if __name__ == "__main__":
    test()
