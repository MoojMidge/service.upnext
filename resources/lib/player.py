# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals

import datetime

import api
import constants
import statichelper
import utils
import xbmc


class UpNextPlayerState(dict):
    def __getattr__(self, name):
        try:
            return self[name].get('value')
        except KeyError as error:
            raise AttributeError(error)  # pylint: disable=raise-missing-from

    def __setattr__(self, name, value):
        self.set(name, value)

    def forced(self, name):
        # If playing is forced all other player properties are also considered
        # to be forced
        if name not in self:
            return None
        if name == 'playing':
            return self['playing'].get('force')
        return self[name].get('force') or self['playing'].get('force')

    def set(self, name, *args, **kwargs):
        if name not in self:
            self[name] = {
                'value': None,
                'force': False,
                'actual': None
            }
        attr = self[name]

        if 'force' in kwargs:
            attr['value'] = args[0] if args else attr.get('actual')
            attr['force'] = kwargs['force']
        elif args:
            attr['actual'] = args[0]
            if not self.forced(name):
                attr['value'] = args[0]


class UpNextPlayer(xbmc.Player, object):
    """Inbuilt player function overrides"""

    __slots__ = (
        '_use_info',
        'player_state',
    )

    MEDIA_TYPES = {
        'episode': 'VideoPlayer(episodes)',
        'movie': 'VideoPlayer(movies)',
        # Other media types are not handled
        # 'video': 'VideoPlayer(files)',
        # 'musicvideo': 'VideoPlayer(musicvideos)',
        # 'channel': 'VideoPlayer(livetv)',
    }

    _get_status = staticmethod(xbmc.getCondVisibility)
    _get_info = staticmethod(xbmc.getInfoLabel)

    def __init__(self, use_info=True):
        self.log('Init')

        # Use Kodi infobools and infolabel rather than xbmc.Player methods
        self._use_info = use_info

        # Used to override player state for testing
        self.player_state = UpNextPlayerState()
        self.player_state.playing = False
        self.player_state.external_player = False
        self.player_state.paused = False
        self.player_state.playing_file = None
        self.player_state.speed = 0
        self.player_state.time = 0
        self.player_state.total_time = 0
        self.player_state.next_file = None
        self.player_state.type = constants.UNKNOWN
        self.player_state.playnext = None
        self.player_state.stop = None

        super(UpNextPlayer, self).__init__()

    # __enter__ and __exit__ allow UpNextPlayer to be used as a contextmanager
    # to check whether video is actually playing when getting video details
    def __enter__(self):
        return (self, True)

    def __exit__(self, exc_type, exc_value, traceback):
        return exc_type == RuntimeError

    @classmethod
    def log(cls, msg, level=utils.LOGDEBUG):
        utils.log(msg, name=cls.__name__, level=level)

    def isExternalPlayer(self):  # pylint: disable=invalid-name
        # Use inbuilt method to store actual value
        actual = (
            xbmc.Player.isExternalPlayer(self)
            if utils.supports_python_api(18)
            else False
        )
        self.player_state.external_player = actual
        # Return actual value or forced value if forced
        return self.player_state.external_player

    def isPlaying(self, use_info=None):  # pylint: disable=invalid-name, arguments-differ
        # Use inbuilt method to store actual value
        actual = (
            self._get_status('Player.HasMedia')
            if (use_info or self._use_info and use_info is None) else
            xbmc.Player.isPlaying(self)
        )
        self.player_state.playing = actual
        # Return actual value or forced value if forced
        return self.player_state.playing

    def is_paused(self):
        # Use inbuilt method to store actual value
        actual = self._get_status('Player.Paused')
        self.player_state.paused = actual
        # Return actual value or forced value if forced
        return self.player_state.paused

    def get_media_type(self, use_info=None):
        # Use current stored value if playing forced
        if self.player_state.forced('type'):
            actual = self.player_state.type
        # Use inbuilt method to store actual value if playing not forced
        elif (use_info or self._use_info and use_info is None):
            for media_type, info_bool in UpNextPlayer.MEDIA_TYPES.items():
                if self._get_status(info_bool):
                    actual = media_type
                    break
            else:
                actual = constants.UNKNOWN
        else:
            actual = statichelper.from_bytes(
                xbmc.Player.getVideoInfoTag(self).getMediaType()
            ) or constants.UNKNOWN
        self.player_state.type = actual
        # Return actual value or forced value if forced
        return self.player_state.type

    def getPlayingFile(self, use_info=None):  # pylint: disable=invalid-name, arguments-differ
        # Use current stored value if playing forced
        if self.player_state.forced('playing_file'):
            actual = self.player_state.playing_file
        # Use inbuilt method to store actual value if playing not forced
        else:
            actual = statichelper.from_bytes(
                self._get_info('Player.FilenameAndPath')
                if (use_info or self._use_info and use_info is None) else
                xbmc.Player.getPlayingFile(self)
            )
        self.player_state.playing_file = actual
        # Return actual value or forced value if forced
        return self.player_state.playing_file

    def get_speed(self, use_info=None):
        # Use current stored value if playing forced
        if self.player_state.forced('speed'):
            actual = self.player_state.speed
        # Use inbuilt method to store actual value if playing not forced
        else:
            actual = (
                utils.get_float(self._get_info('Player.PlaySpeed'),
                                default=1.0)
                if (use_info or self._use_info and use_info is None) else
                api.get_player_speed()
            )
        self.player_state.speed = actual
        # Return actual value or forced value if forced
        return self.player_state.speed

    def getTime(self, use_info=None):  # pylint: disable=invalid-name, arguments-differ
        # Use current stored value if playing forced
        if self.player_state.forced('time'):
            actual = self.player_state.time
        # Use inbuilt method to store actual value if playing not forced
        else:
            actual = (
                xbmc.Player.getTime(self)
                if not (use_info or self._use_info and use_info is None) else
                utils.get_int(self._get_info('Player.Time(secs)'))
                if utils.supports_python_api(18) else
                utils.time_to_seconds(self._get_info('Player.Time'))
            )
        self.player_state.time = actual

        # Simulate time progression if forced
        if self.player_state.forced('time'):
            now = datetime.datetime.now()

            # Change in time from previously forced time to now
            if isinstance(self.player_state.forced('time'), datetime.datetime):
                delta = self.player_state.forced('time') - now
                # No need to check actual speed, just use forced speed value
                delta = delta.total_seconds() * self.player_state.speed
            # Don't update if not previously forced
            else:
                delta = 0

            # Set new forced time
            new_time = self.player_state.time - delta
            self.player_state.set('time', new_time, force=now)

        # Return actual value or forced value if forced
        return self.player_state.time

    def getTotalTime(self, use_info=None):  # pylint: disable=invalid-name, arguments-differ
        # Use current stored value if playing forced
        if self.player_state.forced('total_time'):
            actual = self.player_state.total_time
        # Use inbuilt method to store actual value if playing not forced
        else:
            actual = (
                xbmc.Player.getTotalTime(self)
                if not (use_info or self._use_info and use_info is None) else
                utils.get_int(self._get_info('Player.Duration(secs)'))
                if utils.supports_python_api(18) else
                utils.time_to_seconds(self._get_info('Player.Duration'))
            )
        self.player_state.total_time = actual
        # Return actual value or forced value if forced
        return self.player_state.total_time

    def pause(self):
        # Set fake value if paused state forced
        if self.player_state.forced('paused'):
            toggle = not self.player_state.paused
            self.player_state.set('paused', toggle, force=True)
        # Use inbuilt method if not forced
        else:
            xbmc.Player.pause(self)

    def playnext(self):
        # Simulate playing next file if forced
        if (self.player_state.forced('playnext')
                or self.player_state.forced('next_file')):
            next_file = self.player_state.next_file
            self.player_state.set('next_file', None, force=True)
            self.player_state.set('playing_file', next_file, force=True)
            self.player_state.set('playing', bool(next_file), force=True)
        # Use inbuilt method if not forced
        else:
            xbmc.Player.playnext(self)

    def seekTime(self, seekTime):  # pylint: disable=invalid-name
        # Set fake value if playing forced
        if self.player_state.forced('time'):
            self.player_state.set('time', seekTime, force=True)
        # Use inbuilt method if not forced
        else:
            xbmc.Player.seekTime(self, seekTime)

    def stop(self):
        # Set fake value if playing forced
        if self.player_state.forced('stop'):
            self.player_state.set('playing', False, force=True)
        # Use inbuilt method if not forced
        else:
            xbmc.Player.stop(self)
