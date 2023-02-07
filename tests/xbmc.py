# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
''' This file implements the Kodi xbmc module, either using stubs or alternative functionality '''

# pylint: disable=invalid-name,no-self-use

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import json
import os
import random
import sys
import threading
from datetime import datetime
from time import sleep as time_sleep
from weakref import WeakValueDictionary

import dateutil.parser

from dummydata import LIBRARY
from statichelper import from_bytes
from xbmcextra import (
    __KODI_MATRIX__,
    __KODI_NEXUS__,
    global_settings,
    import_language,
)

if __KODI_MATRIX__:
    LOGDEBUG = 0
    LOGINFO = 1
    LOGWARNING = 2
    LOGERROR = 3
    LOGFATAL = 4
    LOGNONE = 5
    _LOG_LEVELS = {
        LOGDEBUG: 'DEBUG',
        LOGINFO: 'INFO',
        LOGWARNING: 'WARNING',
        LOGERROR: 'ERROR',
        LOGFATAL: 'FATAL',
        LOGNONE: 'NONE'
    }
else:
    LOGDEBUG = 0
    LOGINFO = 1
    LOGNOTICE = 2
    LOGWARNING = 3
    LOGERROR = 4
    LOGSEVERE = 5
    LOGFATAL = 6
    LOGNONE = 7
    _LOG_LEVELS = {
        LOGDEBUG: 'DEBUG',
        LOGINFO: 'INFO',
        LOGNOTICE: 'NOTICE',
        LOGWARNING: 'WARNING',
        LOGERROR: 'ERROR',
        LOGSEVERE: 'SEVERE',
        LOGFATAL: 'FATAL',
        LOGNONE: 'NONE'
    }

PLAYLIST_MUSIC = 0
PLAYLIST_VIDEO = 1
_PLAYLIST_TYPE = random.randint(PLAYLIST_MUSIC, PLAYLIST_VIDEO)
_PLAYER_TYPES = [
    [{'type': 'audio', 'playerid': PLAYLIST_MUSIC}],
    [{'type': 'video', 'playerid': PLAYLIST_VIDEO}],
]
_PLAYLIST = {
    PLAYLIST_MUSIC: {'position': 0, 'playlist': [{'file': 'dummy'}]},
    PLAYLIST_VIDEO: {'position': 0, 'playlist': [{'file': 'dummy'}]},
}

_INFO_LABELS = {
    'System.BuildVersion': (
        '20.0' if __KODI_NEXUS__
        else '19.4' if __KODI_MATRIX__
        else '18.9'
    ),
    'Player.Process(VideoWidth)': '1,920',
    'Player.Process(VideoHeight)': '1,080',
    'Player.Process(VideoDAR)': '1.78'
}

_REGIONS = {
    'datelong': '%A, %d %B %Y',
    'dateshort': '%Y-%m-%d',
    'time': '%I:%M %p'
}

_GLOBAL_SETTINGS = global_settings()
_PO = import_language(language=_GLOBAL_SETTINGS.get('locale.language'))


class Actor(object):
    def __init__(self, name='', role='', order=0, thumbnail=''):
        self.name = name
        self.role = role
        self.order = order
        self.thumbnail = thumbnail

    def getName(self):
        return self.name

    def getRole(self):
        return self.role

    def getOrder(self):
        return self.order

    def getThumbnail(self):
        return self.thumbnail

    def setName(self, name=''):
        self.name = name

    def setRole(self, role=''):
        self.role = role

    def setOrder(self, order=0):
        self.order = order

    def setThumbnail(self, thumbnail=''):
        self.thumbnail = thumbnail


class Keyboard(object):
    ''' A stub implementation of the xbmc Keyboard class '''

    def __init__(self, line='', heading=''):
        ''' A stub constructor for the xbmc Keyboard class '''

    def doModal(self, autoclose=0):
        ''' A stub implementation for the xbmc Keyboard class doModal() method '''

    def isConfirmed(self):
        ''' A stub implementation for the xbmc Keyboard class isConfirmed() method '''
        return True

    def getText(self):
        ''' A stub implementation for the xbmc Keyboard class getText() method '''
        return 'test'


