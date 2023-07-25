import python_weather
import instagrapi
import asyncio
import os
from random import sample, choice
from dotenv import load_dotenv
from enum import Enum
from instagrapi.exceptions import LoginRequired
from utils import get_logger

load_dotenv()

logger = get_logger()

INSTAGRAM_USERNAME = os.environ.get('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.environ.get('INSTAGRAM_PASSWORD')

class WeatherType(Enum):
    RAIN_LIGHT = 1
    RAIN_MEDIUM = 2
    RAIN_HEAVY = 3

async def main() -> None:
    logger.info('Getting Brittany cities.')
    with open('cities.txt', 'r', encoding='utf-8') as f:
        cities = f.read().split('\n')

    logger.info('Selecting 10 random cities.')
    random_cities = sample(cities, 10)

    logger.info('Getting precipitation for each city :')
    cities_precipitation = {}

    async with python_weather.Client(unit=python_weather.METRIC) as weather_client:
        for city in random_cities:
            logger.info('   Getting weather data for %s.' % city)
            weather = await weather_client.get(f"{city}, Bretagne, France")

            if weather.current.precipitation > 8:
                cities_precipitation[city] = WeatherType.RAIN_HEAVY
            elif weather.current.precipitation > 4:
                cities_precipitation[city] = WeatherType.RAIN_MEDIUM
            elif weather.current.precipitation > 0.3:
                cities_precipitation[city] = WeatherType.RAIN_LIGHT
            else:
                continue

    if len(cities_precipitation) == 0:
        logger.info('No rain detected on any of the cities, exiting.')
        return

    logger.info('Rain detected on %d cities, selecting one randomly.' % len(cities_precipitation))
    city = choice(list(cities_precipitation.keys()))
    rain_type = cities_precipitation[city]

    logger.info(f'{rain_type.name} detected on {city}, posting to Instagram the corresponding picture and caption.')

    logger.info('Logging in to Instagram.')
    instagram_client = login_instagram()

    logger.info('Getting the latest media posted on Instagram.')
    latest_media = instagram_client.user_medias(instagram_client.user_id, 1)

    with open(f'texts/{rain_type.name.lower()}.txt', 'r', encoding='utf-8') as _caption_file:
        caption = _caption_file.read()

    # if len(latest_media) > 0 and latest_media[0].caption_text.lower() == caption.lower():
    #     logger.warning('The latest media is already posted, nothing to do.')
    #     return

    logger.info('There is no media posted about this rain type, posting it.')
    instagram_client.photo_upload(f"images/generated/{rain_type.name.lower()}_{city.replace(' ', '_')}.jpg", caption)
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
