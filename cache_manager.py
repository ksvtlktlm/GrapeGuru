import json
import hashlib


def get_wine_cache_key(wine_name):
    """"Создает уникальный ключ по названию вина."""
    return hashlib.md5(wine_name.encode()).hexdigest()


def load_cached_wine(wine_name):
    """Загружает данные о вине из кэш-файла JSON, если они существуют."""
    cache_key = get_wine_cache_key(wine_name)
    try:
        with open("wine_cache.json", "r") as f:
            cache = json.load(f)
            return cache.get(cache_key)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_to_cache(wine_name, data):
    """Сохраняет данные о вине в кэш-файл JSON для последующего быстрого доступа."""
    cache_key = get_wine_cache_key(wine_name)
    try:
        with open("wine_cache.json", "r") as f:
            cache = json.load(f) # Попытка загрузить кэш
    except (FileNotFoundError, json.JSONDecodeError):
        cache = {}

    cache[cache_key] = data
    with open("wine_cache.json", "w") as f:
        json.dump(cache, f, indent=2)

