# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals

import api
import constants
import upnext
import utils
from settings import SETTINGS


class UpNextState(object):  # pylint: disable=too-many-public-methods
    """Class encapsulating all state variables and methods"""

    __slots__ = (
        # Addon data
        'data',
        'encoding',
        # Current video details
        'current_item',
        'filename',
        'total_time',
        # Popup state variables
        'next_item',
        'popup_time',
        'popup_cue',
        'detect_time',
        'shuffle_on',
        # Tracking player state variables
        'starting',
        'tracking',
        'played_in_a_row',
        'queued',
        'playing_next',
        'keep_playing',
    )

    def __init__(self, reset=None):
        self.log('Reset' if reset else 'Init')

        # Plugin data
        self.data = None
        self.encoding = 'base64'
        # Current video details
        self.current_item = utils.create_item_details('empty')
        self.filename = None
        self.total_time = 0
        # Popup state variables
        self.next_item = None
        self.popup_time = 0
        self.popup_cue = False
        self.detect_time = 0
        self.shuffle_on = False
        # Tracking player state variables
        self.starting = 0
        self.tracking = False
        self.played_in_a_row = 1
        self.queued = False
        self.playing_next = False
        self.keep_playing = False

    @classmethod
    def log(cls, msg, level=utils.LOGDEBUG):
        utils.log(msg, name=cls.__name__, level=level)

    def reset(self):
        self.__init__(reset=True)  # pylint: disable=unnecessary-dunder-call

    def reset_item(self):
        self.current_item = utils.create_item_details('empty')
        self.next_item = None

    def get_tracked_file(self):
        return self.filename

    def is_tracking(self):
        return self.tracking

    def set_tracking(self, filename):
        if filename:
            self.tracking = True
            self.filename = filename
            self.log('Tracking enabled: {0}'.format(filename), utils.LOGINFO)
        else:
            self.tracking = False
            self.filename = None
            self.log('Tracking disabled')

    def reset_queue(self):
        if self.queued:
            self.queued = api.reset_queue()

    def get_next(self):
        """Get next video to play, based on current video source"""

        next_video = None
        source = None
        media_type = self.current_item['type']
        next_position, _ = api.get_playlist_position(offset=1)
        plugin_type = self.get_plugin_type(next_position)

        # Next episode from plugin data
        if plugin_type:
            next_video = self.data.get('next_video')
            source = constants.PLUGIN_TYPES[plugin_type]

            if (SETTINGS.unwatched_only
                    and utils.get_int(next_video, 'playcount') > 0):
                next_video = None
            self.log('Plugin next_video: {0}'.format(next_video))

        # Next item from non-plugin playlist
        elif next_position and not self.shuffle_on:
            next_video = api.get_from_playlist(
                position=next_position,
                properties=(api.EPISODE_PROPERTIES | api.MOVIE_PROPERTIES),
                unwatched_only=SETTINGS.unwatched_only
            )
            media_type = constants.UNDEFINED
            source = 'playlist'

        # Next video from Kodi library
        else:
            next_video = api.get_next_from_library(
                item=self.current_item,
                next_season=SETTINGS.next_season,
                unwatched_only=SETTINGS.unwatched_only,
                random=self.shuffle_on
            )
            source = 'library'

            # Show Still Watching? popup if next episode is from next season or
            # next item is a movie
            if media_type == 'movie' or (
                    not self.shuffle_on and next_video and len({
                        constants.SPECIALS,
                        next_video['season'],
                        self.current_item['details']['season']
                    }) == 3
            ):
                self.played_in_a_row = SETTINGS.played_limit

        if next_video:
            self.next_item = utils.create_item_details(
                next_video, source, media_type, next_position
            )
        return self.next_item

    def get_detect_time(self):
        return self.detect_time

    def _set_detect_time(self):
        # Don't use detection time period if an plugin cue point was provided,
        # or end credits detection is disabled
        if self.popup_cue or not SETTINGS.detect_enabled:
            self.detect_time = None
            return

        # Detection time period starts before normal popup time
        self.detect_time = max(
            0,
            self.popup_time - (SETTINGS.detect_period * self.total_time / 3600)
        )

    def get_popup_time(self):
        return self.popup_time

    def set_detected_popup_time(self, detected_time):
        popup_time = 0

        # Detected popup time overrides plugin data and settings
        if detected_time:
            # Force popup time to specified play time
            popup_time = detected_time

            # Enable cue point unless forced off in sim mode
            self.popup_cue = SETTINGS.sim_cue != constants.SETTING_OFF

        self.popup_time = popup_time
        self._set_detect_time()

        self.log('Popup: due at {0}s of {1}s (cue: {2})'.format(
            self.popup_time, self.total_time, self.popup_cue
        ), utils.LOGINFO)

    def set_popup_time(self, total_time):
        popup_time = 0

        # Alway use plugin data, when available
        if self.get_plugin_type():
            # Some plugins send the time from video end
            popup_duration = utils.get_int(self.data, 'notification_time', 0)
            # Some plugins send the time from video start (e.g. Netflix)
            popup_time = utils.get_int(self.data, 'notification_offset', 0)

            # Ensure popup duration is not too short
            if constants.POPUP_MIN_DURATION <= popup_duration < total_time:
                popup_time = total_time - popup_duration

            # Ensure popup time is not too close to end of playback
            if 0 < popup_time <= total_time - constants.POPUP_MIN_DURATION:
                # Enable cue point unless forced off in sim mode
                self.popup_cue = SETTINGS.sim_cue != constants.SETTING_OFF
            # Otherwise ignore popup time from plugin data
            else:
                popup_time = 0

        # Use addon settings as fallback option
        if not popup_time:
            # Time from video end
            popup_duration = SETTINGS.popup_durations[max(0, 0, *[
                duration for duration in SETTINGS.popup_durations
                if total_time > duration
            ])]

            # Ensure popup duration is not too short
            if constants.POPUP_MIN_DURATION <= popup_duration < total_time:
                popup_time = total_time - popup_duration
            # Otherwise set default popup time
            else:
                popup_time = total_time - constants.POPUP_MIN_DURATION

            # Disable cue point unless forced on in sim mode
            self.popup_cue = SETTINGS.sim_cue == constants.SETTING_ON

        self.popup_time = popup_time
        self.total_time = total_time
        self._set_detect_time()

        self.log('Popup: due at {0}s of {1}s (cue: {2})'.format(
            self.popup_time, self.total_time, self.popup_cue
        ), utils.LOGINFO)

    def process_now_playing(self, playlist_position, plugin_type, play_info):
        media_type = play_info.get('type')
        if plugin_type:
            new_video = self._get_plugin_now_playing(media_type)
            source = constants.PLUGIN_TYPES[plugin_type]

        elif playlist_position:
            new_video = api.get_from_playlist(
                position=playlist_position,
                properties=(
                    api.MOVIE_PROPERTIES if media_type == 'movie' else
                    api.EPISODE_PROPERTIES
                )
            )
            source = 'playlist'

        elif media_type in ('episode', 'movie'):
            new_video = self._get_library_now_playing(play_info)
            source = 'library'

        else:
            new_video = None
            source = None

        if new_video and source:
            new_item = utils.create_item_details(
                new_video, source, media_type, playlist_position
            )

            # Reset played in a row count if new tvshow or set is playing,
            # unless playing from a playlist
            new_group = new_item['group_name']
            current_group = self.current_item['group_name']
            if new_group != current_group:
                self.log('Reset playcount: group change - {0} to {1}'.format(
                    current_group, new_group
                ))
                self.played_in_a_row = 1

            self.current_item = new_item
        return self.current_item

    def _get_plugin_now_playing(self, media_type):
        if self.data:
            # Fallback to now playing info if plugin does not provide current
            # episode details
            current_video = (
                self.data.get('current_video')
                or api.get_now_playing(
                    properties=(
                        api.MOVIE_PROPERTIES if media_type == 'movie' else
                        api.EPISODE_PROPERTIES
                    ),
                    retry=SETTINGS.api_retry_attempts
                )
            )
        else:
            current_video = None

        self.log('Plugin current_video: {0}'.format(current_video))
        if not current_video:
            return None

        return current_video

    @classmethod
    def _get_library_now_playing(cls, play_info):  # pylint: disable=too-many-branches, too-many-return-statements
        media_type = play_info.get('type')
        current_video = api.get_now_playing(
            properties=(
                api.MOVIE_PROPERTIES if media_type == 'movie' else
                api.EPISODE_PROPERTIES | {'mediapath'}
            ),
            retry=SETTINGS.api_retry_attempts
        )
        if not current_video:
            return None

        if media_type == 'movie':
            return (
                current_video if utils.get_int(current_video, 'setid') > 0
                else None
            )

        # Previously resolved listitems may lose infotags that are set when the
        # listitem is resolved. Fallback to Player notification data.
        for info, value in play_info.get('item').items():
            current_value = current_video.get(info, '')
            if current_value in (constants.UNDEFINED, constants.UNKNOWN, ''):
                current_video[info] = value

        tvshowid = current_video.get('tvshowid', constants.UNDEFINED)
        title = current_video.get('showtitle')
        season = utils.get_int(current_video, 'season')
        episode = utils.get_int(current_video, 'episode')

        if not title or constants.UNDEFINED in (season, episode):
            return None

        filepath = current_video.get('file', '')
        mediapath = current_video.get('mediapath', '')
        for plugin_url in (filepath, mediapath):
            if plugin_url.startswith('plugin://'):
                break
        else:
            plugin_url = None

        if tvshowid == constants.UNDEFINED or plugin_url:
            # Video plugins can provide a plugin specific tvshowid. Search Kodi
            # library for tvshow title instead.
            tvshowid = api.get_tvshowid(title)
        # Now playing show not found in Kodi library
        if tvshowid == constants.UNDEFINED:
            return cls._get_tmdb_now_playing(
                current_video, title, season, episode, plugin_url
            ) if SETTINGS.enable_tmdbhelper_fallback else None
        # Use found tvshowid for library integrated plugins e.g. Emby,
        # Jellyfin, Plex, etc.
        current_video['tvshowid'] = tvshowid

        # Get current episode id or search in library if detail missing
        episodeid = (
            utils.get_int(current_video, 'episodeid', None)
            or utils.get_int(current_video, 'id')
        )
        if episodeid == constants.UNDEFINED:
            episodeid = api.get_episodeid(tvshowid, season, episode)
        # Now playing episode not found in library
        if episodeid == constants.UNDEFINED:
            return None
        current_video['episodeid'] = episodeid

        return current_video

    @staticmethod
    def _get_tmdb_now_playing(current_video, title, season, episode, url):
        from tmdb_helper import Player, TMDB

        addon_id, _, addon_args = utils.parse_url(url)
        if addon_id == constants.ADDON_ID and 'player' in addon_args:
            addon_id = addon_args['player']

        # TMDBHelper not importable, use plugin url instead
        if not TMDB.is_initialised():
            upnext.send_signal(sender='UpNext.TMDBHelper',
                               upnext_info={'current_video': current_video,
                                            'play_url': None,
                                            'player': addon_id,})
            return

        tmdb_id, current_video = TMDB().get_details(title, season, episode)
        if not tmdb_id or not current_video:
            return

        player = Player(query=title, season=season, episode=episode,  # pylint: disable=unexpected-keyword-arg
                        tbdb_id=tmdb_id, tmdb_type='tv',
                        player=addon_id, mode='play')

        if SETTINGS.queue_from_tmdb:
            player.queue()
            utils.event('OnAVStart', internal=True)
        else:
            episodes = player.get_next_episodes()
            if not episodes or len(episodes) < 2:
                return

            upnext.send_signal(sender='UpNext.TMDBHelper',
                               upnext_info={
                                   'current_video': dict(
                                       current_video['infolabels'],
                                       tmdb_id=tmdb_id,
                                       art=current_video['art'],
                                       showtitle=title,
                                   ),
                                   'next_video': dict(
                                       episodes[1].infolabels,
                                       tmdb_id=tmdb_id,
                                       art=episodes[1].art,
                                       showtitle=title,
                                   ),
                                   'play_url': None,
                                   'player': addon_id,
                               })

    def get_plugin_type(self, playlist_next=None):
        if self.data:
            plugin_type = constants.PLUGIN_DATA_ERROR
            if self.data.get('play_direct'):
                plugin_type += constants.PLUGIN_DIRECT
            elif playlist_next:
                plugin_type += constants.PLUGIN_PLAYLIST
            if self.data.get('play_url'):
                plugin_type += constants.PLUGIN_PLAY_URL
            elif self.data.get('play_info'):
                plugin_type += constants.PLUGIN_PLAY_INFO
            return plugin_type
        return None

    def set_plugin_data(self, plugin_data):
        if not plugin_data:
            self.data = None
            self.encoding = None
            return

        data, encoding = plugin_data
        self.log('Plugin data: {0}'.format(data))

        # Map to new data structure
        if 'current_episode' in data:
            data['current_video'] = data.pop('current_episode')
        if 'next_episode' in data:
            data['next_video'] = data.pop('next_episode')

        self.data = data
        self.encoding = encoding or 'base64'
