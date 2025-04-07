import time
import re
from pprint import pprint
import random
import os
import logging


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from cache_manager import load_cached_wine, save_to_cache


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
        options = get_chrome_options(headless=headless)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(5)
        return driver

    except Exception as e:
        logging.error(f"Ошибка инициализации драйвера: {str(e)}")
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

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.page_load_strategy = 'eager'
    return options


def accept_cookies(driver):
    """Принимает куки."""
    try:
        WebDriverWait(driver, 20).until(lambda d: "vivino.com" in d.current_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.didomi-popup-container"))
        )

        agree_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#didomi-notice-agree-button"))
        )

        try:
            agree_button.click()
        except:
            driver.execute_script("arguments[0].click();", agree_button)

        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.didomi-popup-container"))
        )

        logging.info("Куки приняты и окно закрыто")
        return True

    except TimeoutException:
        logging.warning("Окно куки не появилось — возможно, уже принято")
        return True
    except Exception as e:
        logging.error(f"Ошибка при принятии куки: {e}")
        return False


def save_html_with_scroll(wine_name, url, driver, headless=False, folder="cached_pages", max_scroll_attempts=5):
    """
    Прокручивает страницу с помощью Selenium, сохраняет HTML и возвращает путь к файлу.
    Если файл уже существует — повторно не загружает.
    """
    os.makedirs(folder, exist_ok=True)
    safe_name = re.sub(r'[\\/*?:"<>|]', "_", wine_name.strip())
    file_path = os.path.join(folder, f"{safe_name}.html")

    if os.path.exists(file_path):
        logging.warning(f"Страница уже сохранена: {file_path}")
        return file_path

    try:
        driver.set_page_load_timeout(30)
        driver.get(url)

        # Скроллинг до конца страницы
        scroll_attempt = 0
        last_height = driver.execute_script("return document.body.scrollHeight")
        while scroll_attempt < max_scroll_attempts:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1 + random.random())
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

            last_height = new_height
            scroll_attempt += 1

        page_source = driver.page_source  # Полная html страница
        if not page_source or len(page_source) < 500:  # Минимальный размер
            raise ValueError("Получен пустой или слишком маленький HTML")

        with open(file_path, "w", encoding="utf-8", errors="replace") as file:
            file.write(page_source)

        logging.info(f"HTML-страница сохранена: {file_path}")
        return file_path

    except TimeoutException:
        logging.error(f"[Timeout] Не удалось загрузить страницу: {url}")
        return None

    except Exception as e:
        logging.error(f"[Error] Ошибка при обработке {url}: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)  # Удаление неполного файла
        return None


def search_vivino(wine_name, driver, fallback_on_fail=True, search_timeout=40, headless=False):
    """
    Ищет вино на сайте Vivino по названию и возвращает ссылку на его страницу.
    Использует переданный драйвер, а при неудаче — временный драйвер (если разрешено).
    """
    SEARCH_INPUT_SELECTOR = "input[name='q']"

    def try_search(drv):
        try:
            # drv.set_page_load_timeout(15)
            time.sleep(random.uniform(1, 3))

            if "access denied" in drv.page_source.lower():
                raise Exception("Обнаружена страница блокировки")

            # accept_cookies(drv)
            search_box = WebDriverWait(drv, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_SELECTOR)))

            for char in wine_name:  # Имитация ввода человеком
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            time.sleep(1)
            search_box.send_keys(Keys.RETURN)
            logging.info("Название вина отправлено в поиск")

            time.sleep(random.uniform(1, 3))

            if "access denied" in drv.page_source.lower():
                raise Exception("Обнаружена страница блокировки")

            try:
                no_result_el = WebDriverWait(drv, 3).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//div[contains(@class, 'noResultsMessage')]"
                    ))
                )
                logging.warning("Ни одного вина не найдено!")
                return "NO_RESULTS"

            except TimeoutException:
                pass

            for i in range(0, drv.execute_script("return document.body.scrollHeight"), 300):
                drv.execute_script(f"window.scrollTo(0, {i});")
                time.sleep(0.2)

            drv.execute_script("window.scrollTo(0, 0);")

            WebDriverWait(drv, search_timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-vintage]")))

            vintage_el = WebDriverWait(drv, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-vintage]"))
            )
            vintage_id = vintage_el.get_attribute("data-vintage")
            wine_url = f"https://www.vivino.com/wines/{vintage_id}"
            logging.info(f"Успешно найдено вино: {wine_url}")
            return wine_url

        except Exception as e:
            logging.error(f"Ошибка при поиске: {e}")
            return None

    logging.info(f"Попытка 1 поиска '{wine_name}' через основной драйвер")
    wine_url = try_search(driver)

    if wine_url == "NO_RESULTS":
        return None, driver

    if wine_url:
        return wine_url, driver

    if fallback_on_fail:
        logging.info("Перезапуск драйвера после неудачной попытки...")

        try:
            driver.quit()
            temp_driver = setup_driver(headless=headless)
            time.sleep(2)
            temp_driver.get("https://www.vivino.com/")
            accept_cookies(temp_driver)
            wine_url = try_search(temp_driver)
            return wine_url, temp_driver
        except Exception as e:
            logging.error(f"Ошибка при использовании временного драйвера: {e}")
            return None, None

    logging.error("Не удалось найти вино ни с основным, ни с временным драйвером.")
    return None


