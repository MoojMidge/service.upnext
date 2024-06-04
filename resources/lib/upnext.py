# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""Implements helper functions for video plugins to interact with UpNext"""

from __future__ import absolute_import, division, unicode_literals

import constants
import utils
import xbmc
import xbmcgui
from settings import SETTINGS


def log(msg, level=utils.LOGWARNING):
    utils.log(msg, name=__name__, level=level)


def _copy_video_details(upnext_data):
    # If current/next episode information is not provided, copy it
    dummy_info = None
    dummy_key = None
    if not upnext_data.get('next_video'):
        dummy_info = upnext_data['current_video'].copy()
        dummy_key = 'next_video'
    elif not upnext_data.get('current_video'):
        dummy_info = upnext_data['next_video'].copy()
        dummy_key = 'current_video'

    if not dummy_key:
        return upnext_data

    if dummy_key == 'next_video':
        # Next provided video may not be the next consecutive video so we set
        # the title to indicate the next video in the UpNext popup
        dummy_info['title'] = utils.localize(constants.NEXT_STR_ID)
    else:
        dummy_info['title'] = ''

    dummy_info['art'] = {}
    dummy_info['plot'] = ''
    dummy_info['playcount'] = 0
    dummy_info['rating'] = 0
    dummy_info['firstaired'] = ''
    dummy_info['runtime'] = 0

    if 'tvshowid' in dummy_info:
        dummy_info['episodeid'] = constants.UNDEFINED
        # Change season and episode info to empty string to avoid episode
        # formatting issues ("S-1E-1") in UpNext popup
        dummy_info['season'] = ''
        dummy_info['episode'] = ''
    elif 'setid' in dummy_info:
        dummy_info['movieid'] = constants.UNDEFINED
    else:
        dummy_info['id'] = constants.UNDEFINED

    upnext_data[dummy_key] = dummy_info
    return upnext_data


# pylint: disable=no-member
if utils.supports_python_api(20):
    def _wrap(value):
        if isinstance(value, (list, tuple)):
            return value
        return (value,)


    def _convert_cast(cast_list):
        cast_role_list = []
        for order, person in enumerate(cast_list):
            if isinstance(person, xbmc.Actor):
                return cast_list
            if isinstance(person, tuple):
                name = person[0]
                role = person[1]
            elif isinstance(person, dict):
                name = person.get('name', '')
                role = person.get('role', '')
                order = person.get('order', order)
            else:
                name = person
                role = ''
            cast_role_list.append(
                xbmc.Actor(name=name, role=role, order=order)
            )
        return cast_role_list


    def _set_info(infolabel):
        info_tag = _set_info.info_tag
        if not info_tag or not infolabel:
            return

        name = infolabel[0].lower()
        value = infolabel[1]
        mapping = _set_info.mapping.get(name)

        if not mapping:
            return

        setter, pre_process, force = mapping
        # Some exceptions get logged even if caught. Force pre_process to avoid
        # log spam
        try:
            setter(info_tag, pre_process(value) if force else value)
        except TypeError as error:
            if force:
                log(error)
            else:
                setter(info_tag, pre_process(value))


    _InfoTagVideo = xbmc.InfoTagVideo
    _set_info.mapping = {
        'aired': (_InfoTagVideo.setFirstAired, str, False),
        'album': (_InfoTagVideo.setAlbum, str, False),
        'artist': (_InfoTagVideo.setArtists, _wrap, True),
        'cast': (_InfoTagVideo.setCast, _convert_cast, True),
        'castandrole': (_InfoTagVideo.setCast, _convert_cast, True),
        'code': (_InfoTagVideo.setProductionCode, str, False),
        'country': (_InfoTagVideo.setCountries, _wrap, True),
        'dateadded': (_InfoTagVideo.setDateAdded, str, False),
        'dbid': (_InfoTagVideo.setDbId, int, False),
        'director': (_InfoTagVideo.setDirectors, _wrap, True),
        'duration': (_InfoTagVideo.setDuration, int, False),
        'episode': (_InfoTagVideo.setEpisode, int, False),
        'episodeguide': (_InfoTagVideo.setEpisodeGuide, str, False),
        'genre': (_InfoTagVideo.setGenres, _wrap, True),
        'imdbnumber': (_InfoTagVideo.setIMDBNumber, str, False),
        'lastplayed': (_InfoTagVideo.setLastPlayed, str, False),
        'mediatype': (_InfoTagVideo.setMediaType, str, False),
        'mpaa': (_InfoTagVideo.setMpaa, str, False),
        'originaltitle': (_InfoTagVideo.setOriginalTitle, str, False),
        'path': (_InfoTagVideo.setPath, str, False),
        # 'path': (_InfoTagVideo.setFilenameAndPath, str, False),
        'playcount': (_InfoTagVideo.setPlaycount, int, False),
        'plot': (_InfoTagVideo.setPlot, str, False),
        'plotoutline': (_InfoTagVideo.setPlotOutline, str, False),
        'premiered': (_InfoTagVideo.setPremiered, str, False),
        'rating': (_InfoTagVideo.setRating, float, False),
        # 'rating': (_InfoTagVideo.setRatings, int, False),
        'season': (_InfoTagVideo.setSeason, int, False),
        'set': (_InfoTagVideo.setSet, str, False),
        'setid': (_InfoTagVideo.setSetId, int, False),
        'setoverview': (_InfoTagVideo.setSetOverview, str, False),
        'showlink': (_InfoTagVideo.setShowLinks, _wrap, True),
        'sortepisode': (_InfoTagVideo.setSortEpisode, int, False),
        'sortseason': (_InfoTagVideo.setSortSeason, int, False),
        'sorttitle': (_InfoTagVideo.setSortTitle, str, False),
        'status': (_InfoTagVideo.setTvShowStatus, str, False),
        'studio': (_InfoTagVideo.setStudios, _wrap, True),
        'tag': (_InfoTagVideo.setTags, _wrap, True),
        'tagline': (_InfoTagVideo.setTagLine, str, False),
        'title': (_InfoTagVideo.setTitle, str, False),
        'top250': (_InfoTagVideo.setTop250, int, False),
        'tracknumber': (_InfoTagVideo.setTrackNumber, int, False),
        'trailer': (_InfoTagVideo.setTrailer, str, False),
        'tvshowtitle': (_InfoTagVideo.setTvShowTitle, str, False),
        'userrating': (_InfoTagVideo.setUserRating, int, False),
        'votes': (_InfoTagVideo.setVotes, int, False),
        'writer': (_InfoTagVideo.setWriters, _wrap, True),
        'year': (_InfoTagVideo.setYear, int, False),
    }


