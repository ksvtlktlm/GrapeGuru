from googletrans import Translator
import json
from parser_vivino import parse_wine



translator = Translator()


def translate_text(text, dest_lang='ru'):
    try:
        return translator.translate(text, dest=dest_lang).text
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Возвращаем оригинал, если перевод не удался


def format_for_telegram(wine):
    brand = translate_text(wine['Brand'])
    name = translate_text(wine['Name'])
    wine_type = translate_text(wine['Type'])
    rating = wine['Rating']



if __name__ == "__main__":
    wine = parse_wine("Château Margaux", headless=True)
    message = format_for_telegram(wine)
    print(message)

