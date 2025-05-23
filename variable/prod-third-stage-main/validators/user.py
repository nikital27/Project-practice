import re

import geopy.exc
import geopy.geocoders
import sqlalchemy.engine.base

import strings
import utils.db
import validators.core

user_agent = 'python-telegram-bot'

MAX_LOGIN_LENGTH = 32
MIN_LOGIN_LENGTH = 5
LOGIN_REGEX = r'^[a-zA-Z0-9_]*$'

MAX_AGE_IN_YEARS = 130
MIN_AGE_IN_YEARS = 6
MAX_BIO_LENGTH = 120
MAX_INTERESTS_COUNT = 10


def validate_login(login: str, db_engine: sqlalchemy.engine.base.Engine):
    if utils.db.check_user_exist(db_engine, login):
        raise validators.core.ValidationError(
            strings.LOGIN_ALREADY_EXISTS_ERROR,
        )

    if len(login) > MAX_LOGIN_LENGTH:
        raise validators.core.ValidationError(strings.LOGIN_TOO_LONG_ERROR)

    if not re.match(LOGIN_REGEX, login):
        raise validators.core.ValidationError(strings.LOGIN_INCORRECT_ERROR)

    if len(login) < MIN_LOGIN_LENGTH:
        raise validators.core.ValidationError(strings.LOGIN_TOO_SHORT_ERROR)

    return login


def validate_age(age: str):
    if not age.isnumeric():
        raise validators.core.ValidationError(strings.AGE_INCORRECT_ERROR)

    if int(age) < MIN_AGE_IN_YEARS:
        raise validators.core.ValidationError(strings.AGE_TOO_LOW_ERROR)

    if int(age) > MAX_AGE_IN_YEARS:
        raise validators.core.ValidationError(strings.AGE_TOO_HIGH_ERROR)

    return int(age)


def validate_location_by_name(location: str):
    geolocator = geopy.geocoders.Nominatim(user_agent=user_agent)

    try:
        user_city, user_country = location.split(',')
    except ValueError as e:
        raise validators.core.ValidationError(
            strings.LOCATION_INPUT_ERROR,
        ) from e

    try:
        location_country = geolocator.geocode(user_country)
        location_city = geolocator.geocode(location)
    except geopy.exc.GeocoderTimedOut as e:
        raise validators.core.ValidationError(strings.TIMEOUT_ERROR) from e

    if (
        not location_country
        or not location_city
        or location_city.raw['type']
        not in [
            'city',
            'administrative',
        ]
        or not location_country.raw.get('type', None) == 'administrative'
    ):
        raise validators.core.ValidationError(
            strings.LOCATION_INCORRECT_ERROR,
        )

    country = location_country.raw['name']
    city = location_city.raw['name']

    return city, country


def validate_location_by_coords(lat: str, lon: str):
    geolocator = geopy.geocoders.Nominatim(user_agent=user_agent)

    location_details = geolocator.reverse((lat, lon))

    if not location_details:
        raise validators.core.ValidationError(
            strings.LOCATION_INCORRECT_ERROR,
        )
    try:
        country = location_details.raw['address']['country']
        city = location_details.raw['address']['city']
    except KeyError as e:
        raise validators.core.ValidationError(
            strings.LOCATION_INCORRECT_ERROR,
        ) from e

    return city, country


def validate_bio(bio: str):
    if len(bio) > MAX_BIO_LENGTH:
        raise validators.core.ValidationError(strings.BIO_TOO_LONG_ERROR)

    return bio


def validate_interests(interests: str):
    try:
        interests = {
            x.strip().lower()
            for x in interests.split(',')
            if x.strip().isalpha()
        }
    except (ValueError, AttributeError) as e:
        raise validators.core.ValidationError(
            strings.INTERESTS_INCORRECT_ERROR,
        ) from e

    if len(interests) > MAX_INTERESTS_COUNT:
        raise validators.core.ValidationError(
            strings.INTERESTS_TOO_MANY_ERROR,
        )

    return interests
