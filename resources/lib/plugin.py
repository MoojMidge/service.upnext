# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""This is the actual UpNext plugin handler"""

from __future__ import absolute_import, division, unicode_literals

from random import shuffle as randshuffle

import api
import constants
import upnext
import utils
import xbmcgui
import xbmcplugin
from settings import SETTINGS


def log(msg, level=utils.LOGDEBUG):
    """Log wrapper"""

    utils.log(msg, name=__name__, level=level)


def generate_library_plugin_data(current_item, addon_id, state=None):
    if state:
        next_item = state.get_next()
    else:
        next_item = utils.create_item_details(api.get_next_from_library(
            item=current_item,
            next_season=SETTINGS.next_season,
            unwatched_only=SETTINGS.unwatched_only
        ), 'library')

    if (not next_item
            or not next_item['details']
            or next_item['source'] != 'library'):
        return None

    upnext_info = {
        'current_video': upnext.create_listitem(current_item),
        'next_video': upnext.create_listitem(next_item),
        'play_url': 'plugin://{0}/play_media/?type={1}&id={2}'.format(
            addon_id, next_item['type'], next_item['id']
        )
    }
    return upnext_info


def generate_listing(addon_handle, addon_id, items):  # pylint: disable=unused-argument
    listing = []
    for item in items:
        content = PLUGIN_CONTENT.get(item)
        if not content:
            continue

        path = 'plugin://{0}/{1}{2}'.format(
            addon_id, item, content.get('params', '')
        )
        listitem = xbmcgui.ListItem(
            label=content.get('label', ''), path=path, offscreen=True
        )
        if 'art' in content:
            listitem.setArt(content.get('art'))

        listing += ((path, listitem, True),)

    return listing


def generate_next_movies_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    movies = api.get_upnext_movies_from_library(
        limit=SETTINGS.widget_list_limit,
        movie_sets=SETTINGS.enable_movieset,
        unwatched_only=SETTINGS.unwatched_only,
        resume_from_end=SETTINGS.resume_from_end
    )

    listing = []
    for movie in movies:
        listitem = upnext.create_movie_listitem(movie)
        listing += ((movie['file'], listitem, False),)

    return listing


def generate_watched_movies_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    movies, _ = api.get_videos_from_library(
        db_type='movies',
        limit=SETTINGS.widget_list_limit,
        sort=api.SORT_LASTPLAYED,
        filters=api.FILTER_WATCHED
    )

    listing = []
    for movie in movies:
        path = 'plugin://{0}/similar_movies/{1}'.format(
            addon_id, movie['movieid']
        )
        listitem = upnext.create_movie_listitem(
            movie,
            properties={'isPlayable': 'false', 'isFolder': True},
            infolabels={'path': path},
        )
        listing += ((path, listitem, True),)

    return listing


def generate_similar_movies_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    path = kwargs.get('__path__', ['similar_movies'])
    last_path = path[-1]

    if last_path == 'similar_movies':
        movieid = constants.UNDEFINED
    else:
        movieid = last_path

    movie, movies = api.get_similar_from_library(
        db_type='movies',
        limit=SETTINGS.widget_list_limit,
        db_id=movieid,
        unwatched_only=SETTINGS.widget_unwatched_only,
        use_cast=SETTINGS.widget_enable_cast,
        use_tag=SETTINGS.widget_enable_tags,
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
                'searchstring': title,  # For Embruary skin integration
                'widget': label,        # For AH2 skin integration
                'similartitle': title,  # SHS compatibility
            }
        )
        listing += ((movie['file'], listitem, False),)

    return listing


def generate_next_episodes_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    episodes = api.get_upnext_episodes_from_library(
        limit=SETTINGS.widget_list_limit,
        next_season=SETTINGS.next_season,
        unwatched_only=SETTINGS.unwatched_only,
        resume_from_end=SETTINGS.resume_from_end
    )

    listing = []
    for episode in episodes:
        listitem = upnext.create_episode_listitem(episode)
        listing += ((episode['file'], listitem, False),)

    return listing


