from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from urllib.parse import urlparse

class PageChecker:
    def __init__(self, base_url):
        self.base_url = base_url
        self.driver = webdriver.Chrome()  # veya webdriver.Firefox(), webdriver.Edge() vb. seçeneği tercih edebilirsiniz

    def wait_for_page_load(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            print("Sayfa yüklenemedi.")

    def find_broken_links(self):
        self.driver.get(self.base_url)
        self.wait_for_page_load()

        links = self.driver.find_elements_by_tag_name("a")
        for link in links:
            href = link.get_attribute("href")
            if href:
                self.check_link(href)

    def check_link(self, url):
        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ['http', 'https']:
                print(f"Izin verilmeyen bağlantı: {url}")
                return

            response = requests.head(url, allow_redirects=True)
            if response.status_code == 404:
                print(f"Bozuk sayfa bulundu: {url}")

        except requests.RequestException as e:
            print(f"Hata: {url} erişilemedi: {str(e)}")

    def close_driver(self):
        self.driver.quit()

def main():
    base_url = "url.com"
    
    page_checker = PageChecker(base_url)
    page_checker.find_broken_links()
    page_checker.close_driver()

if __name__ == "__main__":
    main()
