import json
import logging
from parser_vivino import parse_wine


def escape_markdown(text: str) -> str:
    """Экранирует только нужные символы по спецификации Telegram MarkdownV2."""
    if not isinstance(text, str):
        text = str(text)

    to_escape = r'\_*[]()~`>#+-=|{}.!'
    for char in to_escape:
        text = text.replace(char, f'\\{char}')
    return text


def format_wine_markdown(data):
    if not data or not isinstance(data, dict) or all(not v for v in data.values()):
        return "Не удалось найти информацию по данному вину."

    lines = []

    name = data.get("Name")
    if name:
        lines.append(f"*🍷 {escape_markdown(name)}*")

    brand = data.get("Brand")
    if brand:
        lines.append(f"*Brand:* {escape_markdown(brand)}")

    wine_type = data.get("Type")
    if wine_type:
        lines.append(f"*Type:* {escape_markdown(wine_type)}")

    rating = data.get("Rating")
    if rating:
        lines.append(f"*⭐️ Rating:* {escape_markdown(rating)}/5")

    basic_info = data.get("Basic Info", {})
    if basic_info:
        lines.append("\n*📌 Basic Information:*")
        for key, value in basic_info.items():
            if key == "Grapes" and isinstance(value, list):
                lines.append(f"*Grapes:* " + ", ".join(escape_markdown(g) for g in value))
            else:
                lines.append(f"*{escape_markdown(key)}:* {escape_markdown(str(value))}")

    food = data.get("Food Pairing")
    if food:
        lines.append("\n*🍽️ Food Pairing:*")
        if isinstance(food, list):
            lines.append(", ".join(map(escape_markdown, food)))
        else:
            lines.append(escape_markdown(food))

    taste = data.get("Taste Profile")
    if isinstance(taste, dict):
        lines.append("\n*🔎 Taste Profile:*")
        for axis, desc in taste.items():
            lines.append(f"_\- {escape_markdown(axis)}_: {escape_markdown(desc)}")

    notes = data.get("Notes")
    if isinstance(notes, dict):
        lines.append("\n*📝 Tasting Notes:*")
        for category, content in notes.items():
            mentions = content.get("mentions", 0)
            sub_notes = ", ".join(map(escape_markdown, content.get("notes", [])))
            lines.append(f"_\- {escape_markdown(category.title())}_ \({mentions} mentions\): {sub_notes}")

    image_url = data.get("Image")
    if image_url:
        lines.append(f"\n📷 [Image Link](https:{(image_url)})")

    return "\n".join(lines)


if __name__ == "__main__":
    wine_data = parse_wine("Château Margaux", headless=True)
    translated = format_wine_markdown(wine_data)
    print(json.dumps(translated, indent=2, ensure_ascii=False))