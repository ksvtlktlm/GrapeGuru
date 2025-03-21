import time
import re
from pprint import pprint
import random
import os

from bs4 import BeautifulSoup
import requests
import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


CHROME_DRIVER_PATH = ChromeDriverManager().install()
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.234 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1",
]


def get_chrome_options(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    return options


def setup_driver(headless=False):
    service = Service(CHROME_DRIVER_PATH)
    options = get_chrome_options(headless)
    return webdriver.Chrome(service=service, options=options)


def search_vivino(wine_name, attempts=5):
    for attempt in range(1, attempts + 1):
        print(f"Попытка {attempt} поиска вина '{wine_name}'")
        try:
            with setup_driver(headless=False) as driver:
                driver.get("https://www.vivino.com/")

                try:
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")) # Принятие куки
                    ).click()
                    print("Куки приняты")
                except:
                    print("Нет кнопки согласия на куки или уже приняты")

                search_box = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.TAG_NAME, "input"))
                )
                time.sleep(random.randint(2, 5))
                search_box.send_keys(wine_name) # Название вина вводится в поиск
                time.sleep(random.randint(1, 3))
                search_box.send_keys(Keys.RETURN)
                print("Название вина отправлено в поиск")

                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "wine-card__content"))
                )
                print("Вино обнаружено")

                time.sleep(random.randint(1, 3))
                first_wine = driver.find_element(By.CLASS_NAME, "wine-card__content")
                wine_url = first_wine.find_element(By.TAG_NAME, "a").get_attribute("href") # URL первого найденного вина
                return wine_url

        except Exception as e:
            print(f"Ошибка при попытке {attempt}: {e}")
            time.sleep(random.randint(3, 5))

    print("Не удалось получить ссылку на вино после всех попыток.")
    return None