def get_basic_info(soup):
    """Парсинг основных характеристик вина (винодельня, виноград, регион и т. д.)"""
    result = {}
    try:
        table = soup.find("table", class_=lambda x: x and x.startswith("wineFacts__wineFacts"))
        if not table:
            return {"Данные": "Не найдены"}

        for row in table.find_all("tr", attrs={"data-testid": "wineFactRow"}):
            try:
                # Извлечение ключа (названия характеристики)
                key_span = row.find("span", class_=lambda x: x and x.startswith("wineFacts__headerLabel"))
                if not key_span:
                    continue

                key = key_span.get_text(strip=True)
                if not key:
                    continue

                # Извлечение значения
                value_cell = row.find("td", class_=lambda x: x and x.startswith("wineFacts__fact"))
                if not value_cell:
                    result[key] = None
                    continue

                # Обработка составных значений (регионы, виноград)
                links = value_cell.find_all("a")
                if links:
                    if len(links) > 1:
                        result[key] = [l.get_text(strip=True) for l in links] if key == "Grapes" else " / ".join(
                            l.get_text(strip=True) for l in links)
                    else:
                        result[key] = links[0].get_text(strip=True)
                else:
                    # Обработка простого текста (Alcohol, Allergens и т.д.)
                    text = value_cell.get_text(" ", strip=True)
                    result[key] = text if text else None

            except Exception as e:
                logging.error(f"Ошибка обработки строки '{key}': {str(e)}")
                continue

    except Exception as e:
        logging.error(f"Ошибка парсинга таблицы: {str(e)}")
        return {"Ошибка": str(e)}

    return result if result else {"Данные": "Не найдены"}


def get_rating(soup):
    """Парсит рейтинг вина с обработкой ошибок.
       Возвращает float или None при ошибке."""
    try:
        rating = float(soup.find("div", class_=re.compile(r"^vivinoRating_averageValue")).text)
        return rating if rating else "Рейтинг не найден"
    except AttributeError:
        logging.error("Рейтинг не найден")
        return "Рейтинг не найден"


def get_food_pairing(soup):
    """Парсит подходящие блюда"""
    try:
        food_container = soup.find("div", class_=re.compile(r"^foodPairing__foodContainer"))
        if food_container:
            foods = [el.text.strip() for el in food_container.find_all("div") if el.text]
            return foods if foods else "Подходящие блюда не указаны."
        return "Подходящие блюда не указаны."
    except Exception as e:
        logging.error(f"Ошибка при парсинге еды: {e}")
        return "Ошибка при получении информации о еде"


def get_taste_profile(soup):
    """Парсит вкусовой профиль вина"""
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
                        result = f"Completely {str.lower(left_label)} ({round(position, 1)}%)"
                    elif position <= 30:
                        result = f"Mostly {str.lower(left_label)}, but with a slight tendency ({round(position, 1)}%)"
                    elif position <= 45:
                        result = f"A bit closer to {str.lower(left_label)}, but almost balanced ({round(position, 1)}%)"
                    elif position <= 55:
                        result = "Balanced"
                    elif position <= 70:
                        result = f"Slightly {str.lower(right_label)}, but still moderate ({round(position, 1)}%)"
                    elif position <= 90:
                        result = f"Mostly {str.lower(right_label)}, pronounced ({round(position, 1)}%)"
                    else:
                        result = f"Completely {str.lower(right_label)} ({round(position, 1)}%)"

                    taste_profile[char_name] = result

            except Exception as e:
                logging.error(f"Ошибка при обработке характеристики вкуса: {e}")

    except Exception as e:
        logging.error(f"Ошибка при парсинге вкусового профиля: {e}")

    return taste_profile if taste_profile else "Не найден"


def get_wine_image(soup):
    """Парсит изображение вина"""
    try:
        img_container = soup.find("picture", class_=re.compile(r"^wineLabel-module__picture"))
        img_url = img_container.next.get("srcset").split(",")[0]
        return img_url if img_url else "Изображение не найдено"
    except Exception as e:
        logging.error(f"Ошибка при парсинге изображения: {e}")
        return "Ошибка при получении изображения"


def get_wine_type(soup):
    """Парсит тип вина."""
    try:
        wine_type = soup.find("a", attrs={"data-cy": "breadcrumb-winetype"}).text
        return wine_type if wine_type else "Тип вина не найден"
    except Exception as e:
        logging.error(f"Ошибка при парсинге типа вина: {e}")


