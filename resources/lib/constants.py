# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals


ADDON_ID = 'service.upnext'

UNDEFINED = -1
UNDEFINED_STR = '-1'

WINDOW_HOME = 10000
WIDGET_RELOAD_PROPERTY_NAME = 'UpNext.Widgets.Reload'
WIDGET_RELOAD_PARAM_STRING = '?reload=$INFO[Window({0}).Property({1})]'.format(
    WINDOW_HOME, WIDGET_RELOAD_PROPERTY_NAME
)

PLAY_CTRL_ID = 3012
CLOSE_CTRL_ID = 3013
PROGRESS_CTRL_ID = 3014
SHUFFLE_CTRL_ID = 3015

STOP_STR_ID = 30033
CLOSE_STR_ID = 30034
NEXT_STR_ID = 30049

PLUGIN_HOME_STR_ID = 30100
SETTINGS_STR_ID = 30101
NEXT_EPISODES_STR_ID = 30102
NEXT_MOVIES_STR_ID = 30103
NEXT_MEDIA_STR_ID = 30104
WATCHED_MOVIES_STR_ID = 30105
MORE_LIKE_MOVIES_STR_ID = 30106
MORE_LIKE_TVSHOWS_STR_ID = 30107
MORE_LIKE_THIS_STR_ID = 30108

UNWATCHED_MOVIE_PLOT = 0
UNWATCHED_EPISODE_PLOT = 1
UNWATCHED_EPISODE_THUMB = 2
DEFAULT_SPOILERS = [
    UNWATCHED_MOVIE_PLOT,
    UNWATCHED_EPISODE_PLOT,
    UNWATCHED_EPISODE_THUMB,
]
NO_SPOILER_IMAGE = 'OverlaySpoiler.png'
NO_SPOILER_ART = {
    'fanart': NO_SPOILER_IMAGE,
    'landscape': NO_SPOILER_IMAGE,
    'clearart': NO_SPOILER_IMAGE,
    'clearlogo': NO_SPOILER_IMAGE,
    'poster': NO_SPOILER_IMAGE,
    'thumb': NO_SPOILER_IMAGE,
}

VALUE_FROM_STR = {
    'false': False,
    'true': True,
}
VALUE_TO_STR = {
    None: '',
    False: 'false',
    True: 'true',
}

LOG_ENABLE_DISABLED = 0
LOG_ENABLE_INFO = 1
LOG_ENABLE_DEBUG = 2

SEASON_EPISODE = '{0}x{1}'
SPECIALS = 0
UNTITLED = 'untitled'
MIXED_PLAYLIST = 'mixedplaylist'

PLUGIN_TYPES = (
    'plugin_data_error',
    'plugin_playlist',
    'plugin_play_url',
    'plugin_play_url_playlist',
    'plugin_play_info',
    'plugin_play_info_playlist',
)
PLUGIN_DATA_ERROR = 0
PLUGIN_PLAYLIST = 1
PLUGIN_PLAY_URL = 2
PLUGIN_PLAY_INFO = 4

SETTING_DISABLED = 0
SETTING_ON = 1
SETTING_OFF = 2

POPUP_MIN_DURATION = 5

POPUP_POSITIONS = {
    0: 'bottom',
    1: 'centre',
    2: 'top',
}

POPUP_ACCENT_COLOURS = {
    0: 'FFFF4081',
    1: 'FFFF2A00',
    2: 'FF84DE02',
    3: 'FF3399FF',
}

SIM_SEEK_15S = 1
SIM_SEEK_POPUP_TIME = 2
SIM_SEEK_DETECT_TIME = 3

PIL_RESIZE_METHODS = {
    0: 0,  # PIL.Image.NEAREST
    1: 4,  # PIL.Image.BOX
    2: 2,  # PIL.Image.BILINEAR
    3: 5,  # PIL.Image.HAMMING
    4: 3,  # PIL.Image.BICUBIC
    5: 1,  # PIL.Image.LANCZOS
}
