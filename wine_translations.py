from translatepy import Translator
from parser_vivino import parse_wine
from glossary import WINE_GLOSSARY
from pprint import pprint


def normalize_region_name(region):
    """Корректирует отображение региона для целевой аудитории."""
    region = region.strip()
    if "Ukraine / Crimea" in region or "Ukraine / Крим" in region:
        return "Крым"
    if "Crimea" in region and "Ukraine" in region:
        return "Крым"
    if "Крим" in region and "Україна" in region:
        return "Крым"
    return region

def translate_wine_data(wine_data):
    """Переводит все поля винного словаря на русский язык"""
    if not wine_data or not isinstance(wine_data, dict):
        return wine_data

    translator = Translator()
    translated_wine_info = {}

    for key, value in wine_data.items():
        translated_key = WINE_GLOSSARY.get(key, key)
        if isinstance(value, dict):
            translated_inner = translate_wine_data(value)
            if translated_key == "Basic Info" and isinstance(translated_inner, dict):
                if "Регион" in translated_inner:
                    translated_inner["Регион"] = normalize_region_name(translated_inner["Регион"])
            translated_wine_info[translated_key] = translated_inner

        elif isinstance(value, list):
            translated_wine_info[translated_key] = [
                WINE_GLOSSARY.get(item, item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            if translated_key in ("Brand", "Name", "Винодельня"):
                translated_wine_info[translated_key] = value
            else:
                translated = WINE_GLOSSARY.get(value, None)
                if translated:
                    translated_wine_info[translated_key] = translated
                else:
                    try:
                        translated_wine_info[translated_key] = translator.translate(value)
                    except Exception as e:
                        translated_wine_info[translated_key] = value

    return translated_wine_info



wine_info = parse_wine("Массандра Мускат белый красного камня", headless=False)
translated_wine_info = translate_wine_data(wine_info)
# pprint(wine_info, sort_dicts=False)
pprint(translated_wine_info, sort_dicts=False)