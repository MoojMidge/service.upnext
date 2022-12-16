# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""This is the actual UpNext plugin handler"""

from __future__ import absolute_import, division, unicode_literals
from posixpath import split as posix_split
import xbmcgui
import xbmcplugin
import api
import constants
from settings import SETTINGS
import upnext
import utils

try:
    from urllib.parse import parse_qs, urlparse
except ImportError:
    from urlparse import parse_qs, urlparse


def generate_library_plugin_data(current_item, addon_id, state=None):
    media_type = current_item['media_type']
    if state:
        next_item = state.get_next()
    else:
        next_item = utils.create_item_details(
            api.get_next_from_library(
                item=current_item,
                next_season=SETTINGS.next_season,
                unwatched_only=SETTINGS.unwatched_only
            ),
            source='library', media_type=media_type
        )

    if (not next_item
            or not next_item['details']
            or next_item['source'] != 'library'):
        return None

    upnext_info = {
        'current_video': upnext.create_listitem(current_item),
        'next_video': upnext.create_listitem(next_item),
        'play_url': 'plugin://{0}/play/?dbtype={1}&dbid={2}'.format(
            addon_id, media_type, next_item['db_id']
        )
    }
    return upnext_info


def generate_listing(addon_handle, addon_id, items):  # pylint: disable=unused-argument
    listing = []
    for item in items:
        content = PLUGIN_CONTENT.get(item)
        if not content:
            continue

        url = 'plugin://{0}/{1}{2}'.format(addon_id, item, content.get('params', ''))
        listitem = xbmcgui.ListItem(
            label=content.get('label', ''), path=url, offscreen=True
        )
        if 'art' in content:
            listitem.setArt(content.get('art'))

        listing += ((url, listitem, True),)

    return listing


def generate_next_episodes_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    episodes = api.get_upnext_episodes_from_library(
        next_season=SETTINGS.next_season,
        unwatched_only=SETTINGS.unwatched_only
    )

    listing = []
    for episode in episodes:
        listitem = upnext.create_episode_listitem(episode)
        listing += ((episode['file'], listitem, False),)

    return listing


def generate_next_movies_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    movies = api.get_upnext_movies_from_library(
        movie_sets=SETTINGS.enable_movieset,
        unwatched_only=SETTINGS.unwatched_only
    )

    listing = []
    for movie in movies:
        listitem = upnext.create_movie_listitem(movie)
        listing += ((movie['file'], listitem, False),)

    return listing


def generate_next_media_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    episodes = api.get_upnext_episodes_from_library(
        next_season=SETTINGS.next_season,
        unwatched_only=SETTINGS.unwatched_only
    )
    movies = api.get_upnext_movies_from_library(
        movie_sets=SETTINGS.enable_movieset,
        unwatched_only=SETTINGS.unwatched_only
    )

    videos = utils.merge_iterable(
        episodes, movies, sort='lastplayed', reverse=True
    )

    listing = []
    for video in videos:
        listitem = upnext.create_listitem(video)
        listing += ((video['file'], listitem, False),)

    return listing


def generate_watched_movie_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    movies = api.get_watched_movies_from_library()

    listing = []
    for movie in movies:
        url = 'plugin://{0}/similar_movies/{1}'.format(addon_id, movie['movieid'])
        listitem = upnext.create_movie_listitem(
            movie,
            infolabels={'path': url},
            properties={'isPlayable': 'false', 'isFolder': True}
        )
        listing += ((url, listitem, True),)

    return listing


def generate_similar_movie_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    path = kwargs.get('__path__')
    if not path or path[-1] == 'similar_movies':
        movieid = constants.UNDEFINED
    else:
        movieid = path[-1]

    movie, movies = api.get_similar_movies_from_library(
        movieid=movieid,
        unwatched_only=SETTINGS.unwatched_only
    )
    if movie:
        title = movie['title']
        label = utils.localize(constants.MORE_LIKE_THIS_STR_ID).format(title)
        xbmcplugin.setPluginCategory(addon_handle, label)

    listing = []
    for movie in movies:
        listitem = upnext.create_movie_listitem(
            movie,
            properties={
                'searchstring': title,  # For Emburary skin integration
                'widget': label         # For AH2 skin integration
            }
        )
        listing += ((movie['file'], listitem, False),)

    return listing


