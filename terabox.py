from playwright.sync_api import sync_playwright

def get_direct_link(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_selector('a[href*="https://download"]', timeout=15000)
        download_link = page.get_attribute('a[href*="https://download"]', 'href')
        browser.close()
        if not download_link:
            raise Exception("No direct link found. TeraBox layout may have changed.")
        return download_link
