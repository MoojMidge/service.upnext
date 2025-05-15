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

    def __init__(self, reset=False, test=False):
        self.log('Reset' if reset else 'Init')

        # Plugin data
        self.data = None
        self.encoding = 'base64'
        # Current video details
        self.current_item = utils.create_item_details(item=None, reset=True)
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

        if test:
            api.DISABLE_RETRY = True

    @classmethod
    def log(cls, msg, level=utils.LOGDEBUG):
        utils.log(msg, name=cls.__name__, level=level)

    def reset(self):
        self.__init__(reset=True)  # pylint: disable=unnecessary-dunder-call

    def reset_item(self):
        if self.next_item:
            self.current_item = self.next_item
        else:
            self.current_item = utils.create_item_details(
                item=self.current_item,
                reset=True,
            )
        self.next_item = None

    def get_tracked_file(self):
        return self.filename

    def is_tracking(self):
        return self.tracking

    def start_tracking(self, filename):
        self.tracking = True
        self.filename = filename
        self.log('Tracking enabled: {0}'.format(filename), utils.LOGINFO)

    def stop_tracking(self):
        self.tracking = False
        self.log('Tracking stopped')

    def reset_tracking(self):
        self.tracking = False
        self.filename = None
        self.log('Tracking reset')

    def reset_queue(self, on_start=False):
        if self.queued:
            if on_start:
                playcount = self.played_in_a_row
                self.played_in_a_row = playcount + 1
                self.log('Increment group playcount for queued item: {0} to {1}'
                         .format(playcount, self.played_in_a_row))
            self.queued = api.reset_queue()

    def get_next(self):
        """Get next video to play, based on current video source"""

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
            if (next_video and (
                    next_video.get('type') == 'movie'
                    or (not self.shuffle_on
                        and len({constants.SPECIALS,
                                 next_video.get('season'),
                                 self.current_item['details']['season']}) == 3)
            )):
                self.played_in_a_row = SETTINGS.played_limit

        if next_video:
            self.next_item = utils.create_item_details(next_video, source,
                                                       next_position)
        return self.next_item

    def get_detect_time(self):
        return self.detect_time

    def _set_detect_time(self):
        # Don't use detection time period if a plugin cue point was provided,
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

        # Use 1s offset from total_time to try and avoid race condition with
        # internal Kodi playlist handling
        self.total_time = total_time
        if SETTINGS.enable_queue:
            total_time -= 1

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
        self._set_detect_time()

        self.log('Popup: due at {0}s of {1}s (cue: {2})'.format(
            self.popup_time, self.total_time, self.popup_cue
        ), utils.LOGINFO)

    def process_now_playing(self, playlist_position, plugin_type, play_info):
        if plugin_type:
            new_video = self._get_plugin_now_playing(play_info)
            source = constants.PLUGIN_TYPES[plugin_type]

        elif playlist_position:
            new_video = api.get_from_playlist(
                position=playlist_position,
                properties=api.get_json_properties(play_info)
            )
            source = 'playlist'

        else:
            new_video = self._get_library_now_playing(play_info)
            source = 'library' if new_video else None

        if new_video and source:
            new_item = utils.create_item_details(new_video, source,
                                                 playlist_position)

            # Reset played in a row count if new tvshow or set is playing,
            # unless playing from a playlist
            new_group = new_item['group_name']
            current_group = self.current_item['group_name']
            if new_group != current_group:
                self.played_in_a_row = 1
                self.log('Reset playcount: group change - {0} to {1}'.format(
                    current_group, new_group
                ))

            self.current_item = new_item
        return self.current_item

    def _get_plugin_now_playing(self, play_info):
        if self.data:
            # Fallback to now playing info if plugin does not provide current
            # episode details
            current_video = self.data.get('current_video')
            if not current_video:
                current_video = api.get_now_playing(
                    properties=api.get_json_properties(play_info),
                    retry=SETTINGS.api_retry_attempts,
                )
        else:
            current_video = None

        self.log('Plugin current_video: {0}'.format(current_video))
        if not current_video:
            return None

        return current_video

    @classmethod
    # pylint: disable-next=too-many-branches,too-many-return-statements,too-many-locals
    def _get_library_now_playing(cls, play_info):
        if 'id' in play_info['item']:
            current_video = api.get_from_library(item=play_info['item'])
        else:
            current_video = api.get_now_playing(
                properties=api.get_json_properties(play_info, {'mediapath'}),
                retry=SETTINGS.api_retry_attempts
            )
        if not current_video:
            return None

        if current_video['type'] == 'movie':
            if (current_video['set']
                    and utils.get_int(current_video, 'setid') > 0):
                return current_video
            return None

        # Previously resolved listitems may lose infotags that are set when the
        # listitem is resolved. Fallback to Player notification data.
        values_to_ignore = {constants.UNDEFINED, constants.UNKNOWN, ''}
        for info, value in play_info['item'].items():
            if current_video.get(info, '') in values_to_ignore:
                current_video[info] = value

        tvshowid = current_video.get('tvshowid', constants.UNDEFINED)
        title = current_video.get('showtitle')
        season = utils.get_int(current_video, 'season')
        episode = utils.get_int(current_video, 'episode')

        if not title or constants.UNDEFINED in {season, episode}:
            return None

        plugin_url = None
        addon_id = None
        supported_addons = {constants.ADDON_ID, constants.TMDBH_ADDON_ID}
        params_to_replace = ('player', 'tmdb_id', 'season', 'episode')
        for plugin_url_type in ('mediapath', 'file'):
            _plugin_url = current_video.get(plugin_url_type, '')
            if (_plugin_url == plugin_url
                    or not _plugin_url.startswith('plugin://')):
                continue
            plugin_url = _plugin_url
            addon_id, _, addon_args = utils.parse_url(plugin_url)
            if addon_id in supported_addons:
                addon_id = None
            else:
                break
            for param in params_to_replace:
                value = addon_args.get(param, '')
                if value in values_to_ignore:
                    continue
                current_video[param] = value

        if tvshowid == constants.UNDEFINED or plugin_url:
            # Video plugins can provide a plugin specific tvshowid. Search Kodi
            # library for tvshow title instead.
            tvshowid = api.get_tvshowid(title)
        # Now playing show not found in Kodi library
        if tvshowid == constants.UNDEFINED:
            if SETTINGS.enable_tmdbhelper_fallback:
                return cls._get_tmdb_now_playing(
                    current_video, title, season, episode, addon_id
                )
            return None
        # Use found tvshowid for library integrated plugins e.g. Emby,
        # Jellyfin, Plex, etc.
        current_video['tvshowid'] = tvshowid

        # Get current episode id or search in library if detail missing
        episodeid = (utils.get_int(current_video, 'episodeid', None)
                     or utils.get_int(current_video, 'id'))
        if episodeid == constants.UNDEFINED:
            details = api.get_episode_info(tvshowid, season, episode)
            # Now playing episode not found in library
            if not details:
                return None
            current_video = dict(current_video, **details)
        else:
            current_video['episodeid'] = episodeid

        return current_video

    @staticmethod
    # pylint: disable-next=too-many-locals
    def _get_tmdb_now_playing(current_video, title, season, episode, addon_id):
        # TMDBHelper not importable, use plugin url instead
        if SETTINGS.import_tmdbhelper:
            from tmdb_helper import (
                Players,
                TMDb,
                get_item_details,
                get_next_episodes,
                queue_episodes,
            )

            no_integration = not TMDb.is_initialised()
        else:
            no_integration = True

        player_name = current_video.get('player', addon_id)
        if no_integration:
            upnext.send_signal(
                sender='UpNext.TMDBHelper',
                upnext_info={
                    'current_video': current_video,
                    'play_url': None,
                    'player': player_name,
                }
            )
            return

        season = utils.get_int(current_video, 'season', season)
        episode = utils.get_int(current_video, 'episode', episode)
        # noinspection PyUnboundLocalVariable
        # pylint: disable-next=possibly-used-before-assignment,no-value-for-parameter
        tmdb_id = current_video.get('tmdb_id') or TMDb().get_tmdb_id(
            tmdb_type='tv', query=title, season=season, episode=episode
        )
        # noinspection PyUnboundLocalVariable
        # pylint: disable-next=possibly-used-before-assignment,not-callable
        current_video = get_item_details(
            tmdb_type='tv', tmdb_id=tmdb_id, season=season, episode=episode
        )
        if not tmdb_id or not current_video:
            return

        # noinspection PyUnboundLocalVariable
        # pylint: disable-next=possibly-used-before-assignment,no-value-for-parameter,unexpected-keyword-arg
        players = Players(tmdb_type='tv',
                          tmdb_id=tmdb_id,
                          season=season,
                          episode=episode,
                          ignore_default=False,
                          islocal=False,
                          player=player_name,
                          mode='play')

        player = players.current_player or players.get_default_player()
        player = (player and player.get('file')) or player_name
        # noinspection PyUnboundLocalVariable
        # pylint: disable-next=possibly-used-before-assignment
        episodes = get_next_episodes(tmdb_id, season, episode, player)
        if not episodes:
            return

        # noinspection PyUnboundLocalVariable
        # pylint: disable-next=possibly-used-before-assignment
        if player and SETTINGS.queue_from_tmdb and queue_episodes(episodes):
            utils.event('OnAVStart', internal=True)
        else:
            upnext.send_signal(sender='UpNext.TMDBHelper',
                               upnext_info={
                                   'current_video': dict(
                                       current_video.infolabels,
                                       tmdb_id=tmdb_id,
                                       art=current_video.art,
                                       showtitle=title,
                                   ),
                                   'next_video': dict(
                                       episodes[1].infolabels,
                                       tmdb_id=tmdb_id,
                                       art=episodes[1].art,
                                       showtitle=title,
                                   ),
                                   'play_url': None,
                                   'player': player,
                               })

    def get_plugin_type(self, playlist_next=None):
        if self.data:
            _get = self.data.get
            plugin_type = constants.PLUGIN_DATA_ERROR
            if _get('play_direct'):
                plugin_type += constants.PLUGIN_DIRECT
            elif playlist_next:
                plugin_type += constants.PLUGIN_PLAYLIST
            if _get('play_url'):
                plugin_type += constants.PLUGIN_PLAY_URL
            elif _get('play_info'):
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
