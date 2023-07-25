import os
from PIL import Image, ImageFont
from pilmoji import Pilmoji
from pilmoji.source import AppleEmojiSource
from utils import get_logger

logger = get_logger('BretagnePluieH24-ImageGenerator')

TEXT_COLOR = (0, 0, 0)
BACKGROUND_COLOR = (255, 255, 255)
TEXT_OFFSET = 50

logger.info('Checking if images/generated exists.')
if not os.path.exists('images/generated'):
    logger.info('images/generated does not exist, creating it.')
    os.makedirs('images/generated')

font_text = ImageFont.truetype("fonts/Montserrat-ExtraBold.ttf", 98)

states = {
    'light': {
        'text': 'Pluie légère',
        'emoji': '☁️',
        'emoji_font_size': 1200
    },
    'medium': {
        'text': 'Pluie modérée',
        'emoji': '🌧️',
        'emoji_font_size': 900
    },
    'heavy': {
        'text': 'Pluie forte',
        'emoji': '🌩️',
        'emoji_font_size': 1000
    }
}

logger.info('Getting Brittany cities.')
with open('cities.txt', 'r', encoding='utf-8') as f:
    cities = f.read().split('\n')

def generate_image(city: str, text_weather: str, text_state: str, font_size_weather: int, rain_state: str) -> None:
    img = Image.new('RGB', (2048, 2048), color=BACKGROUND_COLOR)
    width, height = img.size

    text_city = f"📍 {city}"
    font_weather = ImageFont.truetype("fonts/Montserrat-ExtraBold.ttf", font_size_weather)

    account_logo = Image.open("images/account_logo.jpg")
    account_logo = account_logo.resize((150, 150))
    account_logo_width, account_logo_height = account_logo.size
    account_logo_x = width - account_logo_width - 20
    account_logo_y = height - account_logo_height - 20
    img.paste(account_logo, (account_logo_x, account_logo_y))

    with Pilmoji(img, source=AppleEmojiSource) as pilmoji:
        text_weather_width, text_weather_height = pilmoji.getsize(text_weather, font=font_weather)
        text_weather_x = (height - text_weather_width) / 2
        text_weather_y = (width - text_weather_height) / 2
        pilmoji.text((text_weather_x, text_weather_y), text_weather, font=font_weather, fill=TEXT_COLOR)

        text_city_width, text_city_height = pilmoji.getsize(text_city, font=font_text)
        text_city_x = (height - text_city_width) / 2
        text_city_y = text_weather_y - text_city_height - TEXT_OFFSET
        pilmoji.text((text_city_x, text_city_y), text_city, font=font_text, fill=TEXT_COLOR)

        text_state_width, text_state_height = pilmoji.getsize(text_state, font=font_text)
        text_state_x = (height - text_state_width) / 2
        text_state_y = text_weather_y + text_weather_height + TEXT_OFFSET
        pilmoji.text((text_state_x, text_state_y), text_state, font=font_text, fill=TEXT_COLOR)

    img.save(f"images/generated/rain_{rain_state}_{city.replace(' ', '_')}.jpg")

for city in cities:
    logger.info('Generating images for %s.' % city)
    for rain_state in states:
        logger.info('   Generating image for %s.' % rain_state)
        text_city = city
        text_weather = states[rain_state]['emoji']
        text_state = states[rain_state]['text']
        font_size_weather = states[rain_state]['emoji_font_size']
        generate_image(text_city, text_weather, text_state, font_size_weather, rain_state)