class Monitor(object):
    ''' A stub implementation of the xbmc Monitor class '''

    __slots__ = ('__weakref__', )

    _instances = WeakValueDictionary()
    _aborted = threading.Event()

    def __new__(cls):
        ''' A stub constructor for the xbmc Monitor class '''

        self = super(Monitor, cls).__new__(cls)

        if not cls._instances:
            abort_timer = threading.Thread(target=self._timer)  # pylint: disable=protected-access
            abort_timer.daemon = True
            abort_timer.start()

        key = id(self)
        cls._instances[key] = self
        return self

    def __del__(self):
        key = id(self)
        if key in Monitor._instances:
            del Monitor._instances[key]

    def _timer(self):
        if __KODI_NEXUS__:
            abort_time = 120
        elif __KODI_MATRIX__:
            abort_time = 90
        else:
            abort_time = random.randint(90, 120)
        log('Test exit in {0}s'.format(abort_time), LOGINFO)

        Monitor._aborted.wait(abort_time)
        Monitor._aborted.set()
        try:
            sys.exit()
        except SystemExit:
            pass

    def abortRequested(self):
        ''' A stub implementation for the xbmc Monitor class abortRequested() method '''
        return Monitor._aborted.is_set()

    def waitForAbort(self, timeout=None):
        ''' A stub implementation for the xbmc Monitor class waitForAbort() method '''
        try:
            Monitor._aborted.wait(timeout)
        except KeyboardInterrupt:
            Monitor._aborted.set()
            try:
                sys.exit()
            except SystemExit:
                pass
        except SystemExit:
            Monitor._aborted.set()

        return Monitor._aborted.is_set()


class Player(object):
    ''' A stub implementation of the xbmc Player class '''
    is_playing = False
    file = ''
    time = 0.0
    duration = 0

    def __init__(self):
        ''' A stub constructor for the xbmc Player class '''
        self._count = 0

    def play(self, item='', listitem=None, windowed=False, startpos=-1):  # pylint: disable=unused-argument
        ''' A stub implementation for the xbmc Player class play() method '''
        Player.file = item
        Player.is_playing = True
        Player.time = 0.0
        Player.duration = 0

    def playnext(self):
        ''' A stub implementation for the xbmc Player class playnext() method '''
        return

    def stop(self):
        ''' A stub implementation for the xbmc Player class stop() method '''
        Player.file = ''
        Player.is_playing = False
        Player.time = 0.0
        Player.duration = 0

    def isExternalPlayer(self):
        ''' A stub implementation for the xbmc Player class isExternalPlayer() method '''
        return False

    def getPlayingFile(self):
        ''' A stub implementation for the xbmc Player class getPlayingFile() method '''
        if not Player.is_playing:
            raise RuntimeError
        return Player.file

    def isPlaying(self):
        ''' A stub implementation for the xbmc Player class isPlaying() method '''
        # Return correct value four times out of five
        if random.randint(1, 5) == 5:
            return False
        return Player.is_playing

    def seekTime(self, seekTime):  # pylint: disable=unused-argument
        ''' A stub implementation for the xbmc Player class seekTime() method '''
        return

    def showSubtitles(self, bVisible):  # pylint: disable=unused-argument
        ''' A stub implementation for the xbmc Player class showSubtitles() method '''
        return

    def getTotalTime(self):
        ''' A stub implementation for the xbmc Player class getTotalTime() method '''
        if not Player.is_playing:
            raise RuntimeError
        return Player.duration

    def getTime(self):
        ''' A stub implementation for the xbmc Player class getTime() method '''
        if not Player.is_playing:
            raise RuntimeError
        return Player.time

    def getVideoInfoTag(self):
        ''' A stub implementation for the xbmc Player class getVideoInfoTag() method '''
        return InfoTagVideo()