def generate_watched_tvshows_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    tvshows, _ = api.get_videos_from_library(
        db_type='tvshows',
        limit=SETTINGS.widget_list_limit,
        sort=api.SORT_LASTPLAYED,
        filters=api.FILTER_WATCHED
    )

    listing = []
    for tvshow in tvshows:
        path = 'plugin://{0}/similar_tvshows/{1}'.format(
            addon_id, tvshow['tvshowid']
        )
        listitem = upnext.create_tvshow_listitem(
            tvshow,
            properties={'isPlayable': 'false', 'isFolder': True},
            infolabels={'path': path},
        )
        listing += ((path, listitem, True),)

    return listing


def generate_similar_tvshows_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    path = kwargs.get('__path__', ['similar_tvshows'])
    last_path = path[-1]

    if last_path == 'similar_tvshows':
        tvshowid = constants.UNDEFINED
    else:
        tvshowid = last_path

    tvshow, tvshows = api.get_similar_from_library(
        db_type='tvshows',
        limit=SETTINGS.widget_list_limit,
        db_id=tvshowid,
        unwatched_only=SETTINGS.widget_unwatched_only,
        use_cast=SETTINGS.widget_enable_cast,
        use_tag=SETTINGS.widget_enable_tags,
    )
    if tvshow:
        title = tvshow['title']
        label = utils.localize(constants.MORE_LIKE_THIS_STR_ID).format(title)
        xbmcplugin.setPluginCategory(addon_handle, label)

    listing = []
    for tvshow in tvshows:
        path = 'videodb://tvshows/titles/{0}/'.format(tvshow['tvshowid'])
        listitem = upnext.create_tvshow_listitem(
            tvshow,
            properties={
                'searchstring': title,  # For Embruary skin integration
                'widget': label,        # For AH2 skin integration
                'similartitle': title,  # SHS compatibility
                'isFolder': True
            },
            infolabels={'path': path},
        )
        listing += ((path, listitem, True),)

    return listing


def generate_next_media_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    episodes = api.get_upnext_episodes_from_library(
        limit=SETTINGS.widget_list_limit,
        next_season=SETTINGS.next_season,
        unwatched_only=SETTINGS.unwatched_only,
        resume_from_end=SETTINGS.resume_from_end
    )
    movies = api.get_upnext_movies_from_library(
        limit=SETTINGS.widget_list_limit,
        movie_sets=SETTINGS.enable_movieset,
        unwatched_only=SETTINGS.unwatched_only,
        resume_from_end=SETTINGS.resume_from_end
    )

    videos = utils.merge_iterable(episodes, movies, sort='lastplayed')

    listing = []
    for video in videos[:SETTINGS.widget_list_limit]:
        listitem = upnext.create_listitem(video)
        listing += ((video['file'], listitem, False),)

    return listing


def generate_watched_media_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    movies, _ = api.get_videos_from_library(
        db_type='movies',
        limit=SETTINGS.widget_list_limit,
        sort=api.SORT_LASTPLAYED,
        filters=api.FILTER_WATCHED,
    )
    tvshows, _ = api.get_videos_from_library(
        db_type='tvshows',
        limit=SETTINGS.widget_list_limit,
        sort=api.SORT_LASTPLAYED,
        filters=api.FILTER_WATCHED,
    )

    videos = utils.merge_iterable(movies, tvshows, sort='lastplayed')

    listing = []
    for video in videos[:SETTINGS.widget_list_limit]:
        if 'tvshowid' in video:
            listitem = upnext.create_tvshow_listitem
            path = 'plugin://{0}/similar_media/tvshows/{1}'.format(
                addon_id, video['tvshowid']
            )
        else:
            listitem = upnext.create_movie_listitem
            path = 'plugin://{0}/similar_media/movies/{1}'.format(
                addon_id, video['movieid']
            )
        listitem = listitem(
            video,
            properties={'isPlayable': 'false', 'isFolder': True},
            infolabels={'path': path}
        )
        listing += ((path, listitem, True),)

    return listing