def open_settings(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    utils.get_addon(addon_id).openSettings()

    xbmcplugin.endOfDirectory(addon_handle, False)
    return False


def parse_plugin_url(url):
    if not url:
        return None, None, None

    parsed_url = urlparse(url)
    if parsed_url.scheme != 'plugin':
        return None, None, None

    addon_id = parsed_url.netloc
    addon_path = posix_split(parsed_url.path.rstrip('/') or '/')
    while addon_path[0] != '/':
        addon_path = posix_split(addon_path[0]) + addon_path[1:]
    addon_args = parse_qs(parsed_url.query, keep_blank_values=True)

    return addon_id, addon_path, addon_args


def play_media(addon_handle, addon_id, **kwargs):
    dbtype = kwargs.get('dbtype', [''])[0]
    dbid = int(kwargs.get('dbid', [constants.UNDEFINED])[0])

    if dbtype and dbid != constants.UNDEFINED:
        current_video = api.get_from_library(media_type=dbtype, db_id=dbid)
        current_item = utils.create_item_details(
            current_video, 'library', dbtype
        )
    else:
        current_item = None

    upnext_info = generate_library_plugin_data(
        current_item=current_item,
        addon_id=addon_id
    ) if current_item and current_item['details'] else None

    if upnext_info:
        resolved = True
        upnext.send_signal(addon_id, upnext_info)
    else:
        resolved = False
        upnext_info = {'current_video': xbmcgui.ListItem(offscreen=True)}

    xbmcplugin.setResolvedUrl(
        addon_handle, resolved, upnext_info['current_video']
    )
    return resolved


def run(argv):
    addon_handle = int(argv[1])
    addon_id, addon_path, addon_args = parse_plugin_url(argv[0] + argv[2])
    content = PLUGIN_CONTENT.get(addon_path[1] or addon_path[0])
    if not content:
        return False

    content_label = content.get('label') or PLUGIN_CONTENT['/']['label']
    content_type = content.get('content_type')
    content_items = content.get('items')
    content_handler = content.get('handler')
    addon_args['__path__'] = addon_path

    if content_type == 'action' and content_handler:
        return content_handler(addon_handle, addon_id, **addon_args)

    xbmcplugin.setPluginCategory(addon_handle, content_label)
    if content_handler:
        content_items = content_handler(addon_handle, addon_id, **addon_args)
    elif content_items:
        content_items = generate_listing(addon_handle, addon_id, content_items)

    if content_type and content_items is not None:
        xbmcplugin.setContent(addon_handle, content_type)
        listing_complete = xbmcplugin.addDirectoryItems(
            addon_handle, content_items, len(content_items)
        )
    else:
        listing_complete = False

    xbmcplugin.endOfDirectory(
        addon_handle, listing_complete, updateListing=False, cacheToDisc=True
    )
    return listing_complete


PLUGIN_CONTENT = {
    '/': {
        'label': utils.localize(constants.PLUGIN_HOME_STR_ID),
        'content_type': 'files',
        'items': [
            'next_episodes',
            'next_movies',
            'next_media',
            'watched_movies',
            'similar_movies',
            'settings',
        ],
    },
    'next_episodes': {
        'label': utils.localize(constants.NEXT_EPISODES_STR_ID),
        'art': {
            'icon': 'DefaultInProgressShows.png',
        },
        'content_type': 'episodes',
        'handler': generate_next_episodes_list,
    },
    'next_movies': {
        'label': utils.localize(constants.NEXT_MOVIES_STR_ID),
        'art': {
            'icon': 'DefaultMovies.png',
        },
        'content_type': 'movies',
        'handler': generate_next_movies_list,
    },
    'next_media': {
        'label': utils.localize(constants.NEXT_MEDIA_STR_ID),
        'art': {
            'icon': 'DefaultVideo.png'
        },
        'content_type': 'videos',
        'handler': generate_next_media_list,
    },
    'watched_movies': {
        'label': utils.localize(constants.WATCHED_MOVIES_STR_ID),
        'art': {
            'icon': 'DefaultMovies.png'
        },
        'content_type': 'movies',
        'handler': generate_watched_movie_list,
    },
    'similar_movies': {
        'label': utils.localize(constants.MORE_LIKE_MOVIES_STR_ID),
        'art': {
            'icon': 'DefaultMovies.png'
        },
        'content_type': 'movies',
        'handler': generate_similar_movie_list,
        'params': constants.WIDGET_RELOAD_PARAM_STRING
    },
    'settings': {
        'label': utils.localize(constants.SETTINGS_STR_ID),
        'art': {
            'icon': 'DefaultAddonProgram.png'
        },
        'content_type': 'action',
        'handler': open_settings,
    },
    'play': {
        'content_type': 'action',
        'handler': play_media,
    },
}
