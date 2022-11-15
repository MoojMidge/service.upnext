# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""Implements helper functions for video plugins to interact with UpNext"""

from __future__ import absolute_import, division, unicode_literals
import xbmc
import xbmcgui
from settings import SETTINGS
import constants
import utils


def log(msg, level=utils.LOGWARNING):
    utils.log(msg, name=__name__, level=level)


def _copy_episode_details(upnext_data):
    # If next episode information is not provided, fake it
    if not upnext_data.get('next_episode'):
        episode = upnext_data['current_episode']
        episode['episodeid'] = constants.UNDEFINED
        episode['art'] = {}
        # Next provided episode may not be the next consecutive episode so we
        # can't assume that the episode can simply be incremented, instead set
        # title to indicate the next episode in the UpNext popup
        # episode['episode'] = utils.get_int(episode, 'episode') + 1
        episode['title'] = utils.localize(constants.NEXT_STRING_ID)
        # Change season and episode info to empty string to avoid episode
        # formatting issues ("S-1E-1") in UpNext popup
        episode['season'] = ''
        episode['episode'] = ''
        episode['plot'] = ''
        episode['playcount'] = 0
        episode['rating'] = 0
        episode['firstaired'] = ''
        episode['runtime'] = 0
        upnext_data['next_episode'] = episode

    # If current episode information is not provided, fake it
    elif not upnext_data.get('current_episode'):
        episode = upnext_data['next_episode']
        episode['episodeid'] = constants.UNDEFINED
        episode['art'] = {}
        episode['title'] = ''
        episode['season'] = ''
        episode['episode'] = ''
        episode['plot'] = ''
        episode['playcount'] = 0
        episode['rating'] = 0
        episode['firstaired'] = ''
        episode['runtime'] = 0
        upnext_data['current_episode'] = episode

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


def _create_listitem(item, kwargs=None, infolabels=None, properties=None):
    """Create a xbmcgui.ListItem from provided item details"""

    title = item.get('title', '')
    file_path = item.get('file', '')
    resume = item.get('resume', {})
    art = item.get('art', {})

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
        'plot': item.get('plot', ''),
        'rating': float(item.get('rating', 0.0)),
        'premiered': item.get('premiered', ''),
        'year': item.get('year', ''),
        'mpaa': item.get('mpaa', ''),
        'dateadded': item.get('dateadded', ''),
        'lastplayed': item.get('lastplayed', ''),
        'playcount': item.get('playcount', 0),
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
        infolabels = dict(map(_set_info, default_infolabels.items()))
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


def create_episode_listitem(item):
    """Create a xbmcgui.ListItem from provided episode details"""

    show_title = item.get('showtitle', '')
    episode_title = item.get('title', '')
    season = item.get('season', '')
    episode_number = item.get('episode', '')
    first_aired = item.get('firstaired', '')

    season_episode = (
        '{0}x{1}'.format(season, episode_number) if season and episode_number
        else episode_number
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
        'dbid': item.get('episodeid', constants.UNDEFINED),
        'tvshowtitle': show_title,
        'season': season or constants.UNDEFINED,
        'episode': episode_number or constants.UNDEFINED,
        'aired': first_aired,
        'premiered': first_aired,
        'year': utils.get_year(first_aired),
        'mediatype': 'episode'
    }

    properties = {
        'tvshowid': str(item.get('tvshowid', constants.UNDEFINED))
    }

    listitem = _create_listitem(item, kwargs, infolabels, properties)
    return listitem


def create_movie_listitem(item):
    """Create a xbmcgui.ListItem from provided movie details"""

    infolabels = {
        'dbid': item.get('movieid', constants.UNDEFINED),
        'mediatype': 'movie'
    }

    listitem = _create_listitem(item, None, infolabels)
    return listitem


def send_signal(sender, upnext_info):
    """Helper function for video plugins to send data to UpNext"""

    # Exit if not enough information provided by video plugin
    required_episode_info = ['current_episode', 'next_episode']
    required_plugin_info = ['play_url', 'play_info']
    if not (any(info in upnext_info for info in required_episode_info)
            and any(info in upnext_info for info in required_plugin_info)):
        log('Invalid UpNext info - {0}'.format(upnext_info), utils.LOGWARNING)
        return

    # Extract ListItem or InfoTagVideo details for use by UpNext
    upnext_data = {}
    for key, val in upnext_info.items():
        thumb = ''
        fanart = ''
        tvshowid = str(constants.UNDEFINED)

        if key in required_plugin_info:
            upnext_data[key] = val
            continue

        if isinstance(val, xbmcgui.ListItem):
            thumb = val.getArt('thumb')
            fanart = val.getArt('fanart')
            tvshowid = val.getProperty('tvshowid')
            val = val.getVideoInfoTag()

        if not isinstance(val, xbmc.InfoTagVideo):
            continue

        # Use show title as substitute for missing ListItem tvshowid
        tvshowid = (
            tvshowid if tvshowid != str(constants.UNDEFINED)
            else val.getTVShowTitle()
        ) or constants.UNDEFINED
        # Fallback for available date information
        firstaired = val.getFirstAired() or val.getPremiered() or val.getYear()
        # Runtime used to evaluate endtime in UpNext popup, if available
        runtime = val.getDuration() if utils.supports_python_api(18) else 0
        # Prefer outline over full plot for UpNext popup
        plot = val.getPlotOutline() or val.getPlot()
        # Prefer user rating over scraped rating
        rating = val.getUserRating() or val.getRating()

        upnext_data[key] = {
            'episodeid': val.getDbId(),
            'tvshowid': tvshowid,
            'title': val.getTitle(),
            'art': {
                'thumb': thumb,
                'tvshow.fanart': fanart,
            },
            'season': val.getSeason(),
            'episode': val.getEpisode(),
            'showtitle': val.getTVShowTitle(),
            'plot': plot,
            'playcount': val.getPlayCount(),
            'rating': rating,
            'firstaired': firstaired,
            'runtime': runtime
        }

    upnext_data = _copy_episode_details(upnext_data)

    utils.event(
        sender=sender,
        message='upnext_data',
        data=upnext_data,
        encoding='base64'
    )