def generate_similar_media_list(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    path = kwargs.get('__path__', ['similar_media'])
    last_path = path[-1]
    similar_list = ['movies', 'tvshows']

    if 'movies' in path:
        db_id = constants.UNDEFINED if last_path in similar_list else last_path
    elif 'tvshows' in path:
        db_id = constants.UNDEFINED if last_path in similar_list else last_path
        similar_list.reverse()
    else:
        db_id = constants.UNDEFINED
        randshuffle(similar_list)

    original, similar_list[0] = api.get_similar_from_library(
        db_type=similar_list[0],
        limit=SETTINGS.widget_list_limit,
        db_id=db_id,
        unwatched_only=SETTINGS.widget_unwatched_only,
        use_cast=SETTINGS.widget_enable_cast,
        use_tag=SETTINGS.widget_enable_tags,
        return_all=True
    )
    original, similar_list[1] = api.get_similar_from_library(
        db_type=similar_list[1],
        limit=SETTINGS.widget_list_limit,
        original=original,
        unwatched_only=SETTINGS.widget_unwatched_only,
        use_cast=SETTINGS.widget_enable_cast,
        use_tag=SETTINGS.widget_enable_tags,
        return_all=True
    )
    if original:
        title = original['title']
        label = utils.localize(constants.MORE_LIKE_THIS_STR_ID).format(title)
        xbmcplugin.setPluginCategory(addon_handle, label)

    videos = utils.merge_iterable(*similar_list, sort='__similarity__')

    listing = []
    for video in videos[:SETTINGS.widget_list_limit]:
        if 'tvshowid' in video:
            listitem = upnext.create_tvshow_listitem
            path = 'videodb://tvshows/titles/{0}/'.format(video['tvshowid'])
            is_folder = True
        else:
            listitem = upnext.create_movie_listitem
            path = video['file']
            is_folder = False
        listitem = listitem(
            video,
            properties={
                'searchstring': title,  # For Embruary skin integration
                'widget': label,        # For AH2 skin integration
                'similartitle': title,  # SHS compatibility
                'isFolder': is_folder
            },
            infolabels={'path': path},
        )
        listing += ((path, listitem, is_folder),)

    return listing


def open_settings(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    utils.get_addon(addon_id).openSettings()

    xbmcplugin.endOfDirectory(addon_handle, False)
    return False


def play_media(addon_handle, addon_id, **kwargs):
    if 'id' in kwargs:
        kwargs['id'] = utils.get_int(kwargs, 'id')
        current_video = api.get_from_library(item=kwargs)
        current_item = utils.create_item_details(current_video, 'library')
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


def play_plugin(addon_handle, addon_id, **kwargs):  # pylint: disable=unused-argument
    from tmdb_helper import Player
    Player(**kwargs).play(handle=addon_handle)


@utils.Profiler(enabled=SETTINGS.widget_debug, lazy=True)
def run(argv):
    addon_handle = int(argv[1])
    addon_id, addon_path, addon_args = utils.parse_url(argv[0] + argv[2])
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
            'movie_widgets',
            'tvshow_widgets',
            'media_widgets',
            'settings',
        ],
    },
    'tvshow_widgets': {
        'label': utils.localize(constants.PLUGIN_TVSHOWS_STR_ID),
        'art': {
            'icon': 'DefaultTVShows.png'
        },
        'content_type': 'files',
        'items': [
            'next_episodes',
            'watched_tvshows',
            'similar_tvshows',
        ],
    },
    'movie_widgets': {
        'label': utils.localize(constants.PLUGIN_MOVIES_STR_ID),
        'art': {
            'icon': 'DefaultMovies.png',
        },
        'content_type': 'files',
        'items': [
            'next_movies',
            'watched_movies',
            'similar_movies',
        ],
    },
    'media_widgets': {
        'label': utils.localize(constants.PLUGIN_MEDIA_STR_ID),
        'art': {
            'icon': 'DefaultVideo.png'
        },
        'content_type': 'files',
        'items': [
            'next_media',
            'watched_media',
            'similar_media',
        ],
    },
    'next_movies': {
        'label': utils.localize(constants.NEXT_MOVIES_STR_ID),
        'art': {
            'icon': 'DefaultMovies.png',
        },
        'content_type': 'movies',
        'handler': generate_next_movies_list,
        'params': (constants.WIDGET_RELOAD_PARAM_STRING
                   if SETTINGS.widget_refresh_all else '')
    },
    'next_episodes': {
        'label': utils.localize(constants.NEXT_EPISODES_STR_ID),
        'art': {
            'icon': 'DefaultInProgressShows.png',
        },
        'content_type': 'episodes',
        'handler': generate_next_episodes_list,
        'params': (constants.WIDGET_RELOAD_PARAM_STRING
                   if SETTINGS.widget_refresh_all else '')
    },
    'next_media': {
        'label': utils.localize(constants.NEXT_MEDIA_STR_ID),
        'art': {
            'icon': 'DefaultVideo.png'
        },
        'content_type': 'videos',
        'handler': generate_next_media_list,
        'params': (constants.WIDGET_RELOAD_PARAM_STRING
                   if SETTINGS.widget_refresh_all else '')
    },
    'watched_movies': {
        'label': utils.localize(constants.WATCHED_MOVIES_STR_ID),
        'art': {
            'icon': 'DefaultMovies.png'
        },
        'content_type': 'movies',
        'handler': generate_watched_movies_list,
        'params': (constants.WIDGET_RELOAD_PARAM_STRING
                   if SETTINGS.widget_refresh_all else '')
    },
    'watched_tvshows': {
        'label': utils.localize(constants.WATCHED_TVSHOWS_STR_ID),
        'art': {
            'icon': 'DefaultTVShows.png'
        },
        'content_type': 'tvshows',
        'handler': generate_watched_tvshows_list,
        'params': (constants.WIDGET_RELOAD_PARAM_STRING
                   if SETTINGS.widget_refresh_all else '')
    },
    'watched_media': {
        'label': utils.localize(constants.WATCHED_MEDIA_STR_ID),
        'art': {
            'icon': 'DefaultVideo.png'
        },
        'content_type': 'tvshows',
        'handler': generate_watched_media_list,
        'params': (constants.WIDGET_RELOAD_PARAM_STRING
                   if SETTINGS.widget_refresh_all else '')
    },
    'similar_movies': {
        'label': utils.localize(constants.MORE_LIKE_MOVIES_STR_ID),
        'art': {
            'icon': 'DefaultMovies.png'
        },
        'content_type': 'movies',
        'handler': generate_similar_movies_list,
        'params': constants.WIDGET_RELOAD_PARAM_STRING
    },
    'similar_tvshows': {
        'label': utils.localize(constants.MORE_LIKE_TVSHOWS_STR_ID),
        'art': {
            'icon': 'DefaultTVShows.png'
        },
        'content_type': 'tvshows',
        'handler': generate_similar_tvshows_list,
        'params': constants.WIDGET_RELOAD_PARAM_STRING
    },
    'similar_media': {
        'label': utils.localize(constants.MORE_LIKE_MEDIA_STR_ID),
        'art': {
            'icon': 'DefaultVideo.png'
        },
        'content_type': 'tvshows',
        'handler': generate_similar_media_list,
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
    'play_media': {
        'content_type': 'action',
        'handler': play_media,
    },
    'play_plugin': {
        'content_type': 'action',
        'handler': play_plugin,
    },
}
