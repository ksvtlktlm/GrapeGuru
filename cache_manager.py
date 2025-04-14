import json
import hashlib


def get_wine_cache_key(brand, name):
    """Создает уникальный ключ по бренду и названию вина."""
    key_str = f"{brand.strip().lower()}::{name.strip().lower()}"
    return hashlib.md5(key_str.encode()).hexdigest()


def load_cached_wine(brand, name):
    """Загружает данные о вине из кэш-файла JSON, если они существуют."""
    cache_key = get_wine_cache_key(brand, name)
    try:
        with open("wine_cache.json", "r") as f:
            cache = json.load(f)
            return cache.get(cache_key)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_to_cache(brand, name, data):
    """Сохраняет данные о вине в кэш-файл JSON для последующего быстрого доступа."""
    cache_key = get_wine_cache_key(brand, name)
    try:
        with open("wine_cache.json", "r") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        cache = {}

    cache[cache_key] = data
    with open("wine_cache.json", "w") as f:
        json.dump(cache, f, indent=2)

