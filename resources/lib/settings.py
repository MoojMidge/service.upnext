# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals
from copy import copy
import constants
import utils


class UpNextSettings(object):  # pylint: disable=useless-object-inheritance
    """Class containing all addon settings"""

    __slots__ = (
        # Settings state variables
        'auto_play',
        'auto_play_delay',
        'demo_cue',
        'demo_mode',
        'demo_plugin',
        'demo_seek',
        'detector_data_limit',
        'detector_debug',
        'detector_threads',
        'detect_enabled',
        'detect_level',
        'detect_matches',
        'detect_mismatches',
        'detect_period',
        'detect_significance',
        'disabled',
        'enable_playlist',
        'enable_queue',
        'enable_resume',
        'mark_watched',
        'next_season',
        'played_limit',
        'popup_accent_colour',
        'popup_durations',
        'popup_position',
        'show_stop_button',
        'simple_mode',
        'skin_popup',
        'start_trigger',
        'unwatched_only',
    )

    def __init__(self):
        self.update()

    def __getitem__(self, name):
        return getattr(self, name, None)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __delitem__(self, name):
        return delattr(self, name)

    def __contains__(self, item):
        return hasattr(self, item)

    def copy(self):
        return copy(self)

    @classmethod
    def log(cls, msg, level=utils.LOGDEBUG):
        utils.log(msg, name='Settings', level=level)

    def update(self):
        self.log('Loading...')
        utils.ADDON = utils.get_addon(constants.ADDON_ID)
        utils.LOG_ENABLE_SETTING = utils.get_setting_int('logLevel')

        self.simple_mode = utils.get_setting_int('simpleMode') == 0
        self.show_stop_button = utils.get_setting_bool('stopAfterClose')
        self.skin_popup = utils.get_setting_bool('enablePopupSkin')
        self.popup_position = constants.POPUP_POSITIONS[
            utils.get_setting_int('popupPosition', default=0)
        ]

        accent_colour = constants.POPUP_ACCENT_COLOURS.get(
            utils.get_setting_int('popupAccentColour', default=0)
        )
        if not accent_colour:
            accent_colour = hex(
                (utils.get_setting_int('popupCustomAccentColourA') << 24)
                + (utils.get_setting_int('popupCustomAccentColourR') << 16)
                + (utils.get_setting_int('popupCustomAccentColourG') << 8)
                + utils.get_setting_int('popupCustomAccentColourB')
            )[2:]
        self.popup_accent_colour = accent_colour

        self.auto_play = utils.get_setting_int('autoPlayMode') == 0
        self.played_limit = (
            utils.get_setting_int('playedInARow')
            if self.auto_play and utils.get_setting_bool('enableStillWatching')
            else 0
        )

        self.enable_resume = utils.get_setting_bool('enableResume')
        self.enable_playlist = utils.get_setting_bool('enablePlaylist')

        self.mark_watched = utils.get_setting_int('markWatched')
        self.unwatched_only = not utils.get_setting_bool('includeWatched')
        self.next_season = utils.get_setting_bool('nextSeason')

        self.auto_play_delay = utils.get_setting_int('autoPlayCountdown')
        self.popup_durations = {
            3600: utils.get_setting_int('autoPlayTimeXL'),
            2400: utils.get_setting_int('autoPlayTimeL'),
            1200: utils.get_setting_int('autoPlayTimeM'),
            600: utils.get_setting_int('autoPlayTimeS'),
            0: utils.get_setting_int('autoPlayTimeXS')
        } if utils.get_setting_bool('customAutoPlayTime') else {
            0: utils.get_setting_int('autoPlaySeasonTime')
        }

        self.detect_enabled = utils.get_setting_bool('detectPlayTime')
        self.detect_period = utils.get_setting_int('detectPeriod')
        self.detect_level = utils.get_setting_int('detectLevel')

        self.disabled = utils.get_setting_bool('disableNextUp')
        self.enable_queue = utils.get_setting_bool('enableQueue')

        self.detector_threads = utils.get_setting_int('detectorThreads')
        self.detector_data_limit = utils.get_setting_int('detectorDataLimit')
        self.detect_significance = utils.get_setting_int('detectSignificance')
        self.detect_matches = utils.get_setting_int('detectMatches')
        self.detect_mismatches = utils.get_setting_int('detectMismatches')

        self.demo_mode = utils.get_setting_bool('enableDemoMode')
        self.demo_seek = self.demo_mode and utils.get_setting_int('demoSeek')
        self.demo_cue = self.demo_mode and utils.get_setting_int('demoCue')
        self.demo_plugin = (
            self.demo_mode and utils.get_setting_bool('demoPlugin')
        )

        self.detector_debug = utils.get_setting_bool('detectorDebug')
        self.start_trigger = utils.get_setting_bool('startTrigger')


settings = UpNextSettings()