def _create_video_listitem(video,
                           kwargs=None, infolabels=None, properties=None):
    """Create a xbmcgui.ListItem from provided video details"""

    _infolabels = {
        'path': video.get('file', ''),
        'title': video.get('title', ''),
        'plot': video.get('plot', ''),
        'genre': video.get('genre', ''),
        'rating': float(video.get('rating', 0.0)),
        'premiered': video.get('premiered', ''),
        'year': video.get('year', 0),
        'mpaa': video.get('mpaa', ''),
        'dateadded': video.get('dateadded', ''),
        'lastplayed': video.get('lastplayed', ''),
        'playcount': video.get('playcount', 0),
    }
    if infolabels:
        _infolabels.update(infolabels)

    resume = video.get('resume', {})
    _properties = {
        'isPlayable': 'true'
    }
    if not utils.supports_python_api(20):
        _properties.update({
            'resumetime': str(resume.get('position', 0)),
            'totaltime': str(resume.get('total', 0)),
        })
    if properties:
        _properties.update(properties)

    _kwargs = {
        'label': _infolabels.get('title'),
        'path': _infolabels.get('path'),
    }
    if utils.supports_python_api(18):
        _kwargs['offscreen'] = True
    if kwargs:
        _kwargs.update(kwargs)

    listitem = xbmcgui.ListItem(**_kwargs)
    if utils.supports_python_api(20):
        info_tag = listitem.getVideoInfoTag()
        _set_info.info_tag = info_tag
        info_tag.setResumePoint(
            time=resume.get('position', 0), totaltime=resume.get('total', 0)
        )
        utils.modify_iterable(_set_info, _infolabels.items())
    else:
        listitem.setInfo(type='Video', infoLabels=_infolabels)

    if utils.supports_python_api(18):
        listitem.setProperties(_properties)
        listitem.setIsFolder(_properties.get('isFolder', False))
    else:
        for key, val in _properties.items():
            listitem.setProperty(key, val)

    listitem.setArt(video.get('art', {}))

    return listitem