def get_wine_brand_and_name(soup):
    """Извлекает бренд (производителя) и название вина (включая винтаж, если есть)."""
    DEFAULT_VALUES = ("Не найден", "Не найдено")
    brand, name = DEFAULT_VALUES

    try:
        headline = soup.find("h1")
        if not headline:
            logging.error("Не найден заголовок h1 на странице")
            return DEFAULT_VALUES

        headline_div = headline.find("div", class_=lambda x: x and "wineHeadline" in x)
        if not headline_div:
            logging.error("Не найден блок с названием вина")
            return DEFAULT_VALUES

        brand_element = headline_div.find("a")
        if brand_element:
            brand = brand_element.get_text(strip=True)
            if not brand:
                logging.error("Бренд найден, но текст пустой")
                brand = DEFAULT_VALUES[0]

        full_text = headline_div.get_text(strip=True)
        if not full_text:
            logging.error("Полное название вина не содержит текста")
            return brand, DEFAULT_VALUES[1]

        name = re.sub(rf'^{re.escape(brand)}', '', full_text).strip()
        if not name:
            name = DEFAULT_VALUES[1]

        return brand, name

    except Exception as e:
        logging.error(f"Ошибка при парсинге названия и бренда: {e}")
        return DEFAULT_VALUES


def get_wine_tasting_notes(url, driver, notes_limit=4):
    """Парсит первые 3 видимые вкусовые карточки без прокрутки"""
    try:
        driver.get(url)
        time.sleep(2)

        slider = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//div[starts-with(@class, 'tasteCharacteristics')]//div[starts-with(@class, 'slider__slider')]")))
        actions = ActionChains(driver)
        actions.move_to_element(slider).perform()

        notes = {}

        cards = slider.find_elements(By.XPATH, ".//div[contains(@class, 'col mobile-column-6')]")
        for card in cards[:3]:
            try:
                group = card.find_element(By.XPATH, ".//span[contains(@class, 'tasteNote__flavorGroup')]").text.strip()
                mentions = int(
                    card.find_element(By.XPATH, ".//div[contains(@class, 'tasteNote__mentions')]").text.split()[0])

                card.find_element(By.XPATH, ".//button[contains(@class, 'card__card')]").click()
                modal = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@id, 'baseModal')]")))
                time.sleep(0.3)
                notes_list = [el.text.strip() for el in
                              modal.find_elements(By.XPATH, ".//div[contains(@class, 'noteTag__name')]")][:3]
                modal.find_element(By.XPATH, "//a[contains(@aria-label, 'Close')]").click()
                time.sleep(0.3)
                notes[group] = {"mentions": mentions, "notes": notes_list}

            except Exception as e:
                logging.error(f"Пропущена карточка: {str(e)}")
                continue

        return dict(sorted(notes.items(),
                           key=lambda x: x[1]["mentions"],
                           reverse=True)[:notes_limit])

    except Exception as e:
        logging.error(f"Ошибка парсинга: {str(e)}")
        return "Не найдены"


def parse_wine(wine_name, headless=False):
    """
    Основная функция парсера:
    - Принимает название вина.
    - Возвращает словарь с данными о вине.
    - Параметр headless управляет режимом браузера (True — без GUI).
    """
    cached_data = load_cached_wine(wine_name)
    if cached_data:
        logging.warning(f"Используются кэшированные данные для {wine_name}")
        return cached_data

    wine_info = {}
    with setup_driver(headless=headless) as driver:
        try:
            driver.get("https://www.vivino.com/")

            accept_cookies(driver)

            wine_url, actual_driver = search_vivino(wine_name, driver, headless=headless)

            if wine_url == "NO_RESULTS":
                actual_driver.quit()
                logging.warning(f"Вино '{wine_name}' не найдено из-за внутренней ошибки. Поиск завершён.")
                return {}

            if not wine_url:
                if actual_driver:
                    actual_driver.quit()
                raise Exception("Не удалось найти URL вина")

            if actual_driver is None:
                raise Exception("Драйвер не инициализирован корректно")

            file_path = save_html_with_scroll(wine_name, wine_url, driver=actual_driver)
            if not file_path:
                raise Exception("Не удалось сохранить страницу")


            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "lxml")
                brand, name = get_wine_brand_and_name(soup)
                wine_info.update({
                    "Brand": brand,
                    "Name": name,
                    "Type": get_wine_type(soup),
                    "Basic Info": get_basic_info(soup),
                    "Rating": get_rating(soup),
                    "Food Pairing": get_food_pairing(soup),
                    "Taste Profile": get_taste_profile(soup),
                    "Image": get_wine_image(soup)
                })

                if actual_driver is None:
                    raise Exception("Невозможно получить tasting notes — драйвер неактивен")

                wine_info["Notes"] = get_wine_tasting_notes(wine_url, actual_driver)

        except Exception as e:
            logging.error(f"Ошибка при парсинге: {str(e)}")

    if wine_info.get("Brand") and wine_info.get("Name"):
        try:
            save_to_cache(wine_name, wine_info)
            logging.info(f"Данные для {wine_name} сохранены в кэш")
        except Exception as e:
            logging.error(f"Ошибка кэширования: {str(e)}")
    else:
        logging.warning(f"Парсинг не удался, данные для {wine_name} не сохранены в кэш")

    return wine_info

"""Для отладки"""
# if __name__ == "__main__":
#     start_time = time.perf_counter()
#     wine_data = parse_wine('крым', headless=True)
#     pprint(wine_data, sort_dicts=False)
#     print(f"Время выполнения: {time.perf_counter() - start_time:.4f} секунд")