class PlayList(object):
    ''' A stub implementation of the xbmc PlayList class '''

    def __init__(self, playList):
        ''' A stub constructor for the xbmc PlayList class '''
        self.playlist_type = playList

    def clear(self):
        _PLAYLIST[self.playlist_type]['playlist'].clear()

    def getposition(self):
        ''' A stub implementation for the xbmc PlayList class getposition() method '''
        return _PLAYLIST[self.playlist_type]['position']

    def size(self):
        ''' A stub implementation for the xbmc PlayList class size() method '''
        return len(_PLAYLIST[self.playlist_type]['playlist'])


class InfoTagVideo(object):  # pylint: disable=too-many-public-methods
    ''' A stub implementation of the xbmc InfoTagVideo class '''

    def __init__(self, tags=None):
        ''' A stub constructor for the xbmc InfoTagVideo class '''
        self._tags = tags if tags else {}

    def getDbId(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getDbId() method '''
        return self._tags.get('dbid', -1)

    def getTitle(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getTitle() method '''
        return self._tags.get('title', '')

    def getSeason(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getSeason() method '''
        return self._tags.get('season', -1)

    def getEpisode(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getEpisode() method '''
        return self._tags.get('episode', -1)

    def getTVShowTitle(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getTVShowTitle() method '''
        return self._tags.get('tvshowtitle', '')

    def getFirstAired(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getFirstAired() method '''
        return self._tags.get('aired', '')

    def getFirstAiredAsW3C(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getFirstAiredAsW3C() method '''
        return self._tags.get('aired', '')

    def getPremiered(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getPremiered() method '''
        return self._tags.get('premiered', '')

    def getPremieredAsW3C(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getPremieredAsW3C() method '''
        return self._tags.get('premiered', '')

    def getYear(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getYear() method '''
        return self._tags.get('year', 1900)

    def getDuration(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getDuration() method '''
        return self._tags.get('duration', 0)

    def getPlotOutline(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getPlotOutline() method '''
        return self._tags.get('plotoutline', '')

    def getPlot(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getPlot() method '''
        return self._tags.get('plot', '')

    def getUserRating(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getUserRating() method '''
        return self._tags.get('userrating', 0)

    def getPlayCount(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getPlayCount() method '''
        return self._tags.get('playcount', 0)

    def getRating(self, _type='_default'):
        ''' A stub implementation for the xbmc InfoTagVideo class getRating() method '''
        ratings = self._tags.get('ratings', {})
        rating = ratings.get(_type, 0.0)
        return rating

    def getMediaType(self):
        ''' A stub implementation for the xbmc InfoTagVideo class getMediaType() method '''
        return self._tags.get('mediatype', '')

    def setSortEpisode(self, value):
        self._tags['sortepisode'] = value

    def setDbId(self, value):
        self._tags['dbid'] = value

    def setYear(self, value):
        self._tags['year'] = value

    def setEpisode(self, value):
        self._tags['episode'] = value

    def setSeason(self, value):
        self._tags['season'] = value

    def setSortSeason(self, value):
        self._tags['sortseason'] = value

    def setEpisodeGuide(self, value):
        self._tags['episodeguide'] = value

    def setTop250(self, value):
        self._tags['top250'] = value

    def setSetId(self, value):
        self._tags['setid'] = value

    def setTrackNumber(self, value):
        self._tags['tracknumber'] = value

    def setRating(self, rating, votes=0, _type='_default', isdefault=True):
        ratings = self._tags.get('ratings', {})
        rating = {
            'rating': rating,
            'votes': votes,
            'isdefault': isdefault
        }
        ratings[_type] = rating
        if isdefault:
            ratings['_default'] = rating

    def setUserRating(self, value):
        self._tags['userrating'] = value

    def setPlaycount(self, value):
        self._tags['playcount'] = value

    def setMpaa(self, value):
        self._tags['mpaa'] = value

    def setPlot(self, value):
        self._tags['plot'] = value

    def setPlotOutline(self, value):
        self._tags['plotoutline'] = value

    def setTitle(self, value):
        self._tags['title'] = value

    def setOriginalTitle(self, value):
        self._tags['originaltitle'] = value

    def setSortTitle(self, value):
        self._tags['sorttitle'] = value

    def setTagLine(self, value):
        self._tags['tagline'] = value

    def setTvShowTitle(self, value):
        self._tags['tvshowtitle'] = value

    def setTvShowStatus(self, value):
        self._tags['tvshowstatus'] = value

    def setGenres(self, value):
        self._tags['genres'] = value

    def setCountries(self, value):
        self._tags['countries'] = value

    def setDirectors(self, value):
        self._tags['directors'] = value

    def setStudios(self, value):
        self._tags['studios'] = value

    def setWriters(self, value):
        self._tags['writers'] = value

    def setDuration(self, value):
        self._tags['duration'] = value

    def setResumePoint(self, time, totaltime=0):
        self._tags['resumetime'] = time
        self._tags['resumetimetotal'] = totaltime

    def setPremiered(self, value):
        self._tags['premiered'] = value

    def setSet(self, value):
        self._tags['set'] = value

    def setSetOverview(self, value):
        self._tags['setoverview'] = value

    def setTags(self, value):
        self._tags['tags'] = value

    def setProductionCode(self, value):
        self._tags['productioncode'] = value

    def setFirstAired(self, value):
        self._tags['firstaired'] = value

    def setLastPlayed(self, value):
        self._tags['lastplayed'] = value

    def setAlbum(self, value):
        self._tags['album'] = value

    def setVotes(self, value):
        self._tags['votes'] = value

    def setTrailer(self, value):
        self._tags['trailer'] = value

    def setPath(self, value):
        self._tags['path'] = value

    def setIMDBNumber(self, value):
        self._tags['imdbnumber'] = value

    def setDateAdded(self, value):
        self._tags['dateadded'] = value

    def setMediaType(self, value):
        self._tags['mediatype'] = value

    def setShowLinks(self, value):
        self._tags['showlinks'] = value

    def setArtists(self, value):
        self._tags['artists'] = value

    def setCast(self, value):
        self._tags['cast'] = value


class RenderCapture(object):
    ''' A stub implementation of the xbmc RenderCapture class '''

    def __init__(self):
        ''' A stub constructor for the xbmc RenderCapture class '''
        self._width = 0
        self._height = 0

    def capture(self, width, height):
        ''' A stub implementation for the xbmc RenderCapture class capture() method '''
        self._width = width
        self._height = height

    def getImage(self, msecs=None):  # pylint: disable=unused-argument
        ''' A stub implementation for the xbmc RenderCapture class getImage() method '''
        return bytearray((
            random.getrandbits(8) if i % 4 != 3 else 255
            for i in range(self._width * self._height * 4)
        ))


def executebuiltin(string, wait=False):  # pylint: disable=unused-argument
    ''' A stub implementation of the xbmc executebuiltin() function '''
    return


def _filter_walker(haystacks, needles):
    found_needles = {}
    target = None
    if isinstance(needles, tuple):
        needles = list(needles)
    if not isinstance(needles, list):
        needles = [needles, ]
    if len(needles) == 1:
        target = needles[0]

    for stack in haystacks:
        if isinstance(haystacks, dict) and haystacks[stack] in needles:
            needle = haystacks[stack]
            found_needles[needle] = haystacks
            needles.remove(needle)
            return found_needles, needles

        if isinstance(stack, dict):
            found_needle, needles = _filter_walker(stack, needles)
            if found_needle:
                found_needles.update(found_needle)

        elif isinstance(haystacks[stack], (dict, list)):
            found_needle, needles = _filter_walker(haystacks[stack], needles)
            if found_needle:
                found_needles.update(found_needle)

        if not needles:
            break

    if target is not None:
        return found_needles.get(target), needles
    return found_needles, needles


def _application_getproperties(params):
    if params.get('properties') == ['version']:
        return json.dumps({
            'id': 1,
            'jsonrpc': '2.0',
            'result': {'version': {'major': (
                20 if __KODI_NEXUS__
                else 19 if __KODI_MATRIX__
                else 18
            )}}
        })
    return False


def _settings_getsettingvalue(params):
    key = params.get('setting')
    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'result': {'value': _GLOBAL_SETTINGS.get(key)}
    })


def _player_getactiveplayers(params):  # pylint: disable=unused-argument
    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'result': _PLAYER_TYPES[_PLAYLIST_TYPE]
    })


def _player_getproperties(params):
    if params.get('properties') == ['speed']:
        return json.dumps({
            'id': 1,
            'jsonrpc': '2.0',
            'result': {'speed': random.randint(0, 1)}
        })
    if params.get('properties') == ['playlistid']:
        return json.dumps({
            'id': 1,
            'jsonrpc': '2.0',
            'result': {'playlistid': _PLAYLIST_TYPE}
        })
    return False


def _player_getitem(params):  # pylint: disable=unused-argument
    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'result': {'item': LIBRARY['episodes'][0]}
    })


def _videolibrary_gettvshows(params):
    filters = params.get('filter')
    # sort = params.get('sort')
    limits = params.get('limits')

    if not filters:
        return False

    filters, _ = _filter_walker(
        filters,
        ['title', 'playcount', 'inprogress', 'genre']
    )
    title = filters.get('title')
    watched = filters.get('playcount', {'operator': 'greaterthan', 'value': -1})
    inprogress = filters.get('inprogress')
    genres = filters.get('genre', {})

    tvshows = []
    if title:
        tvshows = [
            tvshow for tvshow in LIBRARY['tvshows'].values()
            if tvshow.get('title', '') == title.get('value')
        ]
    elif inprogress:
        tvshows = [
            tvshow for tvshow in LIBRARY['tvshows'].values()
            if tvshow.get('playcount', 0) < 1
            and tvshow.get('watchedepisodes', 0) < tvshow.get('episode', 0)
        ]
    elif watched:
        tvshows = [
            tvshow for tvshow in LIBRARY['tvshows'].values()
            if (watched.get('operator') == 'greaterthan' and tvshow.get('playcount', 0) > int(watched.get('value'))
                or watched.get('operator') == 'lessthan' and tvshow.get('playcount', 0) < int(watched.get('value')))
            and (not genres.get('value') or not set(genres.get('value')).isdisjoint(tvshow.get('genre', [])))
        ]
    else:
        return False

    if limits and tvshows:
        start = limits['start']
        end = limits['end']
        if end == -1:
            end = len(tvshows)
        tvshows = tvshows[start:end]

    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'result': {'tvshows': tvshows}
    })


def _videolibrary_getepisodes(params):
    filters = params.get('filter')
    tvshowid = params.get('tvshowid')
    # sort = params.get('sort')
    limits = params.get('limits')

    if not filters:
        return False

    filters, _ = _filter_walker(
        filters,
        ['season', 'episode', 'airdate', 'playcount', 'inprogress']
    )
    season = filters.get('season')
    episode_number = filters.get('episode')
    air_date = filters.get('airdate')
    watched = filters.get('playcount')
    inprogress = filters.get('inprogress')

    episodes = []
    if tvshowid is None:
        if watched is not None and watched.get('operator') == 'greaterthan':
            episodes = [
                episode for episode in LIBRARY['episodes']
                if episode.get('playcount', 0) > int(watched.get('value'))
            ]
        elif inprogress is not None:
            episodes = [
                episode for episode in LIBRARY['episodes']
                if episode.get('resume', {}).get('position', 0) > 0
                and episode.get('playcount', 0) < 1
            ]
    elif season is not None and episode_number is not None:
        episodes = [
            episode for episode in LIBRARY['episodes']
            if episode.get('tvshowid', -1) == tvshowid
            and episode.get('season', -1) == int(season.get('value'))
            and episode.get('episode', -1) >= int(episode_number.get('value'))
        ]
        if episodes and episode_number.get('operator') == 'greaterthan':
            episodes = episodes[1:]
    elif air_date:
        episodes = [
            episode for episode in LIBRARY['episodes']
            if episode.get('tvshowid', -1) == tvshowid
            and (dateutil.parser.parse(episode.get('firstaired', ''))
                 >= dateutil.parser.parse(air_date.get('value', '')))
        ]
        if episodes and air_date.get('operator') == 'after':
            episodes = episodes[1:]
    else:
        return False

    if limits and episodes:
        start = limits['start']
        end = limits['end']
        if end == -1:
            end = len(episodes)
        episodes = episodes[start:end]

    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'result': {'episodes': episodes}
    })


def _videolibrary_getmovies(params):
    filters = params.get('filter')
    # sort = params.get('sort')
    limits = params.get('limits')

    if not filters:
        return False

    filters, _ = _filter_walker(
        filters,
        ['set', 'year', 'playcount', 'inprogress', 'genre']
    )
    _set = filters.get('set')
    year = filters.get('year')
    watched = filters.get('playcount', {'operator': 'greaterthan', 'value': -1})
    inprogress = filters.get('inprogress')
    genres = filters.get('genre', {})

    movies = []
    if not _set:
        if inprogress:
            movies = [
                movie for movie in LIBRARY['movies']
                if movie.get('resume', {}).get('position', 0) > 0
                and movie.get('playcount', 0) < 1
            ]
        elif watched:
            movies = [
                movie for movie in LIBRARY['movies']
                if (watched.get('operator') == 'greaterthan' and movie.get('playcount', 0) > int(watched.get('value'))
                    or watched.get('operator') == 'lessthan' and movie.get('playcount', 0) < int(watched.get('value')))
                and (not genres.get('value') or not set(genres.get('value')).isdisjoint(movie.get('genre', [])))
            ]
        else:
            return False
    elif year:
        movies = [
            movie for movie in LIBRARY['movies']
            if movie.get('set', '') == _set.get('value')
            and movie.get('year', 0) >= int(year.get('value'))
        ]
        if movies and year.get('operator') == 'after':
            movies = movies[1:]
    else:
        movies = [
            movie for movie in LIBRARY['movies']
            if movie.get('set', '') == _set.get('value')
        ]

    if limits and movies:
        start = limits['start']
        end = limits['end']
        if end == -1:
            end = len(movies)
        movies = movies[start:end]

    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'result': {'movies': movies}
    })


def _videolibrary_getmoviedetails(params):
    movieid = params.get('movieid')
    if movieid is None:
        return False

    movies = [
        movie for movie in LIBRARY['movies']
        if movie['movieid'] == movieid
    ]

    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'result': {'moviedetails': movies[0] if movies else {}}
    })


def _videolibrary_getepisodedetails(params):
    episodeid = params.get('episodeid')
    if episodeid is None:
        return False

    episodes = [
        episode for episode in LIBRARY['episodes']
        if episode['episodeid'] == episodeid
    ]

    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'result': {'episodedetails': episodes[0] if episodes else {}}
    })


def _videolibrary_gettvshowdetails(params):
    tvshowid = params.get('tvshowid')
    if tvshowid is None:
        return False

    tvshows = [
        details for _, details in LIBRARY['tvshows'].items()
        if details['tvshowid'] == tvshowid
    ]

    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'result': {'tvshowdetails': tvshows[0] if tvshows else {}}
    })


def _jsonrpc_notifyall(params):
    for ref in Monitor._instances.valuerefs():  # pylint: disable=protected-access
        notification_handler = getattr(ref(), 'onNotification', None)
        if callable(notification_handler):
            message = params.get('message')
            if not message:
                return False

            announcers = [
                name for name, details in _JSONRPC_announcer_map.items()
                if message in details.get('messages')
            ]
            announcer = announcers[0] if announcers else 'Other'

            thread = threading.Thread(target=notification_handler, args=(
                params.get('sender'),
                '{0}.{1}'.format(announcer, message),
                json.dumps(params.get('data'))
            ))
            thread.daemon = True
            thread.start()

    return True


def _player_open(params):
    item = params['item']
    item_file = None
    if 'playlistid' in item:
        _PLAYLIST[item['playlistid']]['position'] = item['position']
        item = _PLAYLIST[item['playlistid']]['playlist'][item['position']]

    if 'file' in item:
        itemid = -1
        item_file = item['file']
    elif 'episodeid' in item:
        itemid = item['episodeid']
        item_file = json.loads(_videolibrary_getepisodedetails({
            'episodeid': itemid
        }))['result']['episodedetails'].get('file')

    if item_file:
        player = Player()
        player.play(item_file)
        _jsonrpc_notifyall({
            'sender': 'xbmc',
            'message': 'OnPlay',
            'data': {
                'item': {
                    'id': itemid,
                    'title': '',
                    'type': 'episode',
                },
                'player': {
                    'playerid': _PLAYLIST_TYPE,
                    'speed': 1
                }
            }
        })
        _jsonrpc_notifyall({
            'sender': 'xbmc',
            'message': 'OnStop',
            'data': {
                'end': True,
                'item': {
                    'id': itemid,
                    'title': '',
                    'type': 'episode',
                }
            }
        })
        _jsonrpc_notifyall({
            'sender': 'xbmc',
            'message': 'OnAVStart',
            'data': {
                'item': {
                    'id': itemid,
                    'title': '',
                    'type': 'episode',
                },
                'player': {
                    'playerid': _PLAYLIST_TYPE,
                    'speed': 1
                }
            }
        })
    return True


def _playlist_add(params):
    _PLAYLIST[params['playlistid']]['playlist'] += [params['item']]
    return True


def _playlist_remove(params):
    playlistid = params['playlistid']
    position = params['position']
    playlist = _PLAYLIST[playlistid]['playlist']
    _PLAYLIST[playlistid]['playlist'] = (
        playlist[:position] + playlist[position + 1:]
    )
    return True


_JSONRPC_methods = {
    'Application.GetProperties': _application_getproperties,
    'Settings.GetSettingValue': _settings_getsettingvalue,
    'Player.GetActivePlayers': _player_getactiveplayers,
    'Player.GetProperties': _player_getproperties,
    'Player.GetItem': _player_getitem,
    'VideoLibrary.GetMovies': _videolibrary_getmovies,
    'VideoLibrary.GetTVShows': _videolibrary_gettvshows,
    'VideoLibrary.GetEpisodes': _videolibrary_getepisodes,
    'VideoLibrary.GetMovieDetails': _videolibrary_getmoviedetails,
    'VideoLibrary.GetEpisodeDetails': _videolibrary_getepisodedetails,
    'VideoLibrary.GetTVShowDetails': _videolibrary_gettvshowdetails,
    'JSONRPC.NotifyAll': _jsonrpc_notifyall,
    'Player.Open': _player_open,
    'Playlist.Add': _playlist_add,
    'Playlist.Remove': _playlist_remove
}

_JSONRPC_announcer_map = {
    'Player': {'flag': 0x001, 'messages': ['OnAVChange', 'OnAVStart', 'OnPause', 'OnPlay', 'OnResume', 'OnSeek', 'OnSpeedChanged', 'OnStop']},
    'Playlist': {'flag': 0x002, 'messages': []},
    'GUI': {'flag': 0x004, 'messages': []},
    'System': {'flag': 0x008, 'messages': []},
    'VideoLibrary': {'flag': 0x010, 'messages': []},
    'AudioLibrary': {'flag': 0x020, 'messages': []},
    'Application': {'flag': 0x040, 'messages': []},
    'Input': {'flag': 0x080, 'messages': []},
    'PVR': {'flag': 0x100, 'messages': []},
    'Other': {'flag': 0x200, 'messages': ['upnext_credits_detected', 'upnext_data', 'upnext_trigger']},
    'Info': {'flag': 0x400, 'messages': []}
}


def executeJSONRPC(jsonrpccommand):
    ''' A reimplementation of the xbmc executeJSONRPC() function '''
    command = json.loads(jsonrpccommand)
    method = _JSONRPC_methods.get(command.get('method')) if command else None
    params = command.get('params', {}) if command else {}

    return_val = method(params) if callable(method) else False
    if return_val is True:
        return json.dumps({
            'id': 1,
            'jsonrpc': '2.0',
            'result': 'OK'
        })
    if return_val:
        return return_val

    log('executeJSONRPC does not implement method "{method}"'.format(**command), LOGERROR)
    return json.dumps({
        'id': 1,
        'jsonrpc': '2.0',
        'error': {'code': -1, 'message': 'Not implemented'}
    })


def getCondVisibility(string):
    ''' A reimplementation of the xbmc getCondVisibility() function '''
    if string == 'system.platform.android':
        return False
    return True


def getInfoLabel(key):
    ''' A reimplementation of the xbmc getInfoLabel() function '''
    return _INFO_LABELS.get(key, '')


def getLocalizedString(msgctxt):
    ''' A reimplementation of the xbmc getLocalizedString() function '''
    for entry in _PO:
        if entry.msgctxt == '#%s' % msgctxt:
            return entry.msgstr or entry.msgid
    if int(msgctxt) >= 30000:
        log('Unable to translate #{msgctxt}'.format(msgctxt=msgctxt), LOGERROR)
    return '<Untranslated>'


def getRegion(key):
    ''' A reimplementation of the xbmc getRegion() function '''
    return _REGIONS.get(key)


def log(msg, level=LOGDEBUG):
    ''' A reimplementation of the xbmc log() function '''

    now = datetime.now()
    thread_id = threading.current_thread().ident
    level_name = _LOG_LEVELS[level]
    component = 'general'
    level_colour = '\033[32;1m'  # green FG, bold
    msg_colour = '\033[37m'  # white FG
    reset_colour = '\033[39;0m'

    if LOGERROR <= level <= LOGFATAL:
        level_colour = '\033[31;1m'  # red FG, bold
    elif level == LOGWARNING:
        level_colour = '\033[33;1m'  # yellow FG, bold
    elif level == LOGDEBUG:
        level_colour = '\033[90;1m'  # grey FG, bold
        msg_colour = '\033[90m'  # grey FG

    print('{time} T:{thread_id}\t{level_colour}{level_name:>8} <{component}>: {msg_colour}{msg}{reset_colour}'.format(
        time=now,
        thread_id=thread_id,
        level_colour=level_colour,
        level_name=level_name,
        component=component,
        reset_colour=reset_colour,
        msg_colour=msg_colour,
        msg=from_bytes(msg)
    ))
    if level == LOGFATAL:
        raise Exception(msg)  # pylint: disable=broad-exception-raised


def setContent(self, content):  # pylint: disable=unused-argument
    ''' A stub implementation of the xbmc setContent() function '''
    return


def sleep(seconds):
    ''' A reimplementation of the xbmc sleep() function '''
    time_sleep(seconds)


# translatePath and makeLegalFilename have been moved to xbmcvfs in Kodi 19+
# but currently still available in xbmc
if not __KODI_NEXUS__:
    def translatePath(path):
        ''' A stub implementation of the xbmc translatePath() function '''
        if path.startswith('special://home'):
            return path.replace('special://home', os.path.join(os.getcwd(), 'tests/'))
        if path.startswith('special://masterprofile'):
            return path.replace('special://masterprofile', os.path.join(os.getcwd(), 'tests/userdata/'))
        if path.startswith('special://profile'):
            return path.replace('special://profile', os.path.join(os.getcwd(), 'tests/userdata/'))
        if path.startswith('special://userdata'):
            return path.replace('special://userdata', os.path.join(os.getcwd(), 'tests/userdata/'))
        return path

    def makeLegalFilename(path):
        ''' A stub implementation of the xbmc makeLegalFilename() function '''
        return os.path.normpath(path)
