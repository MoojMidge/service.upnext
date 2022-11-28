# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals
from settings import SETTINGS
import api
import constants
import utils


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
        self.current_item = {
            'details': {},
            'source': None,
            'media_type': None,
            'db_id': constants.UNDEFINED,
            'group_id': constants.UNDEFINED,
            'group_name': None,
            'group_idx': constants.UNDEFINED,
        }
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
        self.current_item = None
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
        media_type = self.current_item['media_type']
        playlist_position = api.get_playlist_position()
        plugin_type = self.get_plugin_type(playlist_position)

        # Next episode from plugin data
        if plugin_type:
            next_video = self.data.get('next_episode')
            source = constants.PLUGIN_TYPES[plugin_type]

            if (SETTINGS.unwatched_only
                    and utils.get_int(next_video, 'playcount') > 0):
                next_video = None
            self.log('Plugin next_episode: {0}'.format(next_video))

        # Next item from non-plugin playlist
        elif playlist_position and not self.shuffle_on:
            next_video = api.get_from_playlist(
                position=playlist_position,
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
                    not self.shuffle_on and next_video and
                    next_video['season']
                    != self.current_item['details']['season']
            ):
                self.played_in_a_row = SETTINGS.played_limit

        self.next_item = utils.create_item_details(
            next_video, source, media_type, playlist_position
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

            # Enable cue point unless forced off in demo mode
            self.popup_cue = SETTINGS.demo_cue != constants.SETTING_OFF

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
                # Enable cue point unless forced off in demo mode
                self.popup_cue = SETTINGS.demo_cue != constants.SETTING_OFF
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

            # Disable cue point unless forced on in demo mode
            self.popup_cue = SETTINGS.demo_cue == constants.SETTING_ON

        self.popup_time = popup_time
        self.total_time = total_time
        self._set_detect_time()

        self.log('Popup: due at {0}s of {1}s (cue: {2})'.format(
            self.popup_time, self.total_time, self.popup_cue
        ), utils.LOGINFO)

    def process_now_playing(self, playlist_position, plugin_type, media_type):
        if plugin_type:
            current_video = self._get_plugin_now_playing(media_type)
            source = constants.PLUGIN_TYPES[plugin_type]

        elif playlist_position:
            current_video = api.get_from_playlist(
                position=(playlist_position - 1),
                properties=(
                    api.MOVIE_PROPERTIES if media_type == 'movie' else
                    api.EPISODE_PROPERTIES
                )
            )
            source = 'playlist'

        elif media_type in ('episode', 'movie'):
            current_video = self._get_library_now_playing(media_type)
            source = 'library'

        else:
            current_video = None
            source = None

        if not current_video or not source:
            return None

        current_item = utils.create_item_details(
            current_video, source, media_type, playlist_position
        )

        # Reset played in a row count if new tvshow or set is playing, unless
        # playing from a playlist
        if (not playlist_position and self.current_item
                and self.current_item['group_id'] != current_item['group_id']):
            self.log(
                'Reset played count: {0} group_id changed - {1} to {2}'.format(
                    media_type,
                    self.current_item['group_id'],
                    current_item['group_id']
                )
            )
            self.played_in_a_row = 1

        self.current_item = current_item
        return self.current_item

    def _get_plugin_now_playing(self, media_type):
        if self.data:
            # Fallback to now playing info if plugin does not provide current
            # episode details
            current_video = (
                self.data.get('current_episode')
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

        self.log('Plugin current_episode: {0}'.format(current_video))
        if not current_video:
            return None

        return current_video

    @staticmethod
    def _get_library_now_playing(media_type):
        current_video = api.get_now_playing(
            properties=(
                api.MOVIE_PROPERTIES if media_type == 'movie' else
                api.EPISODE_PROPERTIES
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

        # Get current tvshowid or search in library if detail missing
        tvshowid = current_video.get('tvshowid', constants.UNDEFINED)
        if tvshowid == constants.UNDEFINED:
            tvshowid = api.get_tvshowid(current_video.get('showtitle'))

        # Now playing show not found in library
        if tvshowid == constants.UNDEFINED:
            return None
        current_video['tvshowid'] = tvshowid

        # Get current episode id or search in library if detail missing
        episodeid = (
            utils.get_int(current_video, 'episodeid', None)
            or utils.get_int(current_video, 'id')
        )
        if episodeid == constants.UNDEFINED:
            episodeid = api.get_episodeid(
                tvshowid,
                current_video.get('season'),
                current_video.get('episode')
            )
        # Now playing episode not found in library
        if episodeid == constants.UNDEFINED:
            return None
        current_video['episodeid'] = episodeid

        return current_video

    def get_plugin_type(self, playlist_position=None):
        if self.data:
            plugin_type = constants.PLUGIN_DATA_ERROR
            if playlist_position:
                plugin_type += constants.PLUGIN_PLAYLIST
            if self.data.get('play_url'):
                plugin_type += constants.PLUGIN_PLAY_URL
            elif self.data.get('play_info'):
                plugin_type += constants.PLUGIN_PLAY_INFO
            return plugin_type
        return None

    def set_plugin_data(self, data, encoding='base64'):
        if data:
            self.log('Plugin data: {0}'.format(data))
        self.data = data
        self.encoding = encoding
