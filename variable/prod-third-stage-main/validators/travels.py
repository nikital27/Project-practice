import datetime

import geopy.geocoders

import strings
import validators.core

user_agent = 'python-telegram-bot'

MAX_NAME_LENGTH = 32
MAX_DESCRIPTION_LENGTH = 120


def validate_name(name: str) -> str:
    if len(name) > MAX_NAME_LENGTH:
        raise validators.core.ValidationError(strings.NAME_TOO_LONG_ERROR)

    return name


def validate_location(location: str) -> str:
    geolocator = geopy.geocoders.Nominatim(user_agent=user_agent)

    try:
        location_request = geolocator.geocode(location)
    except geopy.exc.GeocoderTimedOut as e:
        raise validators.core.ValidationError(strings.TIMEOUT_ERROR) from e

    if not location_request or location_request.raw['type'] not in [
        'city',
        'town',
        'administrative',
    ]:
        raise validators.core.ValidationError(
            strings.LOCATION_INCORRECT_ERROR,
        )

    name = location_request.raw['name']
    display_name = location_request.raw['display_name']
    lat = location_request.raw['lat']
    lon = location_request.raw['lon']

    return name, display_name, lat, lon


def validate_description(description: str) -> str:
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise validators.core.ValidationError(
            strings.DESCRIPTION_TOO_LONG_ERROR,
        )
    return description


def validate_start(start: str) -> str:
    try:
        return datetime.datetime.strptime(start, '%H:%M %d.%m.%Y').astimezone()
    except ValueError as e:
        raise validators.core.ValidationError(
            strings.START_INCORRECT_ERROR,
        ) from e


def validate_end(start, end: str) -> str:
    try:
        end = datetime.datetime.strptime(end, '%H:%M %d.%m.%Y').astimezone()
    except ValueError as e:
        raise validators.core.ValidationError(
            strings.END_INCORRECT_ERROR,
        ) from e

    if start >= end:
        raise validators.core.ValidationError(strings.END_LAST_DAY_ERROR)

    return end
