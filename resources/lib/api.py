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
EPISODE_ART_MAP = {
    'poster': ('season.poster', 'tvshow.poster'),
    'fanart': ('season.fanart', 'tvshow.fanart'),
    'landscape': ('season.landscape', 'tvshow.landscape'),
    'clearart': ('season.clearart', 'tvshow.clearart'),
    'banner': ('season.banner', 'tvshow.banner'),
    'clearlogo': ('season.clearlogo', 'tvshow.clearlogo'),
}

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
    'episode',
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
    'thumb': ('poster', ),
    'icon': ('poster', ),
}

RECOMMENDATION_PROPERTIES = {
    'movies': frozenset({
        'title',
        'genre',
        'plot',
        'set',
        'tag'
    }),
    'tvshows': frozenset({
        'title',
        'genre',
        'plot',
        'tag'
    })
}

PLAYER_PLAYLIST = {
    'video': xbmc.PLAYLIST_VIDEO,  # 1
    'audio': xbmc.PLAYLIST_MUSIC   # 0
}

JSON_MAP = {
    'episode': {
        'get_method': 'VideoLibrary.GetEpisodeDetails',
        'set_method': 'VideoLibrary.SetEpisodeDetails',
        'db_id': 'episodeid',
        'properties': EPISODE_PROPERTIES,
        'result': 'episodedetails'
    },
    'movie': {
        'get_method': 'VideoLibrary.GetMovieDetails',
        'set_method': 'VideoLibrary.SetMovieDetails',
        'db_id': 'movieid',
        'properties': MOVIE_PROPERTIES,
        'result': 'moviedetails'
    },
    'tvshow': {
        'get_method': 'VideoLibrary.GetTVShowDetails',
        'set_method': 'VideoLibrary.SetTVShowDetails',
        'db_id': 'tvshowid',
        'properties': TVSHOW_PROPERTIES,
        'result': 'tvshowdetails'
    },
    'episodes': {
        'get_method': 'VideoLibrary.GetEpisodes',
        'properties': EPISODE_PROPERTIES,
        'result': 'episodes'
    },
    'movies': {
        'get_method': 'VideoLibrary.GetMovies',
        'properties': MOVIE_PROPERTIES,
        'result': 'movies'
    },
    'tvshows': {
        'get_method': 'VideoLibrary.GetTVShows',
        'properties': TVSHOW_PROPERTIES,
        'result': 'tvshows'
    },
}

QUERY_LIMITS = {
    'start': 0,
    'end': constants.UNDEFINED
}

