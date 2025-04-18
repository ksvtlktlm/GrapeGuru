from glossary import WINE_GLOSSARY, REGION_TRANSLATIONS


IGNORED_TRANSLATION_KEYS = {
    "Rating",
    "Image",
    "Alcohol content",
    "Wine description"
}


def normalize_region_name(region):
    """Корректирует отображение региона для целевой аудитории."""
    region = region.strip()
    if "Ukraine / Crimea" in region or "Ukraine / Крим" in region:
        return "Крым"
    if "Crimea" in region and "Ukraine" in region:
        return "Крым"
    if "Крим" in region and "Україна" in region:
        return "Крым"

    if "Cava" in region:
        parts = region.split(" / ")
        parts = [part for part in parts if part.strip().lower() != "cava"]
        if not parts:
            return "Каталония"
        region = " / ".join(parts)

    parts = region.split(" / ")
    translated_parts = [REGION_TRANSLATIONS.get(part.strip(), part.strip()) for part in parts]
    return " / ".join(translated_parts)

def translate_wine_data(wine_data):
    """Переводит все поля винного словаря на русский язык"""
    if not wine_data or not isinstance(wine_data, dict):
        return wine_data

    translated_wine_info = {}

    for key, value in wine_data.items():
        translated_key = WINE_GLOSSARY.get(key, key)
        if isinstance(value, dict):
            translated_inner = translate_wine_data(value)
            if translated_key == "Basic Info" and isinstance(translated_inner, dict):
                if "Регион" in translated_inner:
                    translated_inner["Регион"] = normalize_region_name(translated_inner["Регион"])
                if "Wine description" in translated_inner:
                    del translated_inner["Wine description"]
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
                    if key not in IGNORED_TRANSLATION_KEYS:
                        untranslated_entry = f"{key} :: {value}"
                        with open("untranslated_log.txt", "a", encoding="utf-8") as log_file:
                            log_file.write(untranslated_entry + "\n")
                    translated_wine_info[translated_key] = value

    return translated_wine_info

