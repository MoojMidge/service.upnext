# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals
from api import (
    get_episodeid, get_next_from_library, get_next_in_playlist,
    get_now_playing, get_playlist_position, get_tvshowid, reset_queue
)
from utils import (
    get_int, get_setting_bool, get_setting_int, log as ulog
)


# keeps track of the state parameters
class UpNextState():

    def __init__(self, reset=None):
        # Settings state variables
        self.disabled = get_setting_bool('disableNextUp')
        self.auto_play = get_setting_int('autoPlayMode') == 0
        self.auto_play_delay = get_setting_int('autoPlayCountdown')
        self.unwatched_only = not get_setting_bool('includeWatched')
        self.enable_playlist = get_setting_bool('enablePlaylist')
        self.played_limit = get_setting_int('playedInARow')
        self.simple_mode = get_setting_int('simpleMode') == 0
        # Addon data
        self.data = {}
        self.encoding = 'base64'
        # Current file details
        self.filename = None
        self.tvshowid = None
        self.episodeid = None
        self.playcount = 0
        self.popup_time = 0
        self.popup_cue = False
        # Previous file details
        self.last_file = None
        # Internal state variables
        self.track = False
        self.queued = False
        self.playing_next = False
        self.played_in_a_row = 1
        # Player state
        self.starting = 0
        self.ended = 1

        self.log('Reset' if reset else 'Init', 2)

    @classmethod
    def log(cls, msg, level=2):
        ulog(msg, name=cls.__name__, level=level)

    def reset(self):
        self.__init__(reset=True)

    def set_last_file(self, filename):
        self.last_file = filename

    def get_last_file(self):
        return self.last_file

    def get_tracked_file(self):
        return self.filename

    def is_disabled(self):
        return self.disabled

    def is_tracking(self):
        return self.track

    def set_tracking(self, filename):
        msg = 'Tracking: {0}'
        if filename:
            self.filename = filename
            msg = msg.format('enabled - %s' % filename)
        else:
            msg = msg.format('disabled')
        self.log(msg, 2)
        self.track = bool(filename)

    def reset_queue(self):
        if self.queued:
            self.queued = reset_queue()

    def get_next(self):
        episode = None
        position = get_playlist_position()
        has_addon_data = self.has_addon_data()

        # File from non addon playlist
        if position and not has_addon_data:
            episode = get_next_in_playlist(position)

        # File from addon
        elif has_addon_data:
            episode = self.data.get('next_episode')
            self.log('Addon: next_episode - {0}'.format(episode), 2)

        # File from Kodi library
        else:
            episode, new_season = get_next_from_library(
                self.tvshowid,
                self.episodeid,
                self.unwatched_only
            )
            # Show Still Watching? popup if next episode is from next season
            if new_season:
                self.played_in_a_row = self.played_limit

        return episode, position

    def get_popup_time(self):
        return self.popup_time

    def set_popup_time(self, total_time):
        # Alway use metadata, when available
        popup_duration = get_int(self.data, 'notification_time')
        if 0 < popup_duration < total_time:
            self.popup_cue = True
            self.popup_time = total_time - popup_duration
            return

        # Some consumers send the offset when the credits start (e.g. Netflix)
        popup_time = get_int(self.data, 'notification_offset')
        if 0 < popup_time < total_time:
            self.popup_cue = True
            self.popup_time = popup_time
            return

        # Use a customized notification time, when configured
        if get_setting_bool('customAutoPlayTime'):
            if total_time > 60 * 60:
                duration_setting = 'autoPlayTimeXL'
            elif total_time > 40 * 60:
                duration_setting = 'autoPlayTimeL'
            elif total_time > 20 * 60:
                duration_setting = 'autoPlayTimeM'
            elif total_time > 10 * 60:
                duration_setting = 'autoPlayTimeS'
            else:
                duration_setting = 'autoPlayTimeXS'

        # Use one global default, regardless of episode length
        else:
            duration_setting = 'autoPlaySeasonTime'

        self.popup_cue = False
        self.popup_time = total_time - get_setting_int(duration_setting)

    def handle_addon_now_playing(self):
        item = self.data.get('current_episode')
        self.log('Addon: current_episode - {0}'.format(item), 2)
        if not item:
            return None

        tvshowid = get_int(item, 'tvshowid')

        # Reset play count if new show playing
        if self.tvshowid != tvshowid:
            msg = 'Reset played count: tvshowid change from {0} to {1}'
            msg = msg.format(
                self.tvshowid,
                tvshowid
            )
            self.log(msg, 2)
            self.tvshowid = tvshowid
            self.played_in_a_row = 1

        self.episodeid = get_int(item, 'episodeid')

        self.playcount = get_int(item, 'playcount', 0)

        return item

    def handle_library_now_playing(self):
        item = get_now_playing()
        if not item or item.get('type') != 'episode':
            return None

        # Get current tvshowid or search in library if detail missing
        tvshowid = get_int(item, 'tvshowid')
        if tvshowid == -1:
            title = item.get('showtitle').encode('utf-8')
            self.tvshowid = get_tvshowid(title)
            self.log('Fetched tvshowid: %s' % self.tvshowid, 2)

        # Reset play count if new show playing
        if self.tvshowid != tvshowid:
            msg = 'Reset played count: tvshowid change from {0} to {1}'
            msg = msg.format(
                self.tvshowid,
                tvshowid
            )
            self.log(msg, 2)
            self.tvshowid = tvshowid
            self.played_in_a_row = 1

        # Get current episodeid or search in library if detail missing
        self.episodeid = get_int(item, 'id')
        if self.episodeid == -1:
            self.episodeid = get_episodeid(
                tvshowid,
                item.get('season'),
                item.get('episode')
            )
            self.log('Fetched episodeid: %s' % self.episodeid, 2)

        self.playcount = get_int(item, 'playcount', 0)

        return item

    def has_addon_data(self):
        if self.data:
            if self.data.get('play_info'):
                return 2
            return 1
        return 0

    def reset_addon_data(self):
        self.data = {}

    def set_addon_data(self, data, encoding='base64'):
        self.log('set_addon_data: %s' % data, 2)
        self.data = data
        self.encoding = encoding
