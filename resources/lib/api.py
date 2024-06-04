# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""Implements helper functions to interact with the Kodi library, player and
   playlist"""

from __future__ import absolute_import, division, unicode_literals

import os.path

import constants
import utils
import xbmc


EPISODE_PROPERTIES = frozenset({
    'title',
    'playcount',
    'season',
    'episode',
    'showtitle',
    # 'originaltitle',  # Not used
    'plot',
    # 'votes',  # Not used
    'file',
    'rating',
    # 'ratings',  # Not used, slow
    # 'userrating',  # Not used
    'resume',
    'tvshowid',
    'firstaired',
    'art',
    # 'streamdetails',  # Not used, slow
    'runtime',
    # 'director',  # Not used
    # 'writer',  # Not used
    # 'cast',  # Not used, slow
    'dateadded',
    'lastplayed',
})

TVSHOW_PROPERTIES = frozenset({
    'title',
    'studio',
    'year',
    'plot',
    # 'cast',  # Not used, slow
    'rating',
    # 'ratings',  # Not used, slow
    # 'userrating',  # Not used
    # 'votes',  # Not used
    'file',
    'genre',
    'episode',  # Remapped to totalepisodes
    'season',
    'runtime',
    'mpaa',
    'premiered',
    'playcount',
    'lastplayed',
    # 'sorttitle',  # Not used
    # 'originaltitle',  # Not used
    'art',
    # 'tag',  # Not used, slow
    'dateadded',
    'watchedepisodes',
    # 'imdbnumber',  # Not used
})

MOVIE_PROPERTIES = frozenset({
    'title',
    'genre',
    'year',
    'rating',
    # 'director',  # Not used
    # 'trailer',  # Not used
    'tagline',
    'plot',
    'plotoutline',
    # 'originaltitle',  # Not used
    'lastplayed',
    'playcount',
    # 'writer',  # Not used
    'studio',
    'mpaa',
    # 'cast',  # Not used, slow
    # 'country',  # Not used
    # 'imdbnumber',  # Not used
    'runtime',
    'set',
    'setid',
    # 'showlink',  # Not used, slow
    # 'streamdetails',  # Not used, slow
    'top250',
    # 'votes',  # Not used
    'fanart',
    # 'thumbnail',  # Not used
    'file',
    # 'sorttitle',  # Not used
    'resume',
    'dateadded',
    # 'tag',  # Not used, slow
    'art',
    # 'userrating',  # Not used
    # 'ratings',  # Not used, slow
    'premiered',
    # 'uniqueid',  # Not used, slow
})

COMMON_ART_MAP = {
    'thumb': ('poster',),
    'icon': ('poster',),
}
EPISODE_ART_MAP = {
    'poster': ('season.poster', 'tvshow.poster'),
    'fanart': ('season.fanart', 'tvshow.fanart'),
    'landscape': ('season.landscape', 'tvshow.landscape'),
    'clearart': ('season.clearart', 'tvshow.clearart'),
    'banner': ('season.banner', 'tvshow.banner'),
    'clearlogo': ('season.clearlogo', 'tvshow.clearlogo'),
}

RECOMMENDATION_PROPERTIES = {
    'movies': frozenset({
        'director',
        'writer',
    }),
    'tvshows': frozenset(),
    'cast': frozenset({
        'cast',  # Slow
    }),
    'tag': frozenset({
        'tag',  # Slow
    })
}

PLAYER_PLAYLIST = {
    'video': xbmc.PLAYLIST_VIDEO,  # 1
    'audio': xbmc.PLAYLIST_MUSIC,  # 0
}

JSON_MAP = {
    'episode': {
        'get_method': 'VideoLibrary.GetEpisodeDetails',
        'set_method': 'VideoLibrary.SetEpisodeDetails',
        'id_name': 'episodeid',
        'properties': EPISODE_PROPERTIES,
        'mapping': {
            'type': 'episode',
        },
        'result': 'episodedetails'
    },
    'movie': {
        'get_method': 'VideoLibrary.GetMovieDetails',
        'set_method': 'VideoLibrary.SetMovieDetails',
        'id_name': 'movieid',
        'properties': MOVIE_PROPERTIES,
        'mapping': {
            'type': 'movie',
        },
        'result': 'moviedetails'
    },
    'tvshow': {
        'get_method': 'VideoLibrary.GetTVShowDetails',
        'set_method': 'VideoLibrary.SetTVShowDetails',
        'id_name': 'tvshowid',
        'properties': TVSHOW_PROPERTIES,
        'mapping': {
            '__rename__': {'episode': 'totalepisodes'},
            'type': 'tvshow',
        },
        'result': 'tvshowdetails'
    },
    'episodes': {
        'get_method': 'VideoLibrary.GetEpisodes',
        'properties': EPISODE_PROPERTIES,
        'result': 'episodes',
        'mapping': {
            'type': 'episode',
        },
    },
    'movies': {
        'get_method': 'VideoLibrary.GetMovies',
        'properties': MOVIE_PROPERTIES,
        'result': 'movies',
        'mapping': {
            'type': 'movie',
        },
    },
    'tvshows': {
        'get_method': 'VideoLibrary.GetTVShows',
        'properties': TVSHOW_PROPERTIES,
        'mapping': {
            '__rename__': {'episode': 'totalepisodes'},
            'type': 'tvshow',
        },
        'result': 'tvshows'
    },
}

QUERY_LIMITS = {
    'start': 0,
    'end': constants.UNDEFINED
}

FILTER_TITLE = {
    'field': 'title',
    'operator': 'is',
    'value': constants.UNDEFINED_STR
}
FILTER_NOT_TITLE = {
    'field': 'title',
    'operator': 'isnot',
    'value': constants.UNDEFINED_STR
}
FILTER_NOT_FILE = {
    'field': 'filename',
    'operator': 'doesnotcontain',
    'value': constants.UNDEFINED_STR
}
FILTER_NOT_PATH = {
    'field': 'path',
    'operator': 'doesnotcontain',
    'value': constants.UNDEFINED_STR
}
FILTER_NOT_FILEPATH = {
    'or': [
        FILTER_NOT_FILE,
        FILTER_NOT_PATH
    ]
}

FILTER_INPROGRESS = {
    'field': 'inprogress',
    'operator': 'true',
    'value': ''
}
FILTER_WATCHED = {
    'field': 'playcount',
    'operator': 'greaterthan',
    'value': '0'
}
FILTER_UNWATCHED = {
    'field': 'playcount',
    'operator': 'lessthan',
    'value': '1'
}

FILTER_REGULAR_SEASON = {
    'field': 'season',
    'operator': 'greaterthan',
    'value': str(constants.SPECIALS)
}
FILTER_REGULAR_SEASON_INPROGRESS = {
    'and': [
        FILTER_REGULAR_SEASON,
        FILTER_INPROGRESS
    ]
}
FILTER_REGULAR_SEASON_WATCHED = {
    'and': [
        FILTER_REGULAR_SEASON,
        FILTER_WATCHED
    ]
}
FILTER_THIS_SEASON = {
    'field': 'season',
    'operator': 'is',
    'value': constants.UNDEFINED_STR
}

FILTER_THIS_EPISODE = {
    'field': 'episode',
    'operator': 'is',
    'value': constants.UNDEFINED_STR
}
FILTER_NEXT_EPISODE = {
    'field': 'episode',
    'operator': 'greaterthan',
    'value': constants.UNDEFINED_STR
}

FILTER_AIRED = {
    'field': 'airdate',
    'operator': 'startswith',
    'value': constants.UNDEFINED_STR
}
FILTER_NEXT_AIRED = {
    'field': 'airdate',
    'operator': 'after',
    'value': constants.UNDEFINED_STR
}
FILTER_UPNEXT_AIRED = {
    'or': [
        FILTER_NEXT_AIRED,
        {'and': [
            FILTER_AIRED,
            FILTER_NEXT_EPISODE
        ]}
    ]
}
FILTER_UNWATCHED_UPNEXT_AIRED = {
    'and': [
        FILTER_UNWATCHED,
        FILTER_UPNEXT_AIRED
    ]
}

FILTER_EPISODE = {
    'and': [
        FILTER_THIS_SEASON,
        FILTER_THIS_EPISODE
    ]
}
FILTER_UPNEXT_EPISODE = {
    'and': [
        FILTER_THIS_SEASON,
        FILTER_NEXT_EPISODE
    ]
}
FILTER_UNWATCHED_UPNEXT_EPISODE = {
    'and': [
        FILTER_UNWATCHED,
        FILTER_THIS_SEASON,
        FILTER_NEXT_EPISODE
    ]
}

FILTER_GENRE = {
    'field': 'genre',
    'operator': 'contains',
    'value': [constants.UNDEFINED_STR]
}
FILTER_UNWATCHED_GENRE = {
    'and': [
        FILTER_UNWATCHED,
        FILTER_GENRE
    ]
}

FILTER_SET = {
    'field': 'set',
    'operator': 'is',
    'value': constants.UNDEFINED_STR
}

FILTER_NEXT_MOVIE = {
    'field': 'year',
    'operator': 'after',
    'value': constants.UNDEFINED_STR
}
FILTER_UPNEXT_MOVIE = {
    'and': [
        FILTER_SET,
        FILTER_NEXT_MOVIE
    ]
}
FILTER_UNWATCHED_UPNEXT_MOVIE = {
    'and': [
        FILTER_UNWATCHED,
        FILTER_SET,
        FILTER_NEXT_MOVIE
    ]
}

SORT_YEAR = {
    'method': 'year',
    'order': 'ascending'
}
SORT_EPISODE = {
    'method': 'episode',
    'order': 'ascending'
}
SORT_LASTPLAYED = {
    'method': 'lastplayed',
    'order': 'descending'
}
SORT_DATE = {
    'method': 'date',
    'order': 'ascending'
}
SORT_RANDOM = {
    'method': 'random'
}
SORT_RATING = {
    'method': 'rating',
    'order': 'descending'
}

DISABLE_RETRY = False

_CACHE = {
    'playerid': None,
    'playlistid': None
}


def cache_invalidate():
    _CACHE.update(_CACHE.fromkeys(_CACHE))


def log(msg, level=utils.LOGDEBUG):
    """Log wrapper"""

    utils.log(msg, name=__name__, level=level)


# pylint: disable=dangerous-default-value
def art_fallbacks(item=None, art=None, art_map=COMMON_ART_MAP, replace=True):
    if item:
        art = item.get('art')
    if not art:
        return {}

    art_types = frozenset(art.keys())
    for art_type, art_substitutes in art_map.items():
        if not replace and art_type in art_types:
            continue
        for art_substitute in art_substitutes:
            if art_substitute in art_types:
                art[art_type] = art[art_substitute]
                break

    if item:
        item['art'] = art
    return art


def map_properties(item, db_type=None, mapping=None):
    if db_type:
        mapping = JSON_MAP.get(db_type, {}).get('mapping')
    if not mapping:
        return item

    for old, new in mapping.items():
        if old == '__rename__':
            for original, replacement in new.items():
                if original in item:
                    item[replacement] = item.pop(original)
        else:
            item[old] = new

    return item


def get_json_properties(item, additional=None):
    db_type = item.get('type')
    if db_type not in JSON_MAP:
        return []
    properties = JSON_MAP[db_type].get('properties')
    if properties and additional:
        return properties | additional
    if additional:
        return additional
    return properties or set()


def get_item_id(item):
    """Helper function to construct item dict with library dbid reference for
    use with params arguments of JSONRPC requests"""

    if not item:
        return {}

    db_id = item['id']
    db_type = JSON_MAP.get(item['type'])

    if not db_type or not db_id:
        return {}

    return {db_type['id_name']: db_id}


def play_kodi_item(item, resume=False):
    """Function to directly play a file from the Kodi library"""

    log('Playing from library: {0}'.format(item))

    item = get_item_id(item)
    utils.jsonrpc(method='Player.Open',
                  params={'item': item},
                  options={'resume': resume},
                  no_response=True)


def queue_next_item(data=None, item=None, playlist=None):
    """Function to add next video to the UpNext queue"""

    next_item = (
        playlist if playlist
        else get_item_id(item) if not data
        else {'file': data['play_url']} if 'play_url' in data
        else None
    )

    if next_item:
        log('Adding to queue: {0}'.format(next_item))
        utils.jsonrpc(method='Playlist.Add',
                      params={'playlistid': get_playlistid(),
                              'item': next_item},
                      no_response=True)
    else:
        log('Nothing added to queue')

    return bool(next_item)


def reset_queue():
    """Function to remove the 1st item from the playlist, used by the UpNext
       queue for the video that was just played"""

    log('Removing previously played item from queue')
    utils.jsonrpc(method='Playlist.Remove',
                  params={'playlistid': get_playlistid(), 'position': 0},
                  no_response=True)
    return False


def dequeue_next_item():
    """Function to remove the 2nd item from the playlist, used by the UpNext
       queue for the next video to be played"""

    log('Removing unplayed next item from queue')
    utils.jsonrpc(method='Playlist.Remove',
                  params={'playlistid': get_playlistid(), 'position': 1},
                  no_response=True)
    return False


def play_playlist_item(position, resume=False):
    """Function to play item in playlist from a specified position, where the
       first item in the playlist is position 1"""

    if position == 'next':
        position, _ = get_playlist_position(offset=1)
    if not position:
        log('Unable to play from playlist position: {0}'.format(position),
            utils.LOGWARNING)
        return
    log('Playing from playlist position: {0}'.format(position))

    # JSON Player.Open can be too slow but is needed if resuming is enabled
    utils.jsonrpc(method='Player.Open',
                  params={'item': {'playlistid': get_playlistid(),
                                   # Convert 1 indexed to 0 indexed position
                                   'position': position - 1}},
                  options={'resume': resume},
                  no_response=True)


def get_playlist_position(offset=0):
    """Function to get current playlist position and number of remaining
       playlist items, where the first item in the playlist is position 1"""

    # Use actual playlistid rather than xbmc.PLAYLIST_VIDEO as Kodi sometimes
    # plays video content in a music playlist
    playlistid = get_playlistid()
    if playlistid is None:
        return None, None

    playlist = xbmc.PlayList(playlistid)
    position = playlist.getposition()
    # PlayList().getposition() starts from zero unless playlist not active
    if position < 0:
        return None, None
    playlist_size = playlist.size()
    # Use 1 based index value for playlist position
    position += (offset + 1)

    # A playlist with only one element has no next item
    if playlist_size > 1 and position <= playlist_size:
        log('playlistid: {0}, position - {1}/{2}'.format(
            playlistid, position, playlist_size
        ))
        return position, (playlist_size - position)
    return None, None


def get_from_playlist(position, properties, unwatched_only=False):
    """Function to get details of item in playlist, where the first item in the
       playlist is position 1"""

    result = utils.jsonrpc(method='Playlist.GetItems',
                           params={'playlistid': get_playlistid(),
                                   # Limits start from 0, position is 1 indexed
                                   'limits': {'start': position - 1,
                                              'end': (-1 if unwatched_only
                                                      else position)},
                                   'properties': properties})
    items = result.get('result', {}).get('items')

    if not items:
        item = None
    # Get first unwatched item in the list of playlist entries
    elif unwatched_only:
        for position_offset, item in enumerate(items):
            if utils.get_int(item, 'playcount') < 1:
                position += position_offset
                break
        else:
            item = None
    # Or just get the first item in the list of playlist entries
    else:
        item = items[0]

    # Don't check if item is an episode, just use it if it is there
    if not item:  # item.get('type') != 'episode':
        log('No item in playlist at position {0}'.format(position),
            utils.LOGWARNING)
        return None

    # Playlist item may not have had video info details set
    # Try and populate required details if missing
    if not item.get('title'):
        item['title'] = item.get('label', '')
    item['episodeid'] = (
            utils.get_int(item, 'episodeid', None)
            or utils.get_int(item, 'id')
    )
    item['tvshowid'] = utils.get_int(item, 'tvshowid')
    # If missing season/episode, change to empty string to avoid episode
    # formatting issues ("S-1E-1") in UpNext popup
    if utils.get_int(item, 'season') == constants.UNDEFINED:
        item['season'] = ''
    if utils.get_int(item, 'episode') == constants.UNDEFINED:
        item['episode'] = ''

    # Store current playlist position for later use
    item['playlist_position'] = position

    log('Item in playlist at position {0}: {1}'.format(position, item))
    return item


def play_plugin_item(data, encoding, resume=False):
    """Function to play next plugin item, either using JSONRPC Player.Open or
       by passthrough back to the plugin"""

    play_url = data.get('play_url')
    if play_url:
        log('Playing from plugin - {0}'.format(play_url))
        utils.jsonrpc(method='Player.Open',
                      params={'item': {'file': play_url}},
                      options={'resume': resume},
                      no_response=True)
        return

    play_info = data.get('play_info')
    if play_info:
        log('Sending as {0} to plugin - {1}'.format(encoding, play_info))
        utils.event(message=data.get('id'),
                    data=play_info,
                    sender='upnextprovider',
                    encoding=encoding)
        return

    log('No plugin data available for playback', utils.LOGWARNING)


def get_playerid(retry=3):
    """Function to get active player playerid"""

    # We don't need to get playerid every time, cache and reuse instead
    if _CACHE['playerid'] is not None:
        return _CACHE['playerid']

    # Sometimes Kodi gets confused and uses a music playlist for video content,
    # so get the first active player instead, default to video player. Wait 2s
    # per retry in case of delay in getting response.
    attempts_left = 1 if DISABLE_RETRY else 1 + retry
    while attempts_left > 0:
        result = utils.jsonrpc(method='Player.GetActivePlayers').get('result')

        if result:
            break

        attempts_left -= 1
        if attempts_left > 0:
            utils.wait(2)
    else:
        log('No active player', utils.LOGWARNING)
        _CACHE['playerid'] = None
        return None

    for player in result:
        if player.get('type', 'video') in PLAYER_PLAYLIST:
            playerid = utils.get_int(player, 'playerid')
            break
    else:
        log('No active player', utils.LOGWARNING)
        _CACHE['playerid'] = None
        return None

    log('Selected playerid: {0}'.format(playerid))
    _CACHE['playerid'] = playerid
    return playerid


def get_playlistid():
    """Function to get playlistid of active player"""

    # We don't need to get playlistid every time, cache and reuse instead
    if _CACHE['playlistid'] is not None:
        return _CACHE['playlistid']

    result = utils.jsonrpc(method='Player.GetProperties',
                           params={'playerid': get_playerid(),
                                   'properties': ['playlistid']})
    playlistid = utils.get_int(result.get('result', {}), 'playlistid',
                               PLAYER_PLAYLIST['video'])

    log('Selected playlistid: {0}'.format(playlistid))
    _CACHE['playlistid'] = playlistid
    return playlistid


def get_player_speed():
    """Function to get speed of active player"""

    result = utils.jsonrpc(method='Player.GetProperties',
                           params={'playerid': get_playerid(),
                                   'properties': ['speed']})
    result = utils.get_float(result.get('result', {}), 'speed', 1.0)

    return result


def get_now_playing(properties, retry=3):
    """Function to get detail of currently playing item"""

    # Retry in case of delay in getting response.
    attempts_left = 1 if DISABLE_RETRY else 1 + retry
    while attempts_left > 0:
        result = utils.jsonrpc(method='Player.GetItem',
                               params={'playerid': get_playerid(retry=0),
                                       'properties': properties})
        result = result.get('result', {}).get('item')

        if result:
            break

        attempts_left -= 1
        if attempts_left > 0:
            utils.wait(2)
    else:
        log('Now playing item info not found', utils.LOGWARNING)
        return None

    log('Now playing: {0}'.format(result))
    return result


def get_next_from_library(item, **kwargs):
    """Function to get details of next episode in tvshow, or next movie in
    movieset, from Kodi library"""

    if item['type'] == 'episode':
        return get_next_episode_from_library(episode=item['details'], **kwargs)

    if item['type'] == 'movie':
        if 'next_season' in kwargs:
            del kwargs['next_season']
        return get_next_movie_from_library(movie=item['details'], **kwargs)

    log('No next video found, unsupported media type', utils.LOGWARNING)
    return None


def get_next_episode_from_library(episode=constants.UNDEFINED,
                                  next_season=True,
                                  unwatched_only=False,
                                  random=False):
    """Function to get show and next episode details from Kodi library"""

    if not episode or episode == constants.UNDEFINED:
        log('No next episode found, current episode not in library',
            utils.LOGWARNING)
        return episode

    tvshowid = utils.get_int(episode, 'tvshowid')
    if not tvshowid or tvshowid == constants.UNDEFINED:
        log('No next episode found, invalid tvshowid',
            utils.LOGWARNING)
        return episode

    (path, filename) = os.path.split(episode['file'])
    FILTER_NOT_FILE['value'] = filename
    FILTER_NOT_PATH['value'] = path
    filters = [
        # Check that both next filename and path are different to current
        # to deal with different file naming schemes e.g.
        # Season 1/Episode 1.mkv
        # Season 1/Episode 1/video.mkv
        # Season 1/Episode 1-2-3.mkv
        FILTER_NOT_FILEPATH
    ]

    if unwatched_only:
        # Exclude watched episodes
        filters.append(FILTER_UNWATCHED)

    if random:
        sort = SORT_RANDOM
    elif next_season:
        sort = SORT_DATE
        FILTER_NEXT_EPISODE['value'] = str(episode['episode'])
        aired = utils.iso_datetime(episode['firstaired'])
        FILTER_AIRED['value'] = aired.split()[0]
        FILTER_NEXT_AIRED['value'] = aired
        filters.append(FILTER_UPNEXT_AIRED)
    else:
        sort = SORT_EPISODE
        FILTER_THIS_SEASON['value'] = str(episode['season'])
        FILTER_NEXT_EPISODE['value'] = str(episode['episode'])
        filters.append(FILTER_UPNEXT_EPISODE)

    filters = {'and': filters}

    result, _ = get_videos_from_library(db_type='episodes',
                                        limit=1,
                                        sort=sort,
                                        filters=filters,
                                        params={'tvshowid': tvshowid})

    if not result:
        log('No next episode found in library')
        return None

    # Update current episode details dict, containing tvshow details, with next
    # episode details. Surprisingly difficult to retain backwards compatibility
    # episode = episode | result       # Python > v3.9
    # episode = {**episode, **result}  # Python > v3.5
    episode = dict(episode, **result)  # Python > v2.7
    log('Next episode from library: {0}'.format(episode))
    return episode


def get_next_movie_from_library(movie=constants.UNDEFINED,
                                unwatched_only=False,
                                random=False):
    """Function to get details of next movie in set from Kodi library"""

    if not movie or movie == constants.UNDEFINED:
        log('No next movie found, current movie not in library',
            utils.LOGWARNING)
        return None

    set_name = movie['set']
    set_id = utils.get_int(movie, 'setid')
    if not set_name or not set_id or set_id == constants.UNDEFINED:
        log('No next movie found, invalid movie set "{0}" ({1})'.format(
            set_name, set_id
        ), utils.LOGWARNING)
        return None

    (path, filename) = os.path.split(movie['file'])
    FILTER_NOT_FILE['value'] = filename
    FILTER_NOT_PATH['value'] = path
    filters = [FILTER_NOT_FILEPATH]

    FILTER_SET['value'] = set_name
    filters.append(FILTER_SET)

    if unwatched_only:
        filters.append(FILTER_UNWATCHED)

    if random:
        sort = SORT_RANDOM
    else:
        sort = SORT_YEAR
        FILTER_NEXT_MOVIE['value'] = str(movie['year'])
        filters.append(FILTER_NEXT_MOVIE)

    filters = {'and': filters}

    movie, _ = get_videos_from_library(db_type='movies',
                                       limit=1,
                                       sort=sort,
                                       filters=filters)

    if not movie:
        log('No next movie found in library')
        return None

    log('Next movie from library: {0}'.format(movie))
    return movie


def get_from_library(db_type=None, db_id=constants.UNDEFINED, item=None):
    """Function to get video and collection details from Kodi library"""

    if item:
        db_type = item['type']
        db_id = item['id']

    if not db_type or db_id == constants.UNDEFINED:
        log('Video info not found in library, invalid dbid', utils.LOGWARNING)
        return None

    details, _ = get_details_from_library(db_type=db_type, db_id=db_id)

    if not details:
        log('Video info for {0} {1} not found in library'.format(
            db_type, db_id
        ), utils.LOGWARNING)
        return None

    if db_type == 'episode':
        db_id = utils.get_int(details, 'tvshowid')
        tvshow_details, _ = get_details_from_library(db_type='tvshow',
                                                     db_id=db_id)

        if not tvshow_details:
            log('tvshowid {0} not found in library'.format(db_id),
                utils.LOGWARNING)
            return None
        tvshow_details.update(details)
        details = tvshow_details

    log('Info from library: {0}'.format(details))
    return details


def get_tvshowid(title):
    """Function to search Kodi library for tshowid by title"""

    FILTER_TITLE['value'] = title
    tvshow, _ = get_videos_from_library(db_type='tvshows',
                                        limit=1,
                                        properties=[],
                                        filters=FILTER_TITLE)

    if not tvshow:
        log('showtitle "{0}" not found in library'.format(title),
            utils.LOGWARNING)
        return constants.UNDEFINED

    tvshowid = utils.get_int(tvshow, 'tvshowid')
    log('Found tvshowid {0} for showtitle "{1}"'.format(tvshowid, title))
    return tvshowid


def get_episodeid(tvshowid, season, episode):
    """Function to search Kodi library for episodeid by tvshowid, season, and
       episode"""

    FILTER_THIS_SEASON['value'] = str(season)
    FILTER_THIS_EPISODE['value'] = str(episode)

    result, _ = get_videos_from_library(db_type='episodes',
                                        limit=1,
                                        properties=[],
                                        filters=FILTER_EPISODE,
                                        params={'tvshowid': tvshowid})

    if not result:
        log('episodeid for tvshowid {0} S{1}E{2} not found in library'.format(
            tvshowid, season, episode
        ), utils.LOGWARNING)
        return constants.UNDEFINED

    episodeid = utils.get_int(result, 'episodeid')
    log('Found episodeid {0} for tvshowid {1} S{2}E{3}'.format(
        episodeid, tvshowid, season, episode
    ))
    return episodeid


def get_details_from_library(db_type=None,
                             db_id=constants.UNDEFINED,
                             item=None,
                             properties=None):
    """Function to retrieve video info details from Kodi library"""

    if item:
        db_type = item['type']
        db_id = item['id']

    if not db_type or db_id == constants.UNDEFINED:
        return None, None

    detail_type = JSON_MAP.get(db_type)
    if detail_type and 'id_name' not in detail_type:
        detail_type = JSON_MAP.get(db_type[:-1])
    if not detail_type:
        return None, None

    if properties is None:
        properties = detail_type['properties']
    elif isinstance(properties, (set, frozenset)):
        properties = detail_type['properties'] | properties

    result = utils.jsonrpc(method=detail_type['get_method'],
                           params={detail_type['id_name']: db_id,
                                   'properties': properties})

    result = result.get('result', {}).get(detail_type['result'], {})
    if result and properties:
        map_properties(result, mapping=detail_type['mapping'])
    return result, detail_type


def handle_just_watched(item, reset_playcount=False, resume_from_end=0.1):
    """Function to update playcount and resume point of just watched video"""

    details = get_details_from_library(item=item,
                                       properties=['playcount', 'resume'])
    details, detail_type = details

    if not details:
        return

    resume = details.get('resume')
    playcount = utils.get_int(item.get('details'), 'playcount', 0)
    params = {}

    # If Kodi has not updated playcount then UpNext will
    if reset_playcount:
        params['playcount'] = 0
    elif utils.get_int(details, 'playcount', 0) == playcount:
        params['playcount'] = playcount + 1

    # If resume point has been saved then reset it
    total = utils.get_int(resume, 'total', 0)
    if 0 > utils.get_int(resume, 'position') >= (1 - resume_from_end) * total:
        params['resume'] = {'position': 0, 'total': total}

    # Only update library if playcount or resume point needs to change
    if params:
        params[detail_type['id_name']] = item['id']
        utils.jsonrpc(method=detail_type['set_method'],
                      params=params,
                      no_response=True)

    log('Library update: {0}{1}{2}{3}'.format(
        '{0}_id - {1}'.format(item['type'], item['id']),
        ', playcount - {0} to {1}'.format(playcount, params['playcount'])
        if 'playcount' in params else '',
        ', resume - {0} to {1}'.format(resume, params['resume'])
        if 'resume' in params else '',
        '' if params else ', no change'
    ), utils.LOGDEBUG)


# pylint: disable=too-many-locals
def get_upnext_episodes_from_library(limit=25,
                                     next_season=True,
                                     unwatched_only=False,
                                     resume_from_end=0.1):
    """Function to get in-progress and next episode details from Kodi library"""

    if next_season:
        filters = [
            FILTER_INPROGRESS,
            FILTER_WATCHED,
            (FILTER_UNWATCHED_UPNEXT_AIRED if unwatched_only
             else FILTER_UPNEXT_AIRED)
        ]
        sort = SORT_DATE
    else:
        filters = [
            FILTER_REGULAR_SEASON_INPROGRESS,
            FILTER_REGULAR_SEASON_WATCHED,
            (FILTER_UNWATCHED_UPNEXT_EPISODE if unwatched_only
             else FILTER_UPNEXT_EPISODE)
        ]
        sort = SORT_EPISODE

    inprogress, _ = get_videos_from_library(db_type='episodes',
                                            limit=limit,
                                            sort=SORT_LASTPLAYED,
                                            filters=filters[0])

    watched, _ = get_videos_from_library(db_type='episodes',
                                         limit=limit,
                                         sort=SORT_LASTPLAYED,
                                         filters=filters[1])

    episodes = utils.merge_iterable(inprogress, watched,
                                    sort='lastplayed', unique='episodeid')

    upnext_episodes = []
    tvshow_index = set()
    for episode in episodes:
        tvshowid = episode['tvshowid']
        if tvshowid in tvshow_index:
            continue

        resume = episode['resume']
        if 0 < resume['position'] < (1 - resume_from_end) * resume['total']:
            upnext_episode = episode
        else:
            FILTER_THIS_SEASON['value'] = str(episode['season'])
            FILTER_NEXT_EPISODE['value'] = str(episode['episode'])
            aired = utils.iso_datetime(episode['firstaired'])
            FILTER_AIRED['value'] = aired.split()[0]
            FILTER_NEXT_AIRED['value'] = aired

            upnext_episode, _ = get_videos_from_library(
                db_type='episodes',
                limit=1,
                sort=sort,
                filters=filters[2],
                params={'tvshowid': tvshowid},
            )

            if not upnext_episode:
                tvshow_index.add(tvshowid)
                continue

        # Restore current episode lastplayed for sorting of next-up episode
        upnext_episode['lastplayed'] = episode['lastplayed']
        art_fallbacks(upnext_episode, art_map=EPISODE_ART_MAP, replace=False)
        # Combine tvshow details with episode details
        tvshow_details, _ = get_details_from_library(
            db_type='tvshow', db_id=tvshowid,
        )
        tvshow_details.update(upnext_episode)
        upnext_episodes.append(tvshow_details)
        tvshow_index.add(tvshowid)

    return upnext_episodes


def get_upnext_movies_from_library(limit=25,
                                   movie_sets=True,
                                   unwatched_only=False,
                                   resume_from_end=0.1):
    """Function to get in-progress and next movie details from Kodi library"""

    inprogress, _ = get_videos_from_library(db_type='movies',
                                            limit=limit,
                                            sort=SORT_LASTPLAYED,
                                            filters=FILTER_INPROGRESS)

    if movie_sets:
        watched, _ = get_videos_from_library(db_type='movies',
                                             limit=limit,
                                             sort=SORT_LASTPLAYED,
                                             filters=FILTER_WATCHED)

        movies = utils.merge_iterable(inprogress, watched,
                                      sort='lastplayed', unique='movieid')
    else:
        movies = inprogress

    filters = (
        FILTER_UNWATCHED_UPNEXT_MOVIE if unwatched_only
        else FILTER_UPNEXT_MOVIE
    )

    upnext_movies = []
    set_index = set()
    for movie in movies:
        set_id = movie['setid'] or constants.UNDEFINED
        if set_id != constants.UNDEFINED and set_id in set_index:
            continue

        resume = movie['resume']
        if 0 < resume['position'] < (1 - resume_from_end) * resume['total']:
            upnext_movie = movie
        elif movie_sets and movie['set'] and set_id != constants.UNDEFINED:
            FILTER_SET['value'] = movie['set']
            FILTER_NEXT_MOVIE['value'] = str(movie['year'])

            upnext_movie, _ = get_videos_from_library(db_type='movies',
                                                      limit=1,
                                                      sort=SORT_YEAR,
                                                      filters=filters)

            if not upnext_movie:
                set_index.add(set_id)
                continue
        else:
            continue

        # Restore current movie lastplayed for sorting of next-up movie
        upnext_movie['lastplayed'] = movie['lastplayed']
        art_fallbacks(upnext_movie)
        upnext_movies.append(upnext_movie)
        set_index.add(set_id)

    return upnext_movies


def get_videos_from_library(db_type,  # pylint: disable=too-many-arguments
                            limit=25,
                            sort=None,
                            properties=None,
                            filters=None,
                            params=None):
    """Function to get videos from Kodi library"""

    detail_type = JSON_MAP.get(db_type)
    if not detail_type:
        return None

    _params = {}

    if properties is None:
        properties = detail_type['properties']
    elif isinstance(properties, (set, frozenset)):
        properties = detail_type['properties'] | properties
    _params['properties'] = properties

    if filters is not None:
        _params['filter'] = filters

    if isinstance(limit, dict):
        _params['limits'] = limit
    elif limit is not None:
        QUERY_LIMITS['end'] = limit
        _params['limits'] = QUERY_LIMITS

    if sort is not None:
        _params['sort'] = sort

    if params is not None:
        _params.update(params)

    videos = utils.jsonrpc(method=detail_type['get_method'],
                           params=_params)
    videos = videos.get('result', {}).get(detail_type['result'], [])

    if videos and limit == 1:
        video = videos[0]
        if properties:
            map_properties(video, mapping=detail_type['mapping'])
        return video, detail_type
    return videos, detail_type


class InfoTagComparator(object):
    __slots__ = (
        'cast_crew',
        'fuzz',
        'genres',
        'set_name',
        'tags',
        'count',
        'limit',
        'threshold',
    )

    from re import compile as re_compile
    from string import punctuation as string_punctuation

    K_CAST_CREW = 10
    K_FUZZ = 7.5
    K_GENRES = 15
    K_SET_NAME = 20
    K_TAGS = 12.5
    MAX_SIMILARITY = K_CAST_CREW + K_FUZZ + K_GENRES + K_SET_NAME + K_TAGS

    STR_TYPE = type('')

    IGNORE_WORDS = frozenset({
        '',
        'ABOUT',
        'AFTER',
        'FROM',
        'HAVE',
        'HERS',
        'INTO',
        'ONLY',
        'OVER',
        'THAN',
        'THAT',
        'THEIR',
        'THERE',
        'THEM',
        'THEN',
        'THEY',
        'THIS',
        'WHAT',
        'WHEN',
        'WHERE',
        'WILL',
        'WITH',
        'YOUR',
        'COLLECTION',
        'DURINGCREDITSSTINGER',
        'AFTERCREDITSSTINGER',
    })
    PUNCTUATION = frozenset(string_punctuation)
    PUNCTUATION_TRANSLATION_TABLE = dict.fromkeys(map(ord, string_punctuation))
    del string_punctuation

    _token_split = re_compile(r'[_.,]* |[|/\\]').split
    del re_compile

    def __init__(self, infotags, limit=constants.UNDEFINED,
                 cast_limit=constants.CAST_LIMIT,
                 _get=dict.get,
                 _set=set):

        self.cast_crew = (
                {cast['name']
                 for cast in _get(infotags, 'cast', [])
                 if cast['order'] <= cast_limit}
                | _set(_get(infotags, 'director', []))
                | _set(_get(infotags, 'writer', []))
        )
        self.fuzz = self.tokenise([_get(infotags, 'plot'),
                                   _get(infotags, 'title')])
        self.genres = _set(_get(infotags, 'genre', []))
        self.set_name = self.tokenise([_get(infotags, 'set')])
        self.tags = self.tokenise(_get(infotags, 'tag', []), split=False)

        self.count = dict.fromkeys(self.genres, 0)
        self.count['__len__'] = len(self.genres)
        self.count['__num__'] = 0
        self.count['__sum__'] = 0
        self.limit = limit

        self.threshold = self.MAX_SIMILARITY / 5 - (
            0 if self.set_name and self.tags else
            self.K_TAGS / 5 if self.set_name else
            self.K_SET_NAME / 5 if self.tags else
            (self.K_TAGS + self.K_SET_NAME) / 5
        )

    # pylint: disable=too-many-arguments, too-many-branches, too-many-locals
    def compare(self,
                infotags,
                cast_limit=constants.CAST_LIMIT,
                _get=dict.get,
                _len=len,
                _min=min,
                _set=set):

        cast_crew_stored = self.cast_crew
        fuzz_stored = self.fuzz
        genres_stored = self.genres
        set_name_stored = self.set_name
        tags_stored = self.tags
        count = self.count
        limit = self.limit
        threshold = self.threshold

        genres = _set(_get(infotags, 'genre', []))
        if not genres:
            return 0

        similarity = self.K_GENRES * (
                _len(genres & genres_stored)
                / _len(genres | genres_stored)
        )

        if cast_crew_stored:
            cast_crew = (
                    {cast['name']
                     for cast in _get(infotags, 'cast', [])
                     if cast['order'] <= cast_limit}
                    | _set(_get(infotags, 'director', []))
                    | _set(_get(infotags, 'writer', []))
            )
            if cast_crew:
                similarity += self.K_CAST_CREW * (
                        _len(cast_crew & cast_crew_stored)
                        / _len(cast_crew | cast_crew_stored)
                )

        if fuzz_stored:
            fuzz = self.tokenise([_get(infotags, 'plot'),
                                  _get(infotags, 'title')])
            if fuzz:
                similarity += self.K_FUZZ * _min(1, (
                        (2 * _len(fuzz & fuzz_stored)) ** 2
                        / _len(fuzz | fuzz_stored)
                ))

        if set_name_stored:
            set_name = self.tokenise([_get(infotags, 'set')])
            if set_name:
                similarity += self.K_SET_NAME * (
                        _len(set_name & set_name_stored)
                        / _len(set_name | set_name_stored)
                )
            else:
                threshold -= self.K_SET_NAME / 5

        if tags_stored:
            tags = self.tokenise(_get(infotags, 'tag', []), split=False)
            if tags:
                similarity += self.K_TAGS * _min(1, (
                        (2 * _len(tags & tags_stored)) ** 2
                        / _len(tags | tags_stored)
                ))
            else:
                threshold -= self.K_TAGS / 5

        if similarity > threshold:
            counted = False
            for genre in genres:
                if genre in count:
                    count[genre] += 1
                    count['__sum__'] += 1
                    counted = True
            if counted:
                count['__num__'] += 1

            if count['__sum__'] / count['__len__'] >= limit >= 0:
                return None
            return similarity if counted else 0
        return 0

    @staticmethod
    # pylint: disable-next=too-many-arguments, dangerous-default-value
    def tokenise(values,
                 split=_token_split,
                 min_length=constants.TOKEN_LENGTH,
                 compare_set=PUNCTUATION,
                 translation_table=PUNCTUATION_TRANSLATION_TABLE,
                 ignore_set=IGNORE_WORDS,
                 _istitle=STR_TYPE.istitle,
                 _isupper=STR_TYPE.isupper,
                 _len=len,
                 _set=set,
                 _translate=STR_TYPE.translate,
                 _upper=STR_TYPE.upper):

        tokens = {
            token for value in values if value for token in split(value)
        } if split else _set(values)

        processed_tokens = {
            _upper(_translate(token, translation_table)
                   if compare_set & _set(token) else
                   token)
            for token in tokens
            if (_len(token) > min_length
                or _isupper(token)
                and not _istitle(token))
        }

        return processed_tokens - ignore_set


# pylint: disable=too-many-arguments, too-many-locals, too-many-statements, too-many-branches
def get_similar_from_library(db_type,
                             limit=25,
                             original=None,
                             db_id=constants.UNDEFINED,
                             unwatched_only=False,
                             use_cast=False,
                             use_tag=False,
                             return_all=False):
    """Function to search by db_id for similar videos from Kodi library"""

    if use_cast and use_tag:
        properties = (
                RECOMMENDATION_PROPERTIES[db_type]
                | RECOMMENDATION_PROPERTIES['cast']
                | RECOMMENDATION_PROPERTIES['tag']
        )
    elif use_cast:
        properties = (
                RECOMMENDATION_PROPERTIES[db_type]
                | RECOMMENDATION_PROPERTIES['cast']
        )
    elif use_tag:
        properties = (
                RECOMMENDATION_PROPERTIES[db_type]
                | RECOMMENDATION_PROPERTIES['tag']
        )
    else:
        properties = RECOMMENDATION_PROPERTIES[db_type]

    if original:
        # Use original video passed as argument to function call
        pass
    elif db_id == constants.UNDEFINED or db_id is None:
        original, _ = get_videos_from_library(db_type=db_type,
                                              limit=1,
                                              sort=SORT_RANDOM,
                                              properties=properties,
                                              filters=FILTER_WATCHED)
    else:
        original, _ = get_details_from_library(db_type=db_type,
                                               db_id=int(db_id),
                                               properties=properties)

    if not original:
        return None, []

    infotags = InfoTagComparator(original, limit=limit)
    selected = []
    video_index = set()

    id_name = 'movieid' if db_type == 'movies' else 'tvshowid'
    if id_name in original:
        video_index.add(original[id_name])

    if infotags.set_name and db_type == 'movies':
        FILTER_SET['value'] = original['set']
        similar, _ = get_videos_from_library(db_type=db_type,
                                             limit=None,
                                             sort=SORT_YEAR,
                                             filters=FILTER_SET)
        for video in similar:
            db_id = video[id_name]
            if db_id in video_index:
                continue
            video_index.add(db_id)
            art_fallbacks(video)
            video['__similarity__'] = InfoTagComparator.MAX_SIMILARITY
            selected.append(video)

    if not infotags.genres:
        return original, selected

    chunk_size = limit * 10
    chunk_limit = {
        'start': 0,
        'end': chunk_size,
    }

    FILTER_GENRE['value'] = infotags.genres
    unwatched_only = FILTER_UNWATCHED_GENRE if unwatched_only else FILTER_GENRE
    while True:
        similar, detail_type = get_videos_from_library(db_type=db_type,
                                                       limit=chunk_limit,
                                                       sort=SORT_RATING,
                                                       properties=properties,
                                                       filters=unwatched_only)

        for video in similar:
            db_id = video[id_name]
            if db_id in video_index:
                continue
            video_index.add(db_id)
            similarity = infotags.compare(video)
            if similarity is None:
                break
            if similarity:
                art_fallbacks(video)
                map_properties(video, mapping=detail_type['mapping'])
                video['__similarity__'] = similarity
                selected.append(video)
        else:
            if chunk_size and len(similar) == chunk_size:
                chunk_limit['start'] += chunk_size
                chunk_limit['end'] += chunk_size
                continue
        break

    if return_all:
        return original, selected
    selected = utils.merge_iterable(selected, sort='__similarity__')
    return original, selected[:limit]
