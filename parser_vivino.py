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


def save_html_page(wine_name, wine_url, folder="cached_pages"):
    """
    Сохраняет HTML-страницу локально, чтобы избежать повторных запросов.
    :param wine_name: Название вина (используется для имени файла)
    :param wine_url: URL страницы вина на Vivino
    :param folder: Папка, куда сохранять HTML
    """
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{wine_name.replace(' ', '_')}.html")

    if os.path.exists(file_path):
        print(f"Страница уже сохранена: {file_path}")
        return file_path

    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(url=wine_url, headers=headers, timeout=10)
        response.raise_for_status()  # Проверка, нет ли ошибки запроса

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)

        print(f"HTML-страница сохранена: {file_path}")
        return file_path

    except Exception as e:
        print(f"Ошибка при сохранении страницы: {e}")
        return None


def get_basic_info(soup):
    """Парсинг основных характеристик вина (винодельня, виноград, регион и т. д.)"""
    wine_info = {}
    try:
        table = soup.find("table")
        rows = table.find_all("tr") if table else []

        for r in rows:
            try:
                key = r.find("span", class_=re.compile(r"^wineFacts__headerLabel")).text
                values = [el.text.strip() for el in r.find_all("a")]
                if not values:
                    values = [r.find("td").text.strip()]
                wine_info[key] = values if len(values) > 1 else values[0]
            except AttributeError:
                print(f"Ошибка парсинга строки: {r}")

    except Exception as e:
        print(f"Ошибка при парсинге основных данных: {e}")

    return wine_info if wine_info else {"Данные": "Не найдены"}


def get_rating(soup):
    """Парсинг рейтинга вина"""
    try:
        rating = float(soup.find("div", class_=re.compile(r"^vivinoRating_averageValue")).text)
        return rating if rating else "Рейтинг не найден"
    except AttributeError:
        print("Рейтинг не найден")
        return "Рейтинг не найден"


def get_food_pairing(soup):
    """Парсинг подходящих блюд"""
    try:
        food_container = soup.find("div", class_=re.compile(r"^foodPairing__foodContainer"))
        if food_container:
            foods = [el.text.strip() for el in food_container.find_all("div") if el.text]
            return foods if foods else "Подходящие блюда не указаны."
        return "Подходящие блюда не указаны."
    except Exception as e:
        print(f"Ошибка при парсинге еды: {e}")
        return "Ошибка при получении информации о еде"


wine_name = "6 Anime Puglia"
wine_url = search_vivino(wine_name)
if wine_url:
    file_path = save_html_page(wine_name, wine_url)
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "lxml")
        wine_info = {}
        wine_info.update(get_basic_info(soup)) # Основная информация
        wine_info["Rating"] = get_rating(soup) # Рейтинг
        wine_info["Food Pairing"] = get_food_pairing(soup)  # Сочетаемая еда

pprint(wine_info, sort_dicts=False)
