import concurrent.futures
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class PageChecker:
    def __init__(self, base_url):
        self.base_url = base_url
        try:
            self.driver = webdriver.Chrome()  # Gelecekte farklı tarayıcı kullanmak isterseniz burayı değiştirebilirsiniz.
        except WebDriverException as e:
            print(f"WebDriver başlatılamadı: {str(e)}")
            raise

    def wait_for_page_load(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            print("Sayfa yüklenemedi.")

    def find_broken_links(self):
        try:
            self.driver.get(self.base_url)
            self.wait_for_page_load()
            links = self.driver.find_elements(By.TAG_NAME, "a")
            hrefs = [link.get_attribute("href") for link in links if link.get_attribute("href")]

            # Bağlantıları paralel olarak kontrol etmek için ThreadPoolExecutor kullanıyoruz
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.check_link, href) for href in hrefs]
                for future in concurrent.futures.as_completed(futures):
                    future.result()  # Her bir görev bittiğinde sonucu alır

        except NoSuchElementException as e:
            print(f"Element bulunamadı: {str(e)}")
        except WebDriverException as e:
            print(f"Tarayıcı hatası: {str(e)}")
        finally:
            self.close_driver()

    def check_link(self, url):
        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ['http', 'https']:
                print(f"İzin verilmeyen bağlantı: {url}")
                return

            response = requests.get(url, timeout=5, allow_redirects=True)
            if response.status_code == 404:
                print(f"Bozuk sayfa bulundu: {url}")
            elif response.status_code >= 400:
                print(f"Hata durumu: {url} - {response.status_code}")
            else:
                print(f"Geçerli sayfa: {url}")

        except requests.RequestException as e:
            print(f"Hata: {url} erişilemedi: {str(e)}")

    def close_driver(self):
        try:
            self.driver.quit()
        except WebDriverException as e:
            print(f"Tarayıcı kapatılamadı: {str(e)}")

def main():
    base_url = "https://www.example.com"
    page_checker = PageChecker(base_url)
    page_checker.find_broken_links()

if __name__ == "__main__":
    main()
