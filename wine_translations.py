from parser_vivino import parse_wine
from pprint import pprint


def translate_wine_data(wine_data):
    """Переводит все поля винного словаря на русский язык"""
    if not wine_data or not isinstance(wine_data, dict):
        return wine_data

    translated_wine_info = {}
    for key, value in wine_data.items():
        translated_key = WINE_GLOSSARY.get(key, key)
        if isinstance(value, dict):
            translated_wine_info[translated_key] = translate_wine_data(value)
        elif isinstance(value, list):
            translated_wine_info[translated_key] = [
                WINE_GLOSSARY.get(item, item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            translated_wine_info[translated_key] = WINE_GLOSSARY.get(value, value)


    return translated_wine_info


WINE_GLOSSARY = {
    # Основные термины
    "Red wine": "Красное вино",
    "White wine": "Белое вино",
    "Rosé wine": "Розовое вино",
    "Sparkling wine": "Игристое вино",
    "Dessert wine": "Десертное вино",
    "Fortified Wine": "Креплёное вино",

    # Вкусовой профиль
    "Light - Bold": "Лёгкое — Насыщенное",
    "Smooth - Tannic": "Мягкое — Танинное",
    "Dry - Sweet": "Сухое — Сладкое",
    "Soft - Acidic": "Мягкое — Кислотное",

    # Light - Bold (Лёгкое — Насыщенное)
    "Completely light": "Абсолютно лёгкое",
    "Mostly light, but with a slight tendency": "Преимущественно лёгкое, с небольшим уклоном",
    "A bit closer to light, but almost balanced": "Ближе к лёгкому, но почти сбалансированное",
    "Completely bold": "Абсолютно насыщенное",
    "Mostly bold, pronounced": "Ярко выраженное насыщенное",
    "Slightly bold, but still moderate": "Умеренно насыщенное",

    # Dry - Sweet (Сухое — Сладкое)
    "Completely dry": "Абсолютно сухое",
    "Mostly dry, but with a slight tendency": "Преимущественно сухое, с небольшим уклоном",
    "A bit closer to dry, but almost balanced": "Ближе к сухому, но почти сбалансированное",
    "Completely sweet": "Абсолютно сладкое",
    "Mostly sweet, pronounced": "Ярко выраженное сладкое",
    "Slightly sweet, but still moderate": "Умеренно сладкое",
    "Balanced": "Сбалансированное",

    # Soft - Acidic (Мягкое — Кислотное)
    "Completely soft": "Абсолютно мягкое",
    "Mostly soft, but with a slight tendency": "Преимущественно мягкое, с небольшим уклоном",
    "A bit closer to soft, but almost balanced": "Ближе к мягкому, но почти сбалансированное",
    "Completely acidic": "Ярко выраженное кислотное",
    "Mostly acidic, pronounced": "Преимущественно кислотное",
    "Slightly acidic, but still moderate": "Умеренно кислотное",

    # Smooth - Tannic (Мягкое — Танинное)
    "Completely smooth": "Исключительно мягкое",
    "Mostly smooth, but with a slight tendency": "Преимущественно мягкое, с лёгкой танинностью",
    "A bit closer to smooth, but almost balanced": "Ближе к мягкому, но с заметными танинами",
    "Completely tannic": "Очень танинное",
    "Mostly tannic, pronounced": "Ярко выраженное танинное",
    "Slightly tannic, but still moderate": "Умеренно танинное",

    # Ноты
    "oaky": "Дубовые ноты",
    "black fruit": "Тёмные фрукты",
    "red fruit": "Красные фрукты",
    "tree fruit": "Фруктовые ноты",
    "citrus": "Цитрусовые ноты",
    "earthy": "Землистые ноты",
    "spices": "Пряные ноты",
    "dried fruit": "Сухофрукты",
    "floral": "Цветочные ноты",
    "yeasty": "Дрожжевые ноты",
    "tropical": "Экзотические ноты",
    "vegetal": "Зеленые тона",
    "ageing notes": "Ноты выдержки",

    # Аллергены
    "Contains sulfites": "Содержит сульфиты",
    "Contains sulfites, egg allergens, milk allergens": "Содержит сульфиты, аллергены яиц и молока",

    #Базовая информация
    "Winery": "Винодельня",
    "Grapes": "Сорт винограда",
    "Region": "Регион",
    "Wine style": "Стиль вина",
    "Alcohol content": "Крепость",
    "Allergens": "Аллергены",

    # Гастрономические сочетания
    "Pork": "Свинина",
    "Beef": "Говядина",
    "Lamb": "Баранина",
    "Game (deer, venison)": "Мясо охотничьих животных",
    "Cured Meat": "Вяленое мясо",
    "Poultry": "Птица",
    "Shellfish": "Моллюски",
    "Lean fish": "Постная рыба",
    "Vegetarian": "Вегетарианские блюда",
    "Pasta": "Паста",
    "Appetizers and snacks": "Закуски",
    "Aperitif": "Аперитив",
    "Venison": "Оленина",
    "Deer": "Оленина",
}

wine_info = parse_wine("cabernet", headless=False)
translated_wine_info = translate_wine_data(wine_info)
# pprint(wine_info, sort_dicts=False)
pprint(translated_wine_info, sort_dicts=False)