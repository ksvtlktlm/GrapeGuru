from translatepy import Translator
from parser_vivino import parse_wine
from pprint import pprint


def translate_wine_data(wine_data):
    """Переводит все поля винного словаря на русский язык"""
    if not wine_data or not isinstance(wine_data, dict):
        return wine_data

    translator = Translator()
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
    "Mostly light, but with a slight tendency": "Скорее лёгкое, но с небольшим уклоном",
    "A bit closer to light, but almost balanced": "Ближе к лёгкому, но почти сбалансированное",
    "Completely bold": "Абсолютно насыщенное",
    "Mostly bold, pronounced": "Ярко выраженное насыщенное",
    "Slightly bold, but still moderate": "Умеренно насыщенное",

    # Dry - Sweet (Сухое — Сладкое)
    "Completely dry": "Абсолютно сухое",
    "Mostly dry, but with a slight tendency": "Преимущественно сухое с легкой сладостью",
    "A bit closer to dry, but almost balanced": "Ближе к сухому, но почти сбалансированное",
    "Completely sweet": "Абсолютно сладкое",
    "Mostly sweet, pronounced": "Ярко выраженное сладкое",
    "Slightly sweet, but still moderate": "Умеренно сладкое",

    # Soft - Acidic (Мягкое — Кислотное)
    "Completely soft": "Абсолютно мягкое",
    "Mostly soft, but with a slight tendency": "Преимущественно мягкое с легкой кислотностью",
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

    "Balanced": "Сбалансированное",

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

    # Дубовые ноты
    "oak": "дуб",
    "vanilla": "ваниль",
    "cedar": "кедр",
    "cigar box": "сигарная коробка",
    "hickory": "гикори (ореховое дерево)",
    "wood smoke": "древесный дым",
    "tobacco": "табак",
    "sweet tobacco": "сладкий табак",
    "cigar": "сигара",
    "chocolate": "шоколад",
    "dark chocolate": "тёмный шоколад",
    "milk chocolate": "молочный шоколад",
    "mocha": "мокко",
    "fudge": "помадка",
    "butterscotch": "ириска",
    "coffee": "кофе",
    "espresso": "эспрессо",
    "clove": "гвоздика",
    "nutmeg": "мускатный орех",
    "allspice": "душистый перец",
    "baking spice": "выпечные специи",
    "camphor": "камфара",
    "dill": "укроп",
    "caramel": "карамель",
    "toffee": "ириска",
    "butter": "сливочность",
    "coconut": "кокос",
    "cola": "кола",


