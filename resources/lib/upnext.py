# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""Implements helper functions for video plugins to interact with UpNext"""

from __future__ import absolute_import, division, unicode_literals
from collections import deque
import xbmc
import xbmcgui
from settings import SETTINGS
import constants
import utils


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
        dummy_info['title'] = utils.localize(constants.NEXT_STRING_ID)
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
    def _set_info(infolabel):
        info_tag = _set_info.info_tag
        if not info_tag or not infolabel:
            return None

        name = infolabel[0].lower()
        value = infolabel[1]
        setter = _set_info.mapping.get(name)
        if callable(setter):
            setter(info_tag, value)
            return (name, value)
        return None

    _InfoTagVideo = xbmc.InfoTagVideo
    _set_info.mapping = {
        'sortepisode': _InfoTagVideo.setSortEpisode,
        'dbid': _InfoTagVideo.setDbId,
        'year': _InfoTagVideo.setYear,
        'episode': _InfoTagVideo.setEpisode,
        'season': _InfoTagVideo.setSeason,
        'sortseason': _InfoTagVideo.setSortSeason,
        'episodeguide': _InfoTagVideo.setEpisodeGuide,
        'top250': _InfoTagVideo.setTop250,
        'setid': _InfoTagVideo.setSetId,
        'tracknumber': _InfoTagVideo.setTrackNumber,
        'rating': _InfoTagVideo.setRating,
        # 'rating': _InfoTagVideo.setRatings,
        'userrating': _InfoTagVideo.setUserRating,
        'playcount': _InfoTagVideo.setPlaycount,
        'mpaa': _InfoTagVideo.setMpaa,
        'plot': _InfoTagVideo.setPlot,
        'plotoutline': _InfoTagVideo.setPlotOutline,
        'title': _InfoTagVideo.setTitle,
        'originaltitle': _InfoTagVideo.setOriginalTitle,
        'sorttitle': _InfoTagVideo.setSortTitle,
        'tagline': _InfoTagVideo.setTagLine,
        'tvshowtitle': _InfoTagVideo.setTvShowTitle,
        'status': _InfoTagVideo.setTvShowStatus,
        'genre': _InfoTagVideo.setGenres,
        'country': _InfoTagVideo.setCountries,
        'director': _InfoTagVideo.setDirectors,
        'studio': _InfoTagVideo.setStudios,
        'writer': _InfoTagVideo.setWriters,
        'duration': _InfoTagVideo.setDuration,
        'premiered': _InfoTagVideo.setPremiered,
        'set': _InfoTagVideo.setSet,
        'setoverview': _InfoTagVideo.setSetOverview,
        'tag': _InfoTagVideo.setTags,
        'code': _InfoTagVideo.setProductionCode,
        'aired': _InfoTagVideo.setFirstAired,
        'lastplayed': _InfoTagVideo.setLastPlayed,
        'album': _InfoTagVideo.setAlbum,
        'votes': _InfoTagVideo.setVotes,
        'trailer': _InfoTagVideo.setTrailer,
        'path': _InfoTagVideo.setPath,
        # 'path': _InfoTagVideo.setFilenameAndPath,
        'imdbnumber': _InfoTagVideo.setIMDBNumber,
        'dateadded': _InfoTagVideo.setDateAdded,
        'mediatype': _InfoTagVideo.setMediaType,
        'showlink': _InfoTagVideo.setShowLinks,
        'artist': _InfoTagVideo.setArtists,
        'cast': _InfoTagVideo.setCast,
        'castandrole': _InfoTagVideo.setCast,
    }


