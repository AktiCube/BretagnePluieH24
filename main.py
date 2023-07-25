import python_weather
import instagrapi
import logging
import asyncio
import os
from dotenv import load_dotenv
from enum import Enum
from utils import _ColourFormatter
from instagrapi.exceptions import LoginRequired

load_dotenv()

handler = logging.StreamHandler()
file_handler = logging.FileHandler('BretagnePluieH24.log')
logger = logging.getLogger('BretagnePluieH24')
logger.setLevel(logging.INFO)
handler.setFormatter(_ColourFormatter())
file_handler.setFormatter(logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'))
logger.addHandler(handler)
logger.addHandler(file_handler)

INSTAGRAM_USERNAME = os.environ.get('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.environ.get('INSTAGRAM_PASSWORD')

class WeatherType(Enum):
    RAIN_LIGHT = ['images/rain_light.jpg', 'texts/rain_light.txt']
    RAIN_MEDIUM = ['images/rain_medium.jpg', 'texts/rain_medium.txt']
    RAIN_HEAVY = ['images/rain_heavy.jpg', 'texts/rain_heavy.txt']

async def main() -> None:
    async with python_weather.Client(unit=python_weather.METRIC) as weather_client:
        logger.info('Getting weather data.')

        weather = await weather_client.get('Saint-Ségal, France')

        if weather.current.precipitation > 8:
            rain_type = WeatherType.RAIN_HEAVY
        elif weather.current.precipitation > 4:
            rain_type = WeatherType.RAIN_MEDIUM
        elif weather.current.precipitation > 0.3:
            rain_type = WeatherType.RAIN_LIGHT
        else:
            logger.info('There is no rain, nothing to do.')
            return

    logger.info(f'{rain_type.name} detected, posting to Instagram the corresponding picture and caption.')

    logger.info('Logging in to Instagram.')
    instagram_client = login_instagram()

    logger.info('Getting the latest media posted on Instagram.')
    latest_media = instagram_client.user_medias(instagram_client.user_id, 1)

    with open(rain_type.value[1], 'r', encoding='utf-8') as _caption_file:
        caption = _caption_file.read()

    if len(latest_media) > 0 and latest_media[0].caption_text.lower() == caption.lower():
        logger.warning('The latest media is already posted, nothing to do.')
        return

    logger.info('There is no media posted about this rain type, posting it.')
    instagram_client.photo_upload(rain_type.value[0], caption)
    logger.info('Media posted.')

    instagram_client.dump_settings("instagram_session.json")
    logger.info('Session saved, exiting.')

def login_instagram() -> instagrapi.Client:
    instagram_client = instagrapi.Client()
    session = instagram_client.load_settings("instagram_session.json")

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            instagram_client.set_settings(session)
            instagram_client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

            try:
                instagram_client.get_timeline_feed()
            except LoginRequired:
                logger.info("Session is invalid, need to login via username and password")

                old_session = instagram_client.get_settings()

                instagram_client.set_settings({})
                instagram_client.set_uuids(old_session["uuids"])

                instagram_client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            login_via_session = True
        except Exception as e:
            logger.error("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info("Attempting to login via username and password. username: %s" % INSTAGRAM_USERNAME)
            if instagram_client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD):
                login_via_pw = True
        except Exception as e:
            logger.error("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")
    else:
        instagram_client.dump_settings("instagram_session.json")
        return instagram_client

if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
