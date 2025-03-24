import time
import re
from pprint import pprint
import random
import os
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pickle


if not os.path.exists("chromedriver"):
    CHROME_DRIVER_PATH = ChromeDriverManager().install()
else:
    CHROME_DRIVER_PATH = "./chromedriver"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.234 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1",
]


def setup_driver(headless=False):
    """Создаёт и настраивает экземпляр Selenium WebDriver для Chrome."""
    try:
        service = Service(CHROME_DRIVER_PATH)
        options = get_chrome_options()
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(5)
        return driver

    except Exception as e:
        print(f"Ошибка инициализации драйвера: {str(e)}")
        raise


def get_chrome_options(headless=False, disable_js=False, disable_images=True):
    """Создаёт и настраивает объект ChromeOptions для Selenium WebDriver."""
    options = Options()
    base_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--start-maximized",
        f"user-agent={random.choice(USER_AGENTS)}"
    ]

    if headless:
        options.add_argument("--headless=new")
    if disable_js:
        options.add_argument("--disable-javascript")

    for arg in base_args:
        options.add_argument(arg)

    prefs = {}
    if disable_images:
        prefs["profile.managed_default_content_settings.images"] = 2

    if prefs:
        options.add_experimental_option("prefs", prefs)

    options.page_load_strategy = 'eager'
    return options


def save_cookies(driver, path="cookies.pkl"):
    """Сохраняет куки"""
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver, path="cookies.pkl"):
    """Загружает куки"""
    try:
        with open(path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("Cookies загружены")
    except FileNotFoundError:
        print("Файл cookies не найден")


def accept_cookies(driver):
    """Принимает куки, если кнопка есть."""
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))  # Принятие куки
        ).click()
        save_cookies(driver)
        print("Куки приняты и сохранены")
    except Exception as e:
        print(f"Ошибка при принятии куки: {e}")


def save_html_with_scroll(wine_name, url, driver, headless=False, folder="cached_pages"):
    """
    Прокручивает страницу с помощью Selenium, сохраняет HTML и возвращает путь к файлу.
    Если файл уже существует — повторно не загружает.
    """
    os.makedirs(folder, exist_ok=True)
    safe_name = wine_name.strip().replace(" ", "_").replace("/", "_")
    file_path = os.path.join(folder, f"{safe_name}.html")

    if os.path.exists(file_path):
        print(f"Страница уже сохранена: {file_path}")
        return file_path

    try:
        driver.get(url)
        load_cookies(driver)
        accept_cookies(driver)

        # Скроллинг до конца страницы
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        page_source = driver.page_source  # Полная html страница

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(page_source)

        print(f"HTML-страница сохранена: {file_path}")
        return file_path

    except Exception as e:
        print(f"Ошибка при сохранении страницы с прокруткой: {e}")
        return None


def search_vivino(wine_name, driver, attempts=5):
    """
    Ищет вино на сайте Vivino по названию и возвращает ссылку на его страницу.
    Принимает уже созданный экземпляр Selenium WebDriver.
    """
    for attempt in range(1, attempts + 1):
        print(f"Попытка {attempt} поиска вина '{wine_name}'")
        try:
            driver.get("https://www.vivino.com/")
            accept_cookies(driver)

            search_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.TAG_NAME, "input")))
            time.sleep(random.randint(2, 5))
            search_box.send_keys(wine_name)  # Название вина вводится в поиск
            time.sleep(random.randint(1, 3))
            search_box.send_keys(Keys.RETURN)
            print("Название вина отправлено в поиск")

            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".wine-card__content a"))
                )
                print("Вино обнаружено")

                first_wine = driver.find_element(By.CSS_SELECTOR, ".wine-card__content a")
                wine_url = first_wine.get_attribute("href")
                return wine_url

            except Exception as e:
                print(f"Не удалось найти карточку с вином: {e}")
                driver.refresh()
                continue

        except Exception as e:
            print(f"Ошибка при попытке {attempt}: {e}")
            driver.refresh()
            time.sleep(random.randint(3, 5))

    print("Не удалось получить ссылку на вино после всех попыток.")
    return None


def get_basic_info(soup):
    """Парсинг основных характеристик вина (винодельня, виноград, регион и т. д.)"""
    info = {}
    try:
        table = soup.find("table")
        rows = table.find_all("tr") if table else []

        for r in rows:
            try:
                key = r.find("span", class_=re.compile(r"^wineFacts__headerLabel")).text
                values = [el.text.strip() for el in r.find_all("a")]
                if not values:
                    values = [r.find("td").text.strip()]
                    info[key] = values if len(values) > 1 else values[0]
            except AttributeError:
                print(f"Ошибка парсинга строки: {r}")

    except Exception as e:
        print(f"Ошибка при парсинге основных данных: {e}")

    return info if info else {"Данные": "Не найдены"}


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