# Тёмные фрукты
    "plum": "слива",
    "dark fruit": "тёмные фрукты",
    "blackberry": "ежевика",
    "ripe blackberry": "спелая ежевика",
    "bramble": "ежевика (дикая)",
    "black plum": "чёрная слива",
    "blueberry": "черника",
    "bilberry": "черника (лесная)",
    "boysenberry": "бойзенова ягода",
    "mulberry": "шелковица",
    "black cherry": "чёрная вишня",
    "blackcurrant": "чёрная смородина",
    "cassis": "кассис (чёрная смородина)",
    "jam": "джем/варенье",
    "berry sauce": "ягодный соус",
    "acai berry": "ягода асаи",

    # Красные фрукты
    "cherry": "вишня",
    "raspberry": "малина",
    "strawberry": "клубника",
    "watermelon": "арбуз",
    "cherry cola": "вишнёвая кола",
    "red cherry": "красная вишня",
    "bing cherry": "вишня Бинг",
    "morello cherry": "вишня морелло",
    "sour cherry": "кислая вишня",
    "cherry syrup": "вишнёвый сироп",
    "ripe strawberry": "спелая клубника",
    "red currant": "красная смородина",
    "cranberry": "клюква",
    "red plum": "красная слива",

    # Деревенские/землистые ноты
    "leather": "кожа",
    "smoke": "дым",
    "honey": "мёд",
    "forest floor": "лесная подстилка",
    "mushroom": "грибы",
    "truffle": "трюфель",
    "potting soil": "парниковая земля",
    "underbrush": "подлесок",
    "chalk": "мел",
    "minerals": "минеральные ноты",
    "flint": "кремень",
    "stone": "камень",
    "ash": "пепел",
    "graphite": "графит",
    "game": "дичь",
    "cured meat": "вяленое мясо",
    "barbecue meat": "мясо с гриля",
    "roasted meat": "жареное мясо",
    "grilled meat": "мясо на гриле",
    "pastrami": "пастрами",
    "barbecue smoke": "дым от барбекю",
    "tar": "дёготь",
    "tobacco leaf": "табачный лист",
    "balsamic": "бальзамический",
    "exotic spice": "экзотические специи",
    "charcoal": "древесный уголь",
    "cocoa": "какао",
    "pencil shavings": "стружка карандаша",
    "pencil lead": "грифель карандаша",
    "salt": "соль",

    # Плодовые
    "peach": "персик",
    "melon": "дыня",
    "apricot": "абрикос",
    "apple": "яблоко",
    "green apple": "зелёное яблоко",
    "yellow apple": "жёлтое яблоко",
    "baked apple": "печёное яблоко",
    "bruised apple": "подгнившее яблоко",
    "pear": "груша",
    "asian pear": "азиатская груша",
    "white peach": "белый персик",
    "yellow peach": "жёлтый персик",
    "nectarine": "нектарин",
    "stewed apricot": "томлёный абрикос",
    "apricot jam": "абрикосовый джем",
    "stone fruit": "косточковые фрукты",
    "yellow plum": "жёлтая слива",
    "mirabelle plum": "мирабель",
    "quince": "айва",

    # Цитрусовые ноты
    "grapefruit": "грейпфрут",
    "lemon": "лимон",
    "lime": "лайм",
    "lime zest": "цедра лайма",
    "orange": "апельсин",
    "tangerine": "мандарин",

    # Ноты выдержки
    "brioche": "бриошь",
    "toast": "тост",
    "nutty": "ореховые ноты",
    "almond": "миндаль",
    "toasted almond": "жареный миндаль",
    "roasted almond": "жареный миндаль",
    "biscuit": "бисквит",
    "hazelnut": "фундук",
    "roasted hazelnut": "жареный фундук",
    "marzipan": "марципан",
    "walnut": "грецкий орех",
    "toasted nuts": "жареные орехи",
    "brown sugar": "коричневый сахар",
    "burnt sugar": "жжёный сахар",
    "chestnut": "каштан",
    "pecan": "пекан",
    "peanut": "арахис",
    "graham cracker": "грахем крекер",
    "maple syrup": "кленовый сироп",

    # Пряные ноты
    "licorice": "солодка",
    "black licorice": "чёрная солодка",
    "pepper": "перец",
    "white pepper": "белый перец",
    "cracked pepper": "молотый перец",
    "cinnamon": "корица",
    "dried herbs": "сушёные травы",
    "mint": "мята",
    "menthol": "ментол",
    "savory": "чабер",
    "eucalyptus": "эвкалипт",
    "anise": "анис",
    "thyme": "тимьян",
    "gingerbread": "имбирный пряник",
    "5-spice powder": "смесь 5 специй",
    "juniper": "можжевельник",
    "oregano": "орегано",
    "rosemary": "розмарин",
    "sage": "шалфей",

    # Зеленые тона
    "straw": "солома",
    "gooseberry": "крыжовник",
    "chard": "листовая свёкла",
    "grass": "трава",
    "fresh-cut grass": "свежескошенная трава",
    "hay": "сено",
    "asparagus": "спаржа",
    "bitter almond": "горький миндаль",
    "tomato": "помидор",
    "rhubarb": "ревень",

    # Цветочные ноты
    "elderflower": "бузина",
    "honeysuckle": "жимолость",
    "orange blossom": "цветок апельсина",
    "acacia": "акация",
    "jasmine": "жасмин",
    "apple blossom": "цветение яблони",
    "chamomile": "ромашка",
    "dried flowers": "сушеные цветы",
    "perfume": "парфюмерные ноты",
    "lily": "лилия",
    "violet": "фиалка",

    # Дрожжевые ноты
    "cream": "сливки",
    "yeast": "дрожжи",
    "cheese": "сыр",

    # Тропические ноты
    "pineapple": "ананас",
    "green pineapple": "зелёный ананас",
    "mango": "манго",
    "lychee": "личи",
    "passion fruit": "маракуйя",
    "guava": "гуава",
    "kiwi": "киви",
    "papaya": "папайя",
    "starfruit": "карамбола",

    # Сухофрукты
    "raisin": "изюм",
    "fig": "инжир",
    "prune": "чернослив",
    "black raisin": "чёрный изюм",
    "dried apricot": "курага",
    "dried cranberry": "сушёная клюква",
    "fruitcake": "фруктовый кекс",

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
    "Game (deer, venison)": "Дичь",
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

    # Сорта винограда
    # Международные сорта
    "Cabernet Sauvignon": "Каберне Совиньон",
    "Merlot": "Мерло",
    "Pinot Noir": "Пино Нуар",
    "Syrah": "Сира",
    "Shiraz": "Шираз",
    "Grenache": "Гренаш",
    "Sangiovese": "Санджовезе",
    "Tempranillo": "Темпранильо",
    "Malbec": "Мальбек",
    "Carmenere": "Карменер",
    "Zinfandel": "Зинфандель",
    "Petit Verdot": "Пти Вердо",
    "Cabernet Franc": "Каберне Фран",
    "Barbera": "Барбера",
    "Nebbiolo": "Неббиоло",
    "Mourvèdre": "Мурведр",
    "Gamay": "Гамэ",

    # Белые сорта
    "Chardonnay": "Шардоне",
    "Sauvignon Blanc": "Совиньон Блан",
    "Riesling": "Рислинг",
    "Pinot Gris": "Пино Гри",
    "Pinot Grigio": "Пино Гриджио",
    "Gewürztraminer": "Гевюрцтраминер",
    "Viognier": "Вионье",
    "Chenin Blanc": "Шенен Блан",
    "Semillon": "Семильон",
    "Muscat": "Мускат",
    "Albariño": "Альбариньо",
    "Vermentino": "Верментино",
    "Grüner Veltliner": "Грюнер Вельтлинер",

    # Региональные/местные сорта
    "Furmint": "Фурминт",
    "Blaufränkisch": "Блауфранкиш",
    "Kékfrankos": "Кекфранкош",
    "Kadarka": "Кадарка",
    "Plavac Mali": "Плавац Мали",
    "Vranac": "Вранац",
    "Saperavi": "Саперави",
    "Rkatsiteli": "Ркацители",
    "Mtsvane": "Мцване",
    "Kisi": "Киси",
    "Aglianico": "Альянико",
    "Nero d'Avola": "Неро д'Авола",
    "Xinomavro": "Ксиномавро",
    "Assyrtiko": "Асиртико",
    "Moschofilero": "Москофилера",
    "Mavrodaphne": "Мавродафни",

    # Игристые вина
    "Macabeo": "Макабео",
    "Parellada": "Парельяда",
    "Xarel-lo": "Шарелло",

    # Португальские сорта
    "Touriga Nacional": "Турига Насьональ",
    "Tinta Roriz": "Тинта Рориш",
    "Baga": "Бага",
    "Vinhão": "Виньян",

    # Русские/постсоветские
    "Krasnostop": "Красностоп",
    "Tsimlyansky": "Цимлянский",
    "Siberian": "Сибирский",
    "Dostoyny": "Достойный",

    # Гибридные сорта
    "Regent": "Регент",
    "Cabernet Cortis": "Каберне Кортис",
    "Solaris": "Соларис",

    # Редкие/автохтонные
    "Tannat": "Таннат",
    "Graciano": "Грасиано",
    "Cinsault": "Сенсо",
    "Carignan": "Кариньян",
    "Marselan": "Марселан",
    "Petit Manseng": "Пти Мансенг",
    "Gros Manseng": "Гро Мансенг",
    "Poulsard": "Пульсар",
    "Trousseau": "Труссо",
    "Savagnin": "Саваньен",

    # Дополнительные белые
    "Fiano": "Фьяно",
    "Greco": "Греко",
    "Falanghina": "Фалангина",
    "Pecorino": "Пекорино",
    "Arneis": "Арнеис",
    "Cortese": "Кортезе",
    "Erbaluce": "Эрбалуче",
    "Garganega": "Гарганега",
    "Trebbiano": "Треббьяно",
    "Verdicchio": "Вердиккио",

    # Дополнительные красные
    "Montepulciano": "Монтепульчано",
    "Lagrein": "Лагрейн",
    "Teroldego": "Терольдего",
    "Schiava": "Скьява",
    "Dolcetto": "Дольчетто",
    "Freisa": "Фрейза",
    "Pelaverga": "Пелаверга",
    "Rossese": "Россезе",
    "Corvina": "Корвина",
    "Rondinella": "Рондинелла",
    "Molinaro": "Молинара",
    "Negroamaro": "Негроамаро",
    "Primitivo": "Примитиво",
    "Uva di Troia": "Ува ди Троя",
    "Bombino Nero": "Бомбино Неро",
    "Gaglioppo": "Гальоппо",
    "Magliocco": "Мальокко",
    "Nerello Mascalese": "Нерелло Маскалезе",
    "Nerello Cappuccio": "Нерелло Каппуччо",
    "Frappato": "Фраппато",
    "Perricone": "Периконе",
    "Susumaniello": "Сусуманиелло",
    "Bovale": "Бовале",
    "Cannonau": "Каннонау",
    "Carricante": "Карриканте",
    "Catarratto": "Катарратто",
    "Inzolia": "Инзолия",
    "Minnella": "Миннелла",
    "Nerello": "Нерелло",
    "Nocera": "Ночера",
    "Zibibbo": "Зибиббо",

    "Monastrell": "Монастрель",
    "Shiraz/Syrah": "Сира/Шираз"
}

wine_info = parse_wine("Grano a Grano Graciano", headless=False)
translated_wine_info = translate_wine_data(wine_info)
# pprint(wine_info, sort_dicts=False)
pprint(translated_wine_info, sort_dicts=False)