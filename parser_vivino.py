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
        options = get_chrome_options(headless=headless)
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

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.page_load_strategy = 'eager'
    return options


def save_cookies(driver, path="cookies.pkl"):
    """Сохраняет куки в файл с обработкой ошибок"""
    try:
        cookies = driver.get_cookies()
        if not cookies:
            print("Нет куки для сохранения")
            return False

        with open(path, "wb") as file:
            pickle.dump(driver.get_cookies(), file)
        print("Куки сохранены")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Ошибка сохранения куки: {e}")
        return False


def load_cookies(driver, path="cookies.pkl"):
    """Загружает куки из файла."""
    if not os.path.exists(path):
        print("Файл куки не найден")
        return False

    try:
        with open(path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                if "name" in cookie and "value" in cookie:
                    driver.add_cookie(cookie)
        print("Куки загружены")
        return True
    except Exception as e:
        print(f"Ошибка загрузки куки: {e}")
        return False


def accept_and_save_cookies(driver, cookie_path="cookies.pkl"):
    """Принимает куки и сохраняет их в файл."""
    try:
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

        print("Куки приняты и окно закрыто")
        save_cookies(driver, path=cookie_path)
        return True

    except TimeoutException:
        print("Окно куки не появилось — возможно, уже принято")
        return True
    except Exception as e:
        print(f"Ошибка при принятии куки: {e}")
        return False


def setup_cookies(driver, cookie_path="cookies.pkl"):
    """
    Основная функция — загружает куки, если есть. Если нет — принимает и сохраняет.
    """
    if not load_cookies(driver, cookie_path):
        print("Пробуем принять новые куки...")
        accept_and_save_cookies(driver, cookie_path)
    else:
        driver.refresh()


def save_html_with_scroll(wine_name, url, driver, headless=False, folder="cached_pages", max_scroll_attempts=5):
    """
    Прокручивает страницу с помощью Selenium, сохраняет HTML и возвращает путь к файлу.
    Если файл уже существует — повторно не загружает.
    """
    os.makedirs(folder, exist_ok=True)
    safe_name = re.sub(r'[\\/*?:"<>|]', "_", wine_name.strip())
    file_path = os.path.join(folder, f"{safe_name}.html")

    if os.path.exists(file_path):
        print(f"Страница уже сохранена: {file_path}")
        return file_path

    try:
        driver.set_page_load_timeout(30)
        driver.get(url)

        if not driver.get_cookies():  # Если cookies пустые
            load_cookies(driver)
            driver.refresh()  # Обновление страницы для активации куки
            if not driver.get_cookies():
                print("Предупреждение: Cookies не загрузились после refresh")

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

        print(f"HTML-страница сохранена: {file_path}")
        return file_path

    except TimeoutException:
        print(f"[Timeout] Не удалось загрузить страницу: {url}")
        return None

    except Exception as e:
        print(f"[Error] Ошибка при обработке {url}: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)  # Удаление неполного файла
        return None


def search_vivino(wine_name, driver, attempts=5, search_timeout=40):
    """
    Ищет вино на сайте Vivino по названию и возвращает ссылку на его страницу.
    Принимает уже созданный экземпляр Selenium WebDriver.
    """
    SEARCH_INPUT_SELECTOR = "input[name='q']"

    for attempt in range(1, attempts + 1):
        print(f"Попытка {attempt}/{attempts} поиска '{wine_name}'")
        try:
            driver.set_page_load_timeout(15)
            driver.get("https://www.vivino.com/")

            search_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_SELECTOR)),
                message=f"Не найдено поле поиска за 10 сек (попытка {attempt})")

            for char in wine_name:  # Имитация ввода человеком
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            time.sleep(1)
            search_box.send_keys(Keys.RETURN)
            print("Название вина отправлено в поиск")


            WebDriverWait(driver, search_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-vintage]")), message=f"Не удалось найти вино за {attempt} попыток.")

            vintage_id = driver.find_element(By.CSS_SELECTOR, "div[data-vintage]").get_attribute("data-vintage")
            wine_url = f"https://www.vivino.com/wines/{vintage_id}"

            print(f"Успешно найдено вино: {wine_url}")
            return wine_url

        except TimeoutException as e:
            print(f"Таймаут при поиске: {str(e)}")
        except NoSuchElementException as e:
            print(f"Элемент не найден: {str(e)}")
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Неожиданная ошибка: {error_msg}")
            page_source = driver.page_source.lower()
            if any(x in page_source for x in ["cloudflare", "captcha", "access denied"]):
                print("Обнаружена система защиты - требуется ручное вмешательство")
                break
            elif "bot" in error_msg or "blocked" in error_msg:
                print("Заблокировано антибот-системой")
                break

    print(f"Поиск не удался после {attempts} попыток")
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
                print(f"Ошибка обработки строки '{key}': {str(e)}")
                continue

    except Exception as e:
        print(f"Ошибка парсинга таблицы: {str(e)}")
        return {"Ошибка": str(e)}

    return result if result else {"Данные": "Не найдены"}


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