def _create_video_listitem(video,
                           kwargs=None, infolabels=None, properties=None):
    """Create a xbmcgui.ListItem from provided video details"""

    title = video.get('title', '')
    file_path = video.get('file', '')
    resume = video.get('resume', {})
    art = video.get('art', {})

    default_kwargs = {
        'label': title,
        'path': file_path
    }
    if utils.supports_python_api(18):
        default_kwargs['offscreen'] = True
    if kwargs:
        default_kwargs.update(kwargs)

    default_infolabels = {
        'path': file_path,
        'title': title,
        'plot': video.get('plot', ''),
        'rating': float(video.get('rating', 0.0)),
        'premiered': video.get('premiered', ''),
        'year': video.get('year', ''),
        'mpaa': video.get('mpaa', ''),
        'dateadded': video.get('dateadded', ''),
        'lastplayed': video.get('lastplayed', ''),
        'playcount': video.get('playcount', 0),
    }
    if infolabels:
        default_infolabels.update(infolabels)

    default_properties = {
        'isPlayable': 'true'
    }
    if not utils.supports_python_api(20):
        default_properties.update({
            'resumetime': str(resume.get('position')),
            'totaltime': str(resume.get('total')),
        })
    if properties:
        default_properties.update(properties)

    listitem = xbmcgui.ListItem(**default_kwargs)
    if utils.supports_python_api(20):
        info_tag = listitem.getVideoInfoTag()
        _set_info.info_tag = info_tag
        info_tag.setResumePoint(
            time=resume.get('position'), totalTime=resume.get('total')
        )
        # Consume iterator
        deque(map(_set_info, default_infolabels.items(), maxlen=0))
    else:
        listitem.setInfo(type='Video', infoLabels=default_infolabels)

    if utils.supports_python_api(18):
        listitem.setProperties(default_properties)
        listitem.setIsFolder(False)
    else:
        for key, val in default_properties.items():
            listitem.setProperty(key, val)
    listitem.setArt(art)
    listitem.setPath(file_path)

    return listitem


def create_episode_listitem(episode):
    """Create a xbmcgui.ListItem from provided episode details"""

    show_title = episode.get('showtitle', '')
    episode_title = episode.get('title', '')
    season = episode.get('season')
    episode_num = episode.get('episode', '')
    first_aired = episode.get('firstaired', '')

    season_episode = (
        episode_num if season is None or episode_num == ''
        else constants.SEASON_EPISODE.format(season, episode_num)
    )
    label_tokens = (None, show_title, season_episode, episode_title)

    kwargs = {
        'label': ' - '.join(
            label_tokens[token]
            for token in SETTINGS.plugin_main_label
            if token
        ),
        'label2': ' - '.join(
            label_tokens[token]
            for token in SETTINGS.plugin_secondary_label
            if token
        ),
    }

    infolabels = {
        'dbid': episode.get('episodeid', constants.UNDEFINED),
        'tvshowtitle': show_title,
        'season': constants.UNDEFINED if season is None else season,
        'episode': constants.UNDEFINED if episode_num == '' else episode_num,
        'aired': first_aired,
        'premiered': first_aired,
        'year': utils.get_year(first_aired),
        'mediatype': 'episode'
    }

    properties = {
        'tvshowid': str(episode.get('tvshowid', constants.UNDEFINED))
    }

    listitem = _create_video_listitem(episode, kwargs, infolabels, properties)
    return listitem


def create_movie_listitem(movie):
    """Create a xbmcgui.ListItem from provided movie details"""

    infolabels = {
        'dbid': movie.get('movieid', constants.UNDEFINED),
        'mediatype': 'movie'
    }

    listitem = _create_video_listitem(movie, None, infolabels)
    return listitem


def create_listitem(item):
    """Create a xbmcgui.ListItem from provided item_details dict"""

    media_type = item.get('media_type')
    if 'details' in item:
        item = item['details']

    if media_type == 'episode' or 'tvshowid' in item:
        return create_episode_listitem(item)

    if media_type == 'movie' or 'setid' in item:
        return create_movie_listitem(item)

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
        return

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
            set_id = val.getProperty('setid') or set_id
            set_name = val.getProperty('set')
            val = val.getVideoInfoTag()

        if not isinstance(val, xbmc.InfoTagVideo):
            continue

        media_type = val.getMediaType()

        # Fallback for available date information
        first_aired = (
            val.getFirstAiredAsW3C() or val.getPremieredAsW3C()
        ) if utils.supports_python_api(20) else (
            val.getFirstAired() or val.getPremiered()
        ) or str(val.getYear())

        video_info = {
            'title': val.getTitle(),
            'art': {
                'thumb': thumb,
                'tvshow.fanart': fanart,
            },
            # Prefer outline over full plot for UpNext popup
            'plot': val.getPlotOutline() or val.getPlot(),
            'playcount': val.getPlayCount(),
            # Prefer user rating over scraped rating
            'rating': val.getUserRating() or val.getRating(),
            'firstaired': first_aired,
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
            })
        elif media_type == 'movie':
            video_info.update({
                'movieid': val.getDbId(),
                'setid': set_id,
                'set': set_name,
            })
        else:
            video_info.update({
                'id': val.getDbId(),
            })

        upnext_data[key] = video_info

    upnext_data = _copy_video_details(upnext_data)

    utils.event(
        sender=sender,
        message='upnext_data',
        data=upnext_data,
        encoding='base64'
    )
