# cookie_collector.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time

def get_cookies_from_site(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30) # more than 30 seconds will result in a timeout

    try:
        driver.get(url)
        time.sleep(5) # for the site to fully load
        cookies = driver.get_cookies()
    except Exception as e:
        print(f"Error loading {url}: {e}")
        cookies = []
    finally:
        driver.quit()
        
    return cookies