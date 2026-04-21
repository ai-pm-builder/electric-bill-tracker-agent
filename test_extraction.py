import ddddocr, re
from playwright.sync_api import sync_playwright

def get_html():
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
    
    page.locator('canvas#captcha').first.screenshot(path='output/test_captcha.png')
    ocr = ddddocr.DdddOcr(show_ad=False, old=True)
    text = ocr.classification(open('output/test_captcha.png', 'rb').read())
    match = re.search(r'(\d+)\s*[\+\*x]\s*(\d+)', text)
    if not match:
        print("Failed to OCR captcha")
        return
    ans = str(int(match.group(1)) + int(match.group(2)))
    page.fill('input#captchaInput', ans)
    
    page.locator("button.btn-prim:has-text('View')").click()
    page.wait_for_timeout(10000) # wait long time for data to load
    
    import codecs
    codecs.open('output/result_page.html', 'w', 'utf-8').write(page.content())
    browser.close()
    p.stop()
    print("Done dumping HTML.")

if __name__ == "__main__":
    get_html()
