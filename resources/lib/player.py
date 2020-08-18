# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals
from xbmc import getCondVisibility, Player, Monitor
from api import Api
from playitem import PlayItem
from state import State
from utils import get_setting_bool, log as ulog


class UpNextPlayer(Player):
    """Service class for playback monitoring"""

    def __init__(self):
        self.api = Api()
        self.state = State()
        self.play_item = PlayItem()
        Player.__init__(self)

    @classmethod
    def log(cls, msg, level=2):
        ulog(msg, name=cls.__name__, level=level)

    def set_last_file(self, filename):
        self.state.last_file = filename

    def get_last_file(self):
        return self.state.last_file

    def is_tracking(self):
        return self.state.track

    def set_tracking(self, track=True):
        self.state.track = track

    def reset_queue(self):
        if self.state.queued:
            self.api.reset_queue()
            self.state.queued = False
            if not self.state.playing_next and not self.state.track:
                self.stop()

    def track_playback(self):
        self.state.starting = True
        monitor = Monitor()

        while not self.isPlaying() or not self.getTotalTime():
            if not self.state.starting:
                return
            monitor.waitForAbort(1)
        self.state.starting = False

        playlist_item = self.api.playlist_position()
        has_addon_data = self.api.has_addon_data()

        if playlist_item and not get_setting_bool('enablePlaylist'):
            return

        if self.state.track and has_addon_data and not self.state.playing_next:
            self.api.reset_addon_data()

        if playlist_item or has_addon_data or getCondVisibility('videoplayer.content(episodes)'):
            self.state.track = True
            self.reset_queue()
            self.play_item.handle_now_playing_result()

    if callable(getattr(Player, 'onAVStarted', None)):
        def onAVStarted(self):  # pylint: disable=invalid-name
            """Will be called when Kodi has a video or audiostream"""
            self.track_playback()
    else:
        def onPlayBackStarted(self):  # pylint: disable=invalid-name
            """Will be called when kodi starts playing a file"""
            self.track_playback()

    def onPlayBackPaused(self):  # pylint: disable=invalid-name
        self.state.pause = True

    def onPlayBackResumed(self):  # pylint: disable=invalid-name
        self.state.pause = False

    def onPlayBackStopped(self):  # pylint: disable=invalid-name
        """Will be called when user stops playing a file"""
        self.reset_queue()
        self.api.reset_addon_data()
        self.state = State()  # Reset state

    def onPlayBackEnded(self):  # pylint: disable=invalid-name
        """Will be called when Kodi has ended playing a file"""
        self.reset_queue()
        if not self.state.playing_next:
            self.api.reset_addon_data()
            self.state = State()  # Reset state

    def onPlayBackError(self):  # pylint: disable=invalid-name
        """Will be called when when playback stops due to an error"""
        self.reset_queue()
        self.api.reset_addon_data()
        self.state = State()  # Reset state