def get_taste_profile(soup):
    """Парсинг вкусового профиля вина"""
    taste_profile = {}
    try:
        taste_table = soup.find("table", class_=re.compile(r"^tasteStructure"))
        rows = taste_table.find_all("tr", class_=re.compile(r"^tasteStructure__")) if taste_table else []

        for row in rows:
            try:
                td_tags = row.find_all("td")
                left_label = td_tags[0].text.strip()
                right_label = td_tags[-1].text.strip()

                progress_span = td_tags[1].find("span", class_=re.compile(r"^indicatorBar__progress"))
                if progress_span:
                    style = progress_span.get("style", "")
                    style_values = {
                        prop.split(":")[0].strip(): prop.split(":")[1].strip().replace("%", "").replace("px", "")
                        for prop in style.split(";") if ":" in prop}

                    width = float(style_values.get("width", 0))
                    left = float(style_values.get("left", 50))

                    position = left + (width / 2)

                    char_name = f"{left_label} - {right_label}"
                    if position <= 10:
                        result = f"Полностью {left_label} ({round(position, 1)}%)"
                    elif position <= 30:
                        result = f"Скорее {left_label}, но с лёгким уклоном ({round(position, 1)}%)"
                    elif position <= 45:
                        result = f"Чуть ближе к {left_label}, но почти сбалансировано ({round(position, 1)}%)"
                    elif position <= 55:
                        result = "Сбалансированное"
                    elif position <= 70:
                        result = f"Немного {right_label}, но ещё умеренно ({round(position, 1)}%)"
                    elif position <= 90:
                        result = f"Скорее {right_label}, выраженное ({round(position, 1)}%)"
                    else:
                        result = f"Полностью {right_label} ({round(position, 1)}%)"

                    taste_profile[char_name] = result

            except Exception as e:
                print(f"Ошибка при обработке характеристики вкуса: {e}")

    except Exception as e:
        print(f"Ошибка при парсинге вкусового профиля: {e}")

    return taste_profile if taste_profile else "Не найден"


def get_wine_image(soup):
    """Парсинг изображения вина"""
    try:
        img_container = soup.find("picture", class_=re.compile(r"^wineLabel-module__picture"))
        img_url = img_container.next.get("srcset").split(",")[0]
        return img_url if img_url else "Изображение не найдено"
    except Exception as e:
        print(f"Ошибка при парсинге изображения: {e}")
        print("Ошибка получения изображения", e)


def get_wine_tasting_notes(url, driver, headless=False):
    """Парсинг вкусовых нот с прокруткой карусели, возвращает топ-4 группы с поднотами."""
    driver.get(url)
    accept_cookies(driver)

    slider_container = driver.find_element(By.XPATH,
                                           "//div[starts-with(@class, 'tasteCharacteristics')]//div[starts-with(@class, 'slider__slider')]")

    actions = ActionChains(driver)
    actions.move_to_element(slider_container).perform()

    notes_dict = {}
    while True:
        cards = slider_container.find_elements(By.XPATH, ".//div[contains(@class, 'col mobile-column-6')]")
        for card in cards:
            try:
                group_name_el = card.find_element(By.XPATH, ".//span[contains(@class, 'tasteNote__flavorGroup')]")
                group_name = group_name_el.text.strip()  # Название группы нот
                total_mentions_el = card.find_element(By.XPATH, ".//div[contains(@class, 'tasteNote__mentions')]")
                total_mentions = int(total_mentions_el.text.split()[0])  # Общее кол-во упоминаний группы нот

                subnotes_button = card.find_element(By.XPATH, ".//button[contains(@class, 'card__card')]")
                subnotes_button.click()
                try:
                    modal_window = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'baseModal')]"))
                    )
                    time.sleep(1)
                    note_elements = modal_window.find_elements(By.XPATH,
                                                               ".//div[contains(@class, 'noteTag__name')]")
                    note_names = [el.text.strip() for el in note_elements][:3]
                    close_button = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Close')]")
                    close_button.click()
                    time.sleep(1)

                    notes_dict[group_name] = {"mentions": total_mentions, "notes": note_names}
                    top_notes = dict(sorted(notes_dict.items(), key=lambda x: x[1]["mentions"], reverse=True)[:4])

                except Exception as e:
                    print(f"Ошибка при работе с поднотами: {e}")

            except:
                continue
        try:
            next_button = slider_container.find_element(By.XPATH, ".//div[contains(@class, 'slider__right')]")
            next_button.click()
            time.sleep(1)
        except:
            print("Просмотрены все карточки.")
            return top_notes


start_time = time.perf_counter()
wine_info = {}
wine_name = "La Rioja Alta"
with setup_driver() as driver:
    try:
        load_cookies(driver)
        driver.get("https://www.vivino.com/")
        if not driver.get_cookies():
            accept_cookies(driver)
            save_cookies(driver)
        wine_url = search_vivino(wine_name, driver)
        if not wine_url:
            raise Exception("Не удалось найти URL вина")
        file_path = save_html_with_scroll(wine_name, wine_url, driver=driver)
        if not file_path:
            raise Exception("Не удалось сохранить страницу")
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "lxml")
            wine_info.update({
                "Basic Info": get_basic_info(soup),
                "Rating": get_rating(soup),
                "Food Pairing": get_food_pairing(soup),
                "Taste Profile": get_taste_profile(soup),
                "Image": get_wine_image(soup),
                "Notes": get_wine_tasting_notes(wine_url, driver)})
    except Exception as e:
        print(f"Ошибка при выполнении: {str(e)}")

    finally:
        save_cookies(driver)
        driver.quit()

pprint(wine_info, sort_dicts=False)
print(f"Время выполнения: {time.perf_counter() - start_time:.4f} секунд")
