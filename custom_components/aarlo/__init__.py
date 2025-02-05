"""
This component provides support for Netgear Arlo IP cameras.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/arlo/
"""
import logging
from datetime import timedelta

import voluptuous as vol
from requests.exceptions import HTTPError, ConnectTimeout

from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_HOST)
from homeassistant.helpers import config_validation as cv

__version__ = '0.6.5'

_LOGGER = logging.getLogger(__name__)

CONF_ATTRIBUTION = "Data provided by my.arlo.com"
DATA_ARLO = 'data_aarlo'
DEFAULT_BRAND = 'Netgear Arlo'
DOMAIN = 'aarlo'

NOTIFICATION_ID = 'aarlo_notification'
NOTIFICATION_TITLE = 'aarlo Component Setup'

CONF_PACKET_DUMP = 'packet_dump'
CONF_CACHE_VIDEOS = 'cache_videos'
CONF_DB_MOTION_TIME = 'db_motion_time'
CONF_DB_DING_TIME = 'db_ding_time'
CONF_RECENT_TIME = 'recent_time'
CONF_LAST_FORMAT = 'last_format'
CONF_CONF_DIR = 'conf_dir'
CONF_REQ_TIMEOUT = 'request_timeout'
CONF_STR_TIMEOUT = 'stream_timeout'
CONF_NO_MEDIA_UP = 'no_media_upload'
CONF_USER_AGENT = 'user_agent'
CONF_MODE_API = 'mode_api'
CONF_DEVICE_REFRESH = 'refresh_devices_every'
CONF_HTTP_CONNECTIONS = 'http_connections'
CONF_HTTP_MAX_SIZE = 'http_max_size'
CONF_RECONNECT_EVERY = 'reconnect_every'

SCAN_INTERVAL = timedelta(seconds=60)
PACKET_DUMP = False
CACHE_VIDEOS = False
DB_MOTION_TIME = timedelta(seconds=30)
DB_DING_TIME = timedelta(seconds=10)
RECENT_TIME = timedelta(minutes=10)
LAST_FORMAT = '%m-%d %H:%M'
CONF_DIR = ''
REQ_TIMEOUT = timedelta(seconds=60)
STR_TIMEOUT = timedelta(seconds=0)
NO_MEDIA_UP = False
USER_AGENT = 'apple'
MODE_API = 'auto'
DEVICE_REFRESH = 0
HTTP_CONNECTIONS = 5
HTTP_MAX_SIZE = 10
RECONNECT_EVERY = 0
DEFAULT_HOST = 'https://my.arlo.com'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.url,
        vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
        vol.Optional(CONF_PACKET_DUMP, default=PACKET_DUMP): cv.boolean,
        vol.Optional(CONF_CACHE_VIDEOS, default=CACHE_VIDEOS): cv.boolean,
        vol.Optional(CONF_DB_MOTION_TIME, default=DB_MOTION_TIME): cv.time_period,
        vol.Optional(CONF_DB_DING_TIME, default=DB_DING_TIME): cv.time_period,
        vol.Optional(CONF_RECENT_TIME, default=RECENT_TIME): cv.time_period,
        vol.Optional(CONF_LAST_FORMAT, default=LAST_FORMAT): cv.string,
        vol.Optional(CONF_CONF_DIR, default=CONF_DIR): cv.string,
        vol.Optional(CONF_REQ_TIMEOUT, default=REQ_TIMEOUT): cv.time_period,
        vol.Optional(CONF_STR_TIMEOUT, default=STR_TIMEOUT): cv.time_period,
        vol.Optional(CONF_NO_MEDIA_UP, default=NO_MEDIA_UP): cv.boolean,
        vol.Optional(CONF_USER_AGENT, default=USER_AGENT): cv.string,
        vol.Optional(CONF_MODE_API, default=MODE_API): cv.string,
        vol.Optional(CONF_DEVICE_REFRESH, default=DEVICE_REFRESH): cv.positive_int,
        vol.Optional(CONF_HTTP_CONNECTIONS, default=HTTP_CONNECTIONS): cv.positive_int,
        vol.Optional(CONF_HTTP_MAX_SIZE, default=HTTP_MAX_SIZE): cv.positive_int,
        vol.Optional(CONF_RECONNECT_EVERY, default=RECONNECT_EVERY): cv.positive_int,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up an Arlo component."""

    # Read config
    conf = config[DOMAIN]
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    host = conf.get(CONF_HOST)
    packet_dump = conf.get(CONF_PACKET_DUMP)
    cache_videos = conf.get(CONF_CACHE_VIDEOS)
    motion_time = conf.get(CONF_DB_MOTION_TIME).total_seconds()
    ding_time = conf.get(CONF_DB_DING_TIME).total_seconds()
    recent_time = conf.get(CONF_RECENT_TIME).total_seconds()
    last_format = conf.get(CONF_LAST_FORMAT)
    conf_dir = conf.get(CONF_CONF_DIR)
    req_timeout = conf.get(CONF_REQ_TIMEOUT).total_seconds()
    str_timeout = conf.get(CONF_STR_TIMEOUT).total_seconds()
    no_media_up = conf.get(CONF_NO_MEDIA_UP)
    user_agent = conf.get(CONF_USER_AGENT)
    mode_api = conf.get(CONF_MODE_API)
    device_refresh = conf.get(CONF_DEVICE_REFRESH)
    http_connections = conf.get(CONF_HTTP_CONNECTIONS)
    http_max_size = conf.get(CONF_HTTP_MAX_SIZE)
    reconnect_every = conf.get(CONF_RECONNECT_EVERY)

    # Fix up config
    if conf_dir == '':
        conf_dir = hass.config.config_dir + '/.aarlo'

    try:
        from .pyaarlo import PyArlo

        arlo = PyArlo(username=username, password=password, cache_videos=cache_videos,
                      storage_dir=conf_dir, dump=packet_dump, host=host,
                      db_motion_time=motion_time, db_ding_time=ding_time,
                      request_timeout=req_timeout, stream_timeout=str_timeout,
                      recent_time=recent_time, last_format=last_format,
                      no_media_upload=no_media_up,
                      user_agent=user_agent, mode_api=mode_api,
                      refresh_devices_every=device_refresh, reconnect_every=reconnect_every,
                      http_connections=http_connections, http_max_size=http_max_size)
        if not arlo.is_connected:
            return False

        hass.data[DATA_ARLO] = arlo

    except (ConnectTimeout, HTTPError) as ex:
        _LOGGER.error("Unable to connect to Netgear Arlo: %s", str(ex))
        hass.components.persistent_notification.create(
            'Error: {}<br />You will need to restart hass after fixing.'.format(ex),
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID)
        return False

    return True