# def get_wine_tasting_notes(url, driver, headless=False):
#     """Парсинг вкусовых нот с прокруткой карусели, возвращает топ-4 группы с поднотами."""
#     driver.get(url)
#     accept_cookies(driver)
#
#     slider_container = driver.find_element(By.XPATH,
#                                            "//div[starts-with(@class, 'tasteCharacteristics')]//div[starts-with(@class, 'slider__slider')]")
#
#     actions = ActionChains(driver)
#     actions.move_to_element(slider_container).perform()
#
#     notes_dict = {}
#     while True:
#         cards = slider_container.find_elements(By.XPATH, ".//div[contains(@class, 'col mobile-column-6')]")
#         for card in cards:
#             try:
#                 group_name_el = card.find_element(By.XPATH, ".//span[contains(@class, 'tasteNote__flavorGroup')]")
#                 group_name = group_name_el.text.strip()  # Название группы нот
#                 total_mentions_el = card.find_element(By.XPATH, ".//div[contains(@class, 'tasteNote__mentions')]")
#                 total_mentions = int(total_mentions_el.text.split()[0])  # Общее кол-во упоминаний группы нот
#
#                 subnotes_button = card.find_element(By.XPATH, ".//button[contains(@class, 'card__card')]")
#                 subnotes_button.click()
#                 try:
#                     modal_window = WebDriverWait(driver, 5).until(
#                         EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'baseModal')]"))
#                     )
#                     time.sleep(1)
#                     note_elements = modal_window.find_elements(By.XPATH,
#                                                                ".//div[contains(@class, 'noteTag__name')]")
#                     note_names = [el.text.strip() for el in note_elements][:3]
#                     close_button = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Close')]")
#                     close_button.click()
#                     time.sleep(1)
#
#                     notes_dict[group_name] = {"mentions": total_mentions, "notes": note_names}
#                     top_notes = dict(sorted(notes_dict.items(), key=lambda x: x[1]["mentions"], reverse=True)[:4])
#
#                 except Exception as e:
#                     print(f"Ошибка при работе с поднотами: {e}")
#
#             except:
#                 continue
#         try:
#             next_button = slider_container.find_element(By.XPATH, ".//div[contains(@class, 'slider__right')]")
#             next_button.click()
#             time.sleep(1)
#         except:
#             print("Просмотрены все карточки.")
#             return top_notes


start_time = time.perf_counter()
wine_info = {}
wine_name = "De Los Abuelos"
with setup_driver() as driver:
    try:
        driver.get("https://www.vivino.com/")
        setup_cookies(driver)
        wine_url = search_vivino(wine_name, driver)
        if not wine_url:
            raise Exception("Не удалось найти URL вина")

        file_path = save_html_with_scroll(wine_name, wine_url, driver=driver)
        if not file_path:
            raise Exception("Не удалось сохранить страницу")

        save_cookies(driver)

        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "lxml")
            wine_info.update({
                "Basic Info": get_basic_info(soup)
                # "Rating": get_rating(soup),
                # "Food Pairing": get_food_pairing(soup),
                # "Taste Profile": get_taste_profile(soup),
                # "Image": get_wine_image(soup),
                # "Notes": get_wine_tasting_notes(wine_url, driver)
            })
    except Exception as e:
        print(f"Ошибка при выполнении: {str(e)}")
        try:
            save_cookies(driver)  # Резервное сохранение при ошибке
        except Exception as e:
            print(f"Ошибка при резервном сохранении куки: {e}")

pprint(wine_info, sort_dicts=False)
print(f"Время выполнения: {time.perf_counter() - start_time:.4f} секунд")