FILTER_SEARCH_TVSHOW = {
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
FILTER_NEXT_AIRED = {
    'field': 'airdate',
    'operator': 'after',
    'value': constants.UNDEFINED_STR
}
FILTER_UNWATCHED_NEXT_AIRED = {
    'and': [
        FILTER_UNWATCHED,
        FILTER_NEXT_AIRED
    ]
}

FILTER_SEARCH_EPISODE = {
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

FILTER_SEARCH_SET = {
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
        FILTER_SEARCH_SET,
        FILTER_NEXT_MOVIE
    ]
}
FILTER_UNWATCHED_UPNEXT_MOVIE = {
    'and': [
        FILTER_UNWATCHED,
        FILTER_SEARCH_SET,
        FILTER_NEXT_MOVIE
    ]
}

FILTER_SIMILAR = {
    'or': []
}
FILTER_SIMILAR_NOT_SAME = {
    'and': [
        FILTER_NOT_TITLE,
        FILTER_SIMILAR
    ]
}
FILTER_UNWATCHED_SIMILAR_NOT_SAME = {
    'and': [
        FILTER_UNWATCHED,
        FILTER_NOT_TITLE,
        FILTER_SIMILAR
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

_CACHE = {
    'playerid': None,
    'playlistid': None
}


def cache_invalidate():
    _CACHE.update(_CACHE.fromkeys(_CACHE))


def log(msg, level=utils.LOGDEBUG):
    """Log wrapper"""

    utils.log(msg, name=__name__, level=level)


def art_fallbacks(item=None, art=None, art_map=COMMON_ART_MAP, replace=True):  # pylint: disable=dangerous-default-value
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


def get_item_id(item):
    """Helper function to construct item dict with library dbid reference for
    use with params arguments of JSONRPC requests"""

    if not item:
        return {}

    db_id = item['db_id']
    media_type = item['media_type']

    db_type = JSON_MAP.get(media_type)
    if not db_type or not db_id:
        return {}

    return {
        db_type['db_id']: item['db_id']
    }


def play_kodi_item(item, resume=False):
    """Function to directly play a file from the Kodi library"""

    log('Playing from library: {0}'.format(item))

    item = get_item_id(item)
    utils.jsonrpc(
        method='Player.Open',
        params={'item': item},
        options={'resume': resume},
        no_response=True
    )


def queue_next_item(data=None, item=None):
    """Function to add next video to the UpNext queue"""

    next_item = (
        get_item_id(item) if not data
        else {'file': data['play_url']} if 'play_url' in data
        else None
    )

    if next_item:
        log('Adding to queue: {0}'.format(next_item))
        utils.jsonrpc(
            method='Playlist.Add',
            params={'playlistid': get_playlistid(), 'item': next_item},
            no_response=True
        )
    else:
        log('Nothing added to queue')

    return bool(next_item)


def reset_queue():
    """Function to remove the 1st item from the playlist, used by the UpNext
       queue for the video that was just played"""

    log('Removing previously played item from queue')
    utils.jsonrpc(
        method='Playlist.Remove',
        params={'playlistid': get_playlistid(), 'position': 0},
        no_response=True
    )
    return False


def dequeue_next_item():
    """Function to remove the 2nd item from the playlist, used by the UpNext
       queue for the next video to be played"""

    log('Removing unplayed next item from queue')
    utils.jsonrpc(
        method='Playlist.Remove',
        params={'playlistid': get_playlistid(), 'position': 1},
        no_response=True
    )
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
    # Unfortunately resuming from a playlist item does not seem to work...
    utils.jsonrpc(
        method='Player.Open',
        params={
            'item': {
                'playlistid': get_playlistid(),
                # Convert one indexed position to zero indexed position
                'position': position - 1
            }
        },
        options={'resume': resume},
        no_response=True
    )


def get_playlist_position(offset=0):
    """Function to get current playlist position and number of remaining
       playlist items, where the first item in the playlist is position 1"""

    # Use actual playlistid rather than xbmc.PLAYLIST_VIDEO as Kodi sometimes
    # plays video content in a music playlist
    playlistid = get_playlistid()
    if playlistid is None:
        return None, None

    playlist = xbmc.PlayList(playlistid)
    playlist_size = playlist.size()
    # Use 1 based index value for playlist position
    position = playlist.getposition() + 1 + offset

    # A playlist with only one element has no next item
    # PlayList().getposition() starts counting from zero
    if playlist_size > 1 and position <= playlist_size:
        log('playlistid: {0}, position - {1}/{2}'.format(
            playlistid, position, playlist_size
        ))
        return position, (playlist_size - position)
    return None, None


def get_from_playlist(position, properties, unwatched_only=False):
    """Function to get details of item in playlist, where the first item in the
       playlist is position 1"""

    result = utils.jsonrpc(
        method='Playlist.GetItems',
        params={
            'playlistid': get_playlistid(),
            # limits are zero indexed, position is one indexed
            'limits': {
                'start': position - 1,
                'end': -1 if unwatched_only else position
            },
            'properties': properties
        }
    )
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
        utils.jsonrpc(
            method='Player.Open',
            params={'item': {'file': play_url}},
            options={'resume': resume},
            no_response=True
        )
        return

    play_info = data.get('play_info')
    if play_info:
        log('Sending as {0} to plugin - {1}'.format(encoding, play_info))
        utils.event(
            message=data.get('id'),
            data=play_info,
            sender='upnextprovider',
            encoding=encoding
        )
        return

    log('No plugin data available for playback', utils.LOGWARNING)


def get_playerid(retry=3):
    """Function to get active player playerid"""

    # We don't need to get playerid every time, cache and reuse instead
    if _CACHE['playerid'] is not None:
        return _CACHE['playerid']

    # Sometimes Kodi gets confused and uses a music playlist for video content,
    # so get the first active player instead, default to video player. Wait 1s
    # and retry in case of delay in getting response.
    attempts_left = 1 + retry
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

    result = utils.jsonrpc(
        method='Player.GetProperties',
        params={
            'playerid': get_playerid(),
            'properties': ['playlistid'],
        }
    )
    playlistid = utils.get_int(
        result.get('result', {}), 'playlistid', PLAYER_PLAYLIST['video']
    )

    log('Selected playlistid: {0}'.format(playlistid))
    _CACHE['playlistid'] = playlistid
    return playlistid


def get_player_speed():
    """Function to get speed of active player"""

    result = utils.jsonrpc(
        method='Player.GetProperties',
        params={
            'playerid': get_playerid(),
            'properties': ['speed'],
        }
    )
    result = utils.get_int(result.get('result', {}), 'speed', 1)

    return result


def get_now_playing(properties, retry=3):
    """Function to get detail of currently playing item"""

    # Retry in case of delay in getting response.
    attempts_left = 1 + retry
    while attempts_left > 0:
        result = utils.jsonrpc(
            method='Player.GetItem',
            params={
                'playerid': get_playerid(retry=retry),
                'properties': properties,
            }
        )
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

    if item['media_type'] == 'episode':
        return get_next_episode_from_library(episode=item['details'], **kwargs)

    if item['media_type'] == 'movie':
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
        FILTER_NEXT_AIRED['value'] = utils.iso_datetime(episode['firstaired'])
        filters.append(FILTER_NEXT_AIRED)
    else:
        sort = SORT_EPISODE
        FILTER_THIS_SEASON['value'] = str(episode['season'])
        FILTER_NEXT_EPISODE['value'] = str(episode['episode'])
        filters.append(FILTER_UPNEXT_EPISODE)

    filters = {'and': filters}

    result = get_videos_from_library(
        media_type='episodes',
        limit=1,
        sort=sort,
        filters=filters,
        params={'tvshowid': episode.get('tvshowid', constants.UNDEFINED)}
    )

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

    if utils.get_int(movie, 'setid') <= 0:
        log('No next movie found, invalid movie setid', utils.LOGWARNING)
        return None

    (path, filename) = os.path.split(movie['file'])
    FILTER_NOT_FILE['value'] = filename
    FILTER_NOT_PATH['value'] = path
    filters = [FILTER_NOT_FILEPATH]

    FILTER_SEARCH_SET['value'] = movie['set']
    filters.append(FILTER_SEARCH_SET)

    if unwatched_only:
        filters.append(FILTER_UNWATCHED)

    if random:
        sort = SORT_RANDOM
    else:
        sort = SORT_YEAR
        FILTER_NEXT_MOVIE['value'] = str(movie['year'])
        filters.append(FILTER_NEXT_MOVIE)

    filters = {'and': filters}

    movie = get_videos_from_library(
        media_type='movies',
        limit=1,
        sort=sort,
        filters=filters
    )

    if not movie:
        log('No next movie found in library')
        return None

    log('Next movie from library: {0}'.format(movie))
    return movie


def get_from_library(media_type=None, db_id=constants.UNDEFINED, item=None):
    """Function to get video and collection details from Kodi library"""

    if item:
        media_type = item['media_type']
        db_id = item['db_id']

    if not media_type or db_id == constants.UNDEFINED:
        log('Video info not found in library, invalid dbid', utils.LOGWARNING)
        return None

    result, _ = get_details_from_library(media_type=media_type, db_id=db_id)

    if not result:
        log('Video info not found in library', utils.LOGWARNING)
        return None

    if media_type == 'episode':
        tvshow_details, _ = get_details_from_library(
            media_type='tvshow',
            db_id=result.get('tvshowid', constants.UNDEFINED)
        )

        if not tvshow_details:
            log('Show info not found in library', utils.LOGWARNING)
            return None
        tvshow_details.update(result)
        result = tvshow_details

    log('Info from library: {0}'.format(result))
    return result


def get_tvshowid(title):
    """Function to search Kodi library for tshowid by title"""

    FILTER_SEARCH_TVSHOW['value'] = title
    tvshow = get_videos_from_library(
        media_type='tvshows',
        limit=1,
        properties=[],
        filters=FILTER_SEARCH_TVSHOW
    )

    if not tvshow:
        log('tvshowid not found in library', utils.LOGWARNING)
        return constants.UNDEFINED

    tvshowid = utils.get_int(tvshow, 'tvshowid')
    log('Fetched show "{0}" tvshowid: {1}'.format(title, tvshowid))
    return tvshowid


def get_episodeid(tvshowid, season, episode):
    """Function to search Kodi library for episodeid by tvshowid, season, and
       episode"""

    FILTER_THIS_SEASON['value'] = str(season)
    FILTER_THIS_EPISODE['value'] = str(episode)

    result = get_videos_from_library(
        media_type='episodes',
        limit=1,
        properties=[],
        filters=FILTER_SEARCH_EPISODE,
        params={'tvshowid': tvshowid}
    )

    if not result:
        log('episodeid not found in library', utils.LOGWARNING)
        return constants.UNDEFINED

    episodeid = utils.get_int(result, 'episodeid')
    log('Fetched show {0} s{1}e{2} episodeid: {3}'.format(
        tvshowid, season, episode, episodeid
    ))
    return episodeid


def get_details_from_library(media_type=None,
                             db_id=constants.UNDEFINED,
                             item=None,
                             properties=None):
    """Function to retrieve video info details from Kodi library"""

    if item:
        media_type = item['media_type']
        db_id = item['db_id']

    if not media_type or db_id == constants.UNDEFINED:
        return None, None

    detail_type = JSON_MAP.get(media_type)
    if 'db_id' not in detail_type:
        detail_type = JSON_MAP.get(media_type[:-1])
    if not detail_type:
        return None, None

    if properties is None:
        properties = detail_type['properties']
    elif isinstance(properties, (set, frozenset)):
        properties = detail_type['properties'] | properties

    result = utils.jsonrpc(
        method=detail_type['get_method'],
        params={
            detail_type['db_id']: db_id,
            'properties': properties,
        }
    )

    result = result.get('result', {}).get(detail_type['result'])
    return result, detail_type


def handle_just_watched(item, reset_playcount=False, reset_resume=True):
    """Function to update playcount and resume point of just watched video"""

    result, detail_type = get_details_from_library(
        item=item, properties=['playcount', 'resume']
    )

    if result:
        initial_playcount = utils.get_int(item.get('details'), 'playcount', 0)
        current_playcount = utils.get_int(result, 'playcount', 0)
        current_resume = utils.get_int(result.get('resume'), 'position', 0)
    else:
        return

    params = {}

    # If Kodi has not updated playcount then UpNext will
    if reset_playcount:
        params['playcount'] = 0
    elif current_playcount == initial_playcount:
        current_playcount += 1
        params['playcount'] = current_playcount

    # If resume point has been saved then reset it
    if current_resume and reset_resume:
        params['resume'] = {'position': 0}

    # Only update library if playcount or resume point needs to change
    if params:
        params[detail_type['db_id']] = item['db_id']
        utils.jsonrpc(
            method=detail_type['set_method'],
            params=params,
            no_response=True
        )

    log('Library update: {0}{1}{2}{3}'.format(
        '{0}_id - {1}'.format(item['media_type'], item['db_id']),
        ', playcount - {0} to {1}'.format(initial_playcount, current_playcount)
        if 'playcount' in params else '',
        ', resume - {0} to 0'.format(current_resume)
        if 'resume' in params else '',
        '' if params else ', no change'
    ), utils.LOGDEBUG)


def get_upnext_episodes_from_library(limit=25,  # pylint: disable=too-many-locals
                                     next_season=True,
                                     unwatched_only=False):
    """Function to get in-progress and next episode details from Kodi library"""

    if next_season:
        filters = [
            FILTER_INPROGRESS,
            FILTER_WATCHED,
            (FILTER_UNWATCHED_NEXT_AIRED if unwatched_only
             else FILTER_NEXT_AIRED)
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

    inprogress = get_videos_from_library(
        media_type='episodes',
        limit=limit,
        sort=SORT_LASTPLAYED,
        filters=filters[0]
    )

    watched = get_videos_from_library(
        media_type='episodes',
        limit=limit,
        sort=SORT_LASTPLAYED,
        filters=filters[1]
    )

    episodes = utils.merge_iterable(
        inprogress, watched, sort='lastplayed', reverse=True
    )

    upnext_episodes = []
    tvshows = set()
    for episode in episodes:
        tvshowid = episode['tvshowid']
        if tvshowid in tvshows:
            continue

        if episode['resume']['position']:
            upnext_episode = episode
        else:
            FILTER_THIS_SEASON['value'] = str(episode['season'])
            FILTER_NEXT_EPISODE['value'] = str(episode['episode'])
            FILTER_NEXT_AIRED['value'] = utils.iso_datetime(
                episode['firstaired']
            )

            upnext_episode = get_videos_from_library(
                media_type='episodes',
                limit=1,
                sort=sort,
                filters=filters[2],
                params={'tvshowid': tvshowid}
            )

            if not upnext_episode:
                tvshows.add(tvshowid)
                continue

        # Restore current episode lastplayed for sorting of next-up episode
        upnext_episode['lastplayed'] = episode['lastplayed']

        art_fallbacks(upnext_episode, art_map=EPISODE_ART_MAP, replace=False)

        upnext_episodes.append(upnext_episode)
        tvshows.add(tvshowid)

    return upnext_episodes


def get_upnext_movies_from_library(limit=25,
                                   movie_sets=True,
                                   unwatched_only=False):
    """Function to get in-progress and next movie details from Kodi library"""

    inprogress = get_videos_from_library(
        media_type='movies',
        limit=limit,
        sort=SORT_LASTPLAYED,
        filters=FILTER_INPROGRESS
    )

    if movie_sets:
        watched = get_videos_from_library(
            media_type='movies',
            limit=limit,
            sort=SORT_LASTPLAYED,
            filters=FILTER_WATCHED
        )

        movies = utils.merge_iterable(
            inprogress, watched, sort='lastplayed', reverse=True
        )
    else:
        movies = inprogress

    filters = (
        FILTER_UNWATCHED_UPNEXT_MOVIE if unwatched_only
        else FILTER_UPNEXT_MOVIE
    )

    upnext_movies = []
    sets = set()
    for movie in movies:
        setid = movie['setid'] or constants.UNDEFINED
        if setid != constants.UNDEFINED and setid in sets:
            continue

        if movie['resume']['position']:
            upnext_movie = movie
        elif movie_sets and setid != constants.UNDEFINED:
            FILTER_SEARCH_SET['value'] = movie['set']
            FILTER_NEXT_MOVIE['value'] = str(movie['year'])

            upnext_movie = get_videos_from_library(
                media_type='movies',
                limit=1,
                sort=SORT_YEAR,
                filters=filters
            )

            if not upnext_movie:
                sets.add(setid)
                continue
        else:
            continue

        # Restore current movie lastplayed for sorting of next-up movie
        upnext_movie['lastplayed'] = movie['lastplayed']

        art_fallbacks(upnext_movie)

        upnext_movies.append(upnext_movie)
        sets.add(setid)

    return upnext_movies


def get_videos_from_library(media_type,  # pylint: disable=too-many-arguments
                            limit=25,
                            sort=None,
                            properties=None,
                            filters=None,
                            params=None,
                            process_art=False):
    """Function to get videos from Kodi library"""

    detail_type = JSON_MAP.get(media_type)
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

    videos = utils.jsonrpc(
        method=detail_type['get_method'],
        params=_params
    )
    videos = videos.get('result', {}).get(detail_type['result'], [])

    if process_art:
        utils.modify_iterable(art_fallbacks, videos)

    if videos and limit == 1:
        return videos[0]
    return videos


class InfoTagComparator(object):  # pylint: disable=too-few-public-methods
    __slots__ = (
        'fuzz',
        'genre',
        'set_name',
        'tag',
        'limit',
        'threshold',
    )

    def __init__(self, infotags, threshold=0, limit=25,  # pylint: disable=too-many-arguments
                 _frozenset=frozenset,
                 _get=dict.get,
                 _tokenise=utils.tokenise):

        self.fuzz = _tokenise([
            _get(infotags, 'plot'), _get(infotags, 'title')
        ])
        self.genre = _frozenset(_get(infotags, 'genre', []))
        self.set_name = _tokenise([_get(infotags, 'set')])
        self.tag = _tokenise([_get(infotags, 'tag')], split=False)
        self.threshold = threshold
        self.limit = limit

    def compare(self, infotags,  # pylint: disable=too-many-arguments
                _bit_length=int.bit_length,
                _frozenset=frozenset,
                _get=dict.get,
                _len=len,
                _tokenise=utils.tokenise):

        if self.limit <= 0:
            return None

        fuzz_stored = self.fuzz
        genre_stored = self.genre
        set_name_stored = self.set_name
        tag_stored = self.tag
        threshold = self.threshold

        similarity = 0

        if fuzz_stored:
            fuzz = _tokenise([_get(infotags, 'plot'), _get(infotags, 'title')])
            if fuzz:
                similarity += (
                    _len(fuzz & fuzz_stored) ** 2
                )

        if genre_stored:
            genre = _frozenset(_get(infotags, 'genre', []))
            if genre:
                similarity += 2 * (
                    _bit_length(_len(genre & genre_stored))
                    - _len(genre ^ genre_stored)
                )

        if set_name_stored:
            set_name = _tokenise([_get(infotags, 'set')])
            if set_name:
                similarity += 1000 * (
                    _len(set_name & set_name_stored) * 2
                    - _len(set_name - set_name_stored)
                )

        if tag_stored:
            tag = _tokenise([_get(infotags, 'tag')], split=False)
            if tag:
                similarity += 2 * (
                    _bit_length(_len(tag & tag_stored))
                )

        infotags['__similarity__'] = similarity

        if similarity > threshold:
            self.limit -= 1
            return similarity
        return threshold


def get_similar_from_library(media_type,  # pylint: disable=too-many-arguments, too-many-locals, too-many-branches
                             limit=25,
                             original=None,
                             db_id=constants.UNDEFINED,
                             unwatched_only=False,
                             sort=True,
                             threshold=0):
    """Function to search by db_id for similar videos from Kodi library"""

    if original:
        pass
    elif db_id == constants.UNDEFINED or db_id is None:
        original = get_videos_from_library(
            media_type=media_type,
            limit=1,
            sort=SORT_RANDOM,
            properties=RECOMMENDATION_PROPERTIES[media_type],
            filters=FILTER_WATCHED
        )
    else:
        original, _ = get_details_from_library(
            media_type=media_type,
            db_id=int(db_id),
            properties=RECOMMENDATION_PROPERTIES[media_type]
        )

    if not original:
        return None, []

    infotags = InfoTagComparator(original, threshold=threshold, limit=limit)
    if not (infotags.genre or infotags.set_name):
        return original, []

    FILTER_NOT_TITLE['value'] = original['title']
    FILTER_SIMILAR['or'] = [{
        'field': 'genre',
        'operator': 'is',
        'value': genre
    } for genre in infotags.genre]
    if infotags.set_name and media_type == 'movies':
        FILTER_SEARCH_SET['value'] = original['set']
        FILTER_SIMILAR['or'].append(FILTER_SEARCH_SET)

    selected = []
    chunk_size = limit * 10
    chunk_limit = {
        'start': 0,
        'end': chunk_size
    }
    while True:
        similar = get_videos_from_library(
            media_type=media_type,
            limit=chunk_limit,
            sort=SORT_RATING,
            properties=RECOMMENDATION_PROPERTIES[media_type],
            filters=(FILTER_UNWATCHED_SIMILAR_NOT_SAME if unwatched_only
                     else FILTER_SIMILAR_NOT_SAME)
        )

        idx = 0
        for idx, video in enumerate(similar):
            similarity = infotags.compare(video)
            if similarity is None:
                break
            if similarity:
                art_fallbacks(video)
        else:
            selected.extend(similar)
            if idx != chunk_size - 1:
                break
            chunk_limit['start'] += chunk_size
            chunk_limit['end'] += chunk_size
            continue
        selected.extend(similar[:idx])
        break

    if sort:
        return original, utils.merge_iterable(
            selected, sort='__similarity__', threshold=threshold, reverse=True
        )[:limit]
    return original, selected