def create_episode_listitem(episode,  # pylint: disable=too-many-locals
                            kwargs=None, infolabels=None, properties=None):
    """Create a xbmcgui.ListItem from provided episode details"""

    episode_num = episode.get('episode')
    episode_title = episode.get('title', '')
    first_aired = episode.get('firstaired', '')
    first_aired, first_aired_short = utils.localize_date(first_aired)
    season = episode.get('season')
    show_title = episode.get('showtitle', '')

    # Calculate tvshow progress if available
    num_episodes = episode.get('totalepisodes', 0)
    num_watched = episode.get('watchedepisodes', 0)
    num_unwatched = max(0, num_episodes - num_watched)
    progress = round(100 * num_watched / num_episodes) if num_episodes else 0

    if first_aired:
        year = first_aired.year
        first_aired_string = str(first_aired)
    else:
        year = first_aired_short
        first_aired_string = first_aired_short

    season_episode = (
        '' if episode_num is None
        else str(episode_num) if season is None
        else constants.SEASON_EPISODE.format(season, episode_num)
    )
    label_tokens = (
        None,
        show_title,
        season_episode,
        episode_title,
        first_aired_short
    )

    _kwargs = {
        'label': ' - '.join(
            label_tokens[token]
            for token in SETTINGS.plugin_main_label
            if token and label_tokens[token]
        ),
        'label2': ' - '.join(
            label_tokens[token]
            for token in SETTINGS.plugin_secondary_label
            if token and label_tokens[token]
        ),
    }
    if kwargs:
        _kwargs.update(kwargs)

    _infolabels = {
        'dbid': episode.get('episodeid', constants.UNDEFINED),
        'tvshowtitle': show_title,
        'season': constants.UNDEFINED if season is None else season,
        'episode': constants.UNDEFINED if episode_num is None else episode_num,
        'aired': first_aired_string,
        'premiered': first_aired_string,
        'year': year,
        'mediatype': 'episode'
    }
    if infolabels:
        _infolabels.update(infolabels)

    _properties = {
        # No method to set/get tvshowid from a ListItem or InfoTagVideo
        'tvshowid': str(episode.get('tvshowid', constants.UNDEFINED)),
        # Set tvshow progress if available
        'totalepisodes': str(num_episodes),
        'unwatchedepisodes': str(num_unwatched),
        'watchedepisodes': str(num_watched),
        'watchedprogress': str(progress),
    }
    if properties:
        _properties.update(properties)

    listitem = _create_video_listitem(
        episode, _kwargs, _infolabels, _properties
    )
    return listitem


def create_movie_listitem(movie,
                          kwargs=None, infolabels=None, properties=None):
    """Create a xbmcgui.ListItem from provided movie details"""

    set_id = movie.get('setid', constants.UNDEFINED)
    set_name = movie.get('set', '')
    title = movie.get('title', '')
    year = movie.get('year')

    _kwargs = {
        'label': '{0} ({1})'.format(title, year) if year else title
    }
    if kwargs:
        _kwargs.update(kwargs)

    _infolabels = {
        'dbid': movie.get('movieid', constants.UNDEFINED),
        'setid': set_id,
        'set': set_name,
        'mediatype': 'movie'
    }
    if infolabels:
        _infolabels.update(infolabels)

    # Pass as property - there is no method to get setid/set from a ListItem
    # or InfoTagVideo even though there are new methods to set these info tags
    _properties = {
        'setid': str(set_id),
        'set': set_name
    }
    if properties:
        _properties.update(properties)

    listitem = _create_video_listitem(
        movie, _kwargs, _infolabels, _properties
    )
    return listitem


def create_tvshow_listitem(tvshow,
                           kwargs=None, infolabels=None, properties=None):
    """Create a xbmcgui.ListItem from provided tvshow details"""

    num_episodes = tvshow.get('totalepisodes') or tvshow.get('episode', 0)
    title = tvshow.get('title', '')
    num_watched = tvshow.get('watchedepisodes', 0)
    num_unwatched = max(0, num_episodes - num_watched)
    progress = round(100 * num_watched / num_episodes) if num_episodes else 0
    year = tvshow.get('year')

    _kwargs = {
        'label': '{0} ({1})'.format(title, year) if year else title
    }
    if kwargs:
        _kwargs.update(kwargs)

    _infolabels = {
        'dbid': tvshow.get('tvshowid', constants.UNDEFINED),
        'mediatype': 'tvshow'
    }
    if infolabels:
        _infolabels.update(infolabels)

    _properties = {
        'totalepisodes': str(num_episodes),
        'unwatchedepisodes': str(num_unwatched),
        'watchedepisodes': str(num_watched),
        'watchedprogress': str(progress),
    }
    if properties:
        _properties.update(properties)

    listitem = _create_video_listitem(
        tvshow, _kwargs, _infolabels, _properties
    )
    return listitem


