# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""Implements helper functions to interact with the Kodi library, player and
   playlist"""

from __future__ import absolute_import, division, unicode_literals
import os.path
import xbmc
import constants
import utils


EPISODE_PROPERTIES = {
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
}
EPISODE_ART_SUBSTITUTES = {
    'poster': ('season.poster', 'tvshow.poster'),
    'fanart': ('season.fanart', 'tvshow.fanart'),
    'landscape': ('season.landscape', 'tvshow.landscape'),
    'clearart': ('season.clearart', 'tvshow.clearart'),
    'banner': ('season.banner', 'tvshow.banner'),
    'clearlogo': ('season.clearlogo', 'tvshow.clearlogo'),
}

TVSHOW_PROPERTIES = {
    'title',
    'studio',
    'year',
    'plot',
    # 'cast',  # Not used, slow
    'rating',
    # 'ratings',  # Not used, slow
    # 'userrating',  # Not used
    # 'votes',  # Not used
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
}

MOVIE_PROPERTIES = {
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
    # 'showlink',  # Not used, slow
    # 'streamdetails',  # Not used, slow
    'top250',
    # 'votes',  # Not used
    'fanart',
    'thumbnail',
    'file',
    # 'sorttitle',  # Not used
    'resume',
    'setid',
    'dateadded',
    # 'tag',  # Not used, slow
    'art',
    # 'userrating',  # Not used
    # 'ratings',  # Not used, slow
    'premiered',
    # 'uniqueid',  # Not used, slow
}

PLAYER_PLAYLIST = {
    'video': xbmc.PLAYLIST_VIDEO,  # 1
    'audio': xbmc.PLAYLIST_MUSIC   # 0
}

JSON_DETAILS_MAP = {
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
}

_QUERY_LIMITS = {
    'start': 0,
    'end': constants.UNDEFINED
}
_QUERY_LIMIT_ONE = {
    'start': 0,
    'end': 1
}

_FILTER_SEARCH_TVSHOW = {
    'field': 'title',
    'operator': 'is',
    'value': constants.VALUE_TO_STR[constants.UNDEFINED]
}
_FILTER_NOT_FILE = {
    'field': 'filename',
    'operator': 'isnot',
    'value': constants.VALUE_TO_STR[constants.UNDEFINED]
}
_FILTER_NOT_PATH = {
    'field': 'path',
    'operator': 'isnot',
    'value': constants.VALUE_TO_STR[constants.UNDEFINED]
}
_FILTER_NOT_FILEPATH = {
    'or': [
        _FILTER_NOT_FILE,
        _FILTER_NOT_PATH
    ]
}

_FILTER_INPROGRESS = {
    'field': 'inprogress',
    'operator': 'true',
    'value': ''
}
_FILTER_WATCHED = {
    'field': 'playcount',
    'operator': 'greaterthan',
    'value': '0'
}
_FILTER_UNWATCHED = {
    'field': 'playcount',
    'operator': 'lessthan',
    'value': '1'
}
_FILTER_INPROGRESS_OR_WATCHED = {
    'or': [
        _FILTER_INPROGRESS,
        _FILTER_WATCHED
    ]
}

_FILTER_REGULAR_SEASON = {
    'field': 'season',
    'operator': 'greaterthan',
    'value': '0'
}
_FILTER_THIS_SEASON = {
    'field': 'season',
    'operator': 'is',
    'value': constants.VALUE_TO_STR[constants.UNDEFINED]
}
_FILTER_NEXT_SEASON = {
    'field': 'season',
    'operator': 'greaterthan',
    'value': constants.VALUE_TO_STR[constants.UNDEFINED]
}

_FILTER_THIS_EPISODE = {
    'field': 'episode',
    'operator': 'is',
    'value': constants.VALUE_TO_STR[constants.UNDEFINED]
}
_FILTER_NEXT_EPISODE = {
    'field': 'episode',
    'operator': 'greaterthan',
    'value': constants.VALUE_TO_STR[constants.UNDEFINED]
}

_FILTER_SEARCH_EPISODE = {
    'and': [
        _FILTER_THIS_SEASON,
        _FILTER_THIS_EPISODE
    ]
}
_FILTER_CURRENT_EPISODE = {
    'and': [
        _FILTER_REGULAR_SEASON,
        _FILTER_INPROGRESS_OR_WATCHED
    ]
}
_FILTER_UPNEXT_EPISODE = {
    'and': [
        _FILTER_THIS_SEASON,
        _FILTER_NEXT_EPISODE
    ]
}
_FILTER_UPNEXT_EPISODE_SEASON = {
    'or': [
        _FILTER_UPNEXT_EPISODE,
        _FILTER_NEXT_SEASON
    ]
}
_FILTER_UNWATCHED_UPNEXT_EPISODE_SEASON = {
    'and': [
        _FILTER_UNWATCHED,
        _FILTER_UPNEXT_EPISODE_SEASON
    ]
}

_FILTER_SEARCH_SET = {
    'field': 'set',
    'operator': 'is',
    'value': constants.VALUE_TO_STR[constants.UNDEFINED]
}
_FILTER_NEXT_MOVIE = {
    'field': 'year',
    'operator': 'after',
    'value': constants.VALUE_TO_STR[constants.UNDEFINED]
}
_FILTER_UPNEXT_MOVIE = {
    'and': [
        _FILTER_SEARCH_SET,
        _FILTER_NEXT_MOVIE
    ]
}
_FILTER_UNWATCHED_UPNEXT_MOVIE = {
    'and': [
        _FILTER_UNWATCHED,
        _FILTER_UPNEXT_MOVIE
    ]
}

_SORT_YEAR = {
    'method': 'year',
    'order': 'ascending'
}
_SORT_EPISODE = {
    'method': 'episode',
    'order': 'ascending'
}
_SORT_LASTPLAYED = {
    'method': 'lastplayed',
    'order': 'descending'
}
_SORT_RANDOM = {
    'method': 'random'
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


def get_item_id(item):
    """Helper function to construct item dict with library dbid reference for
    use with params arguments of JSONRPC requests"""

    if not item:
        return {}

    db_id = item['db_id']
    media_type = item['media_type']

    db_type = JSON_DETAILS_MAP.get(media_type)
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

    next_item = {
        'file': data['play_url']
    } if data and 'play_url' in data else get_item_id(item)

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


def play_playlist_item(position=0, resume=False):
    """Function to play episode in playlist"""

    if position == 'next':
        position = get_playlist_position()
    log('Playing from playlist position: {0}'.format(position))

    # JSON Player.Open can be too slow but is needed if resuming is enabled
    # Unfortunately resuming from a playlist item does not seem to work...
    utils.jsonrpc(
        method='Player.Open',
        params={
            'item': {'playlistid': get_playlistid(), 'position': position}
        },
        options={'resume': resume},
        no_response=True
    )


def get_playlist_position():
    """Function to get current playlist playback position, where the first item
       in the playlist is position 1"""

    # Use actual playlistid rather than xbmc.PLAYLIST_VIDEO as Kodi sometimes
    # plays video content in a music playlist
    playlistid = get_playlistid()
    if playlistid is None:
        return None

    playlist = xbmc.PlayList(playlistid)
    playlist_size = playlist.size()
    # Use 1 based index value for playlist position
    position = playlist.getposition() + 1

    # A playlist with only one element has no next item
    # PlayList().getposition() starts counting from zero
    if playlist_size > 1 and position < playlist_size:
        log('playlistid: {0}, position - {1}/{2}'.format(
            playlistid, position, playlist_size
        ))
        return position
    return None


def get_from_playlist(position, properties, unwatched_only=False):
    """Function to get details of item in playlist"""

    result = utils.jsonrpc(
        method='Playlist.GetItems',
        params={
            'playlistid': get_playlistid(),
            # limits are zero indexed, position is one indexed
            'limits': {
                'start': position,
                'end': -1 if unwatched_only else position + 1
            },
            'properties': properties
        }
    )
    items = result.get('result', {}).get('items')

    # Get first unwatched item in the list of playlist entries
    if unwatched_only and items:
        position_offset, item = next(
            (
                (idx, item) for idx, item in enumerate(items)
                if utils.get_int(item, 'playcount') < 1
            ),
            (0, None)
        )
        position += position_offset
    # Or just get the first item in the list of playlist entries
    else:
        item = items[0] if items else None

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

    result = [
        player for player in result
        if player.get('type', 'video') in PLAYER_PLAYLIST
    ]

    playerid = (
        utils.get_int(result[0], 'playerid') if result
        else constants.UNDEFINED
    )

    if playerid == constants.UNDEFINED:
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
    _FILTER_NOT_FILE['value'] = filename
    _FILTER_NOT_PATH['value'] = path
    filters = [
        # Check that both next filename and path are different to current
        # to deal with different file naming schemes e.g.
        # Season 1/Episode 1.mkv
        # Season 1/Episode 1/video.mkv
        # Season 1/Episode 1-2-3.mkv
        _FILTER_NOT_FILEPATH
    ]

    if unwatched_only:
        # Exclude watched episodes
        filters.append(_FILTER_UNWATCHED)

    if random:
        sort = _SORT_RANDOM
    else:
        sort = _SORT_EPISODE
        current_season = str(episode['season'])
        _FILTER_THIS_SEASON['value'] = current_season
        _FILTER_NEXT_SEASON['value'] = current_season
        _FILTER_NEXT_EPISODE['value'] = str(episode['episode'])
        # Next episode in current season or first episode in next season
        filters.append(
            _FILTER_UPNEXT_EPISODE_SEASON if next_season
            else _FILTER_UPNEXT_EPISODE
        )

    filters = {'and': filters}

    result = utils.jsonrpc(
        method='VideoLibrary.GetEpisodes',
        params={
            'tvshowid': episode.get('tvshowid', constants.UNDEFINED),
            'properties': EPISODE_PROPERTIES,
            'sort': sort,
            'limits': _QUERY_LIMIT_ONE,
            'filter': filters
        }
    )
    result = result.get('result', {}).get('episodes')

    if not result:
        log('No next episode found in library')
        return None

    log('Next episode from library: {0}'.format(result[0]))
    # Update current episode details dict, containing tvshow details, with next
    # episode details. Surprisingly difficult to retain backwards compatibility
    # episode = episode | result[0]       # Python > v3.9
    # episode = {**episode, **result[0]}  # Python > v3.5
    episode = dict(episode, **result[0])  # Python > v2.7
    return episode


def get_next_movie_from_library(movie=constants.UNDEFINED,
                                unwatched_only=False,
                                random=False):
    """Function to get details of next movie in set from Kodi library"""

    if not movie or movie == constants.UNDEFINED:
        log('No next movie found, current movie not in library',
            utils.LOGWARNING)
        return None

    if not movie['setid'] or movie['setid'] != constants.UNDEFINED:
        log('No next movie found, invalid movie setid', utils.LOGWARNING)
        return None

    (path, filename) = os.path.split(movie['file'])
    _FILTER_NOT_FILE['value'] = filename
    _FILTER_NOT_PATH['value'] = path
    filters = [_FILTER_NOT_FILEPATH]

    _FILTER_SEARCH_SET['value'] = movie['set']
    filters.append(_FILTER_SEARCH_SET)

    if unwatched_only:
        filters.append(_FILTER_UNWATCHED)

    if random:
        sort = _SORT_RANDOM
    else:
        sort = _SORT_YEAR
        _FILTER_NEXT_MOVIE['value'] = str(movie['year'])
        filters.append(_FILTER_NEXT_MOVIE)

    filters = {'and': filters}

    result = utils.jsonrpc(
        method='VideoLibrary.GetMovies',
        params={
            'properties': MOVIE_PROPERTIES,
            'sort': sort,
            'limits': _QUERY_LIMIT_ONE,
            'filter': filters
        }
    )
    result = result.get('result', {}).get('movies', [])

    if not result:
        log('No next movie found in library')
        return None

    movie = result[0]
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

    _FILTER_SEARCH_TVSHOW['value'] = title
    result = utils.jsonrpc(
        method='VideoLibrary.GetTVShows',
        params={
            'properties': [],
            'limits': _QUERY_LIMIT_ONE,
            'filter': _FILTER_SEARCH_TVSHOW
        }
    )
    result = result.get('result', {}).get('tvshows')

    if not result:
        log('tvshowid not found in library', utils.LOGWARNING)
        return constants.UNDEFINED

    tvshowid = utils.get_int(result[0], 'tvshowid')
    log('Fetched show "{0}" tvshowid: {1}'.format(title, tvshowid))
    return tvshowid


def get_episodeid(tvshowid, season, episode):
    """Function to search Kodi library for episodeid by tvshowid, season, and
       episode"""

    _FILTER_THIS_SEASON['value'] = str(season)
    _FILTER_THIS_EPISODE['value'] = str(episode)

    result = utils.jsonrpc(
        method='VideoLibrary.GetEpisodes',
        params={
            'tvshowid': tvshowid,
            'properties': [],
            'limits': _QUERY_LIMIT_ONE,
            'filter': _FILTER_SEARCH_EPISODE
        }
    )
    result = result.get('result', {}).get('episodes')

    if not result:
        log('episodeid not found in library', utils.LOGWARNING)
        return constants.UNDEFINED

    episodeid = utils.get_int(result[0], 'episodeid')
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

    detail_type = JSON_DETAILS_MAP.get(media_type)
    if not detail_type:
        return None, None

    result = utils.jsonrpc(
        method=detail_type['get_method'],
        params={
            detail_type['db_id']: db_id,
            'properties': (
                properties if properties else detail_type['properties']
            ),
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
        actual_playcount = utils.get_int(result, 'playcount', 0)
        actual_resume = utils.get_int(result.get('resume'), 'position', 0)
    else:
        return

    params = {}

    # If Kodi has not updated playcount then UpNext will
    if reset_playcount:
        playcount = -1
    if reset_playcount or actual_playcount == playcount:
        playcount += 1
        params['playcount'] = playcount

    # If resume point has been saved then reset it
    if actual_resume and reset_resume:
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
        ', playcount - {0} to {1}'.format(actual_playcount, playcount)
        if 'playcount' in params else '',
        ', resume - {0} to 0'.format(actual_resume)
        if 'resume' in params else '',
        '' if params else ', no change'
    ), utils.LOGDEBUG)


def get_upnext_episodes_from_library(limit=25):
    """Function to get in-progress and next episode details from Kodi library"""

    _QUERY_LIMITS['end'] = limit
    inprogress = utils.jsonrpc(
        method='VideoLibrary.GetTVShows',
        params={
            'properties': [],
            'sort': _SORT_LASTPLAYED,
            'limits': _QUERY_LIMITS,
            'filter': _FILTER_INPROGRESS
        }
    )
    inprogress = inprogress.get('result', {}).get('tvshows', [])

    upnext_episodes = []
    for tvshow in inprogress:
        current_episode = utils.jsonrpc(
            method='VideoLibrary.GetEpisodes',
            params={
                'tvshowid': tvshow['tvshowid'],
                'properties': EPISODE_PROPERTIES,
                'sort': _SORT_LASTPLAYED,
                'limits': _QUERY_LIMIT_ONE,
                'filter': _FILTER_CURRENT_EPISODE
            }
        )
        current_episode = current_episode.get('result', {}).get('episodes')

        if not current_episode:
            continue
        if current_episode[0]['resume']['position']:
            upnext_episode = current_episode
        else:
            current_season = str(current_episode[0]['season'])
            _FILTER_THIS_SEASON['value'] = current_season
            _FILTER_NEXT_SEASON['value'] = current_season
            _FILTER_NEXT_EPISODE['value'] = str(current_episode[0]['episode'])

            upnext_episode = utils.jsonrpc(
                method='VideoLibrary.GetEpisodes',
                params={
                    'tvshowid': tvshow['tvshowid'],
                    'properties': EPISODE_PROPERTIES,
                    'sort': _SORT_EPISODE,
                    'limits': _QUERY_LIMIT_ONE,
                    'filter': _FILTER_UNWATCHED_UPNEXT_EPISODE_SEASON
                }
            )
            upnext_episode = upnext_episode.get('result', {}).get('episodes')

        if not upnext_episode:
            continue

        # Restore current episode lastplayed for sorting of next-up episode
        upnext_episode[0]['lastplayed'] = current_episode[0]['lastplayed']

        art = upnext_episode[0].get('art')
        if art:
            art_types = frozenset(art.keys())
            for art_type, art_substitutes in EPISODE_ART_SUBSTITUTES.items():
                if art_type in art_types:
                    continue
                for art_substitute in art_substitutes:
                    if art_substitute in art_types:
                        art[art_type] = art[art_substitute]
                        break
            upnext_episode[0]['art'] = art

        upnext_episodes += upnext_episode

    return upnext_episodes


def get_upnext_movies_from_library(limit=25):
    """Function to get in-progress and next movie details from Kodi library"""

    _QUERY_LIMITS['end'] = limit
    inprogress = utils.jsonrpc(
        method='VideoLibrary.GetMovies',
        params={
            'properties': MOVIE_PROPERTIES,
            'sort': _SORT_LASTPLAYED,
            'limits': _QUERY_LIMITS,
            'filter': _FILTER_INPROGRESS
        }
    )
    inprogress = inprogress.get('result', {}).get('movies', [])

    watched = utils.jsonrpc(
        method='VideoLibrary.GetMovies',
        params={
            'properties': MOVIE_PROPERTIES,
            'sort': _SORT_LASTPLAYED,
            'limits': _QUERY_LIMITS,
            'filter': _FILTER_WATCHED
        }
    )
    watched = watched.get('result', {}).get('movies', [])

    inprogress_or_watched = utils.merge_and_sort(
        inprogress, watched, key='lastplayed', reverse=True
    )

    upnext_movies = []
    for movie in inprogress_or_watched:
        if movie['resume']['position']:
            upnext_movie = [movie]
        elif movie['setid'] and movie['setid'] != constants.UNDEFINED:
            _FILTER_SEARCH_SET['value'] = movie['set']
            _FILTER_NEXT_MOVIE['value'] = str(movie['year'])

            upnext_movie = utils.jsonrpc(
                method='VideoLibrary.GetMovies',
                params={
                    'properties': MOVIE_PROPERTIES,
                    'sort': _SORT_YEAR,
                    'limits': _QUERY_LIMIT_ONE,
                    'filter': _FILTER_UNWATCHED_UPNEXT_MOVIE
                }
            )
            upnext_movie = upnext_movie.get('result', {}).get('movies', [])
        else:
            continue

        if upnext_movie:
            # Restore current movie lastplayed for sorting of next-up movie
            upnext_movie[0]['lastplayed'] = movie['lastplayed']
            upnext_movies += upnext_movie

    return upnext_movies