def create_listitem(item, kwargs=None, infolabels=None, properties=None):
    """Create a xbmcgui.ListItem from provided item_details dict"""

    media_type = item.get('type')
    if 'details' in item:
        item = item['details']

    if media_type == 'episode' or 'tvshowid' in item:
        return create_episode_listitem(item, kwargs, infolabels, properties)

    if media_type == 'tvshow' or 'watchedepisodes' in item:
        return create_tvshow_listitem(item, kwargs, infolabels, properties)

    if media_type == 'movie' or 'setid' in item:
        return create_movie_listitem(item, kwargs, infolabels, properties)

    return None


def send_signal(sender, upnext_info):
    """Helper function for video plugins to send data to UpNext"""

    # Exit if not enough information provided by video plugin
    required_episode_info = {
        'current_episode': 'current_video',
        'next_episode': 'next_video',
        'current_video': 'current_video',
        'next_video': 'next_video'
    }
    required_plugin_info = ['play_url', 'play_info']
    if not (any(info in upnext_info for info in required_episode_info)
            and any(info in upnext_info for info in required_plugin_info)):
        log('Invalid UpNext info - {0}'.format(upnext_info), utils.LOGWARNING)
        return None

    # Extract ListItem or InfoTagVideo details for use by UpNext
    upnext_data = {}
    for key, val in upnext_info.items():
        if key in required_plugin_info:
            upnext_data[key] = val
            continue

        key = required_episode_info.get(key)
        if not key:
            continue

        thumb = ''
        fanart = ''
        tvshow_id = constants.UNDEFINED
        set_id = constants.UNDEFINED
        set_name = ''

        if isinstance(val, xbmcgui.ListItem):
            thumb = val.getArt('thumb')
            fanart = val.getArt('fanart')
            tvshow_id = (
                    val.getProperty('tvshowid')
                    or val.getProperty('TvShowDBID')
                    or tvshow_id
            )
            set_id = int(val.getProperty('setid') or set_id)
            set_name = val.getProperty('set')
            val = val.getVideoInfoTag()

        if not isinstance(val, xbmc.InfoTagVideo):
            upnext_data[key] = val
            continue

        media_type = val.getMediaType()

        video_info = {
            'title': val.getTitle(),
            # Prefer outline over full plot for UpNext popup
            'plot': val.getPlotOutline() or val.getPlot(),
            'playcount': val.getPlayCount(),
            # Prefer user rating over scraped rating
            'rating': val.getUserRating() or val.getRating(),
            # Fallback for available date information
            'firstaired': ((val.getFirstAiredAsW3C() or val.getPremieredAsW3C())
                           if utils.supports_python_api(20) else
                           (val.getFirstAired() or val.getPremiered())
                           or str(val.getYear())),
            # Runtime used to evaluate endtime in UpNext popup, if available
            'runtime': utils.supports_python_api(18) and val.getDuration() or 0
        }

        if media_type == 'episode':
            video_info.update({
                'episodeid': val.getDbId(),
                'tvshowid': tvshow_id,
                'season': val.getSeason(),
                'episode': val.getEpisode(),
                'showtitle': val.getTVShowTitle(),
                'art': {
                    'thumb': thumb,
                    'tvshow.fanart': fanart,
                },
            })
        elif media_type == 'movie':
            video_info.update({
                'movieid': val.getDbId(),
                'setid': set_id,
                'set': set_name,
                'art': {
                    'thumb': thumb,
                    'fanart': fanart,
                },
            })
        else:
            video_info.update({
                'id': val.getDbId(),
            })

        upnext_data[key] = video_info

    if 'player' in upnext_info:
        from tmdb_helper import generate_tmdbhelper_play_url

        upnext_data['play_url'] = generate_tmdbhelper_play_url(
            upnext_data, upnext_info['player']
        )
        upnext_data['play_direct'] = True
    upnext_data = _copy_video_details(upnext_data)

    return utils.event(sender=sender,
                       message='upnext_data',
                       data=upnext_data,
                       encoding='base64')
