# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals

import constants
import file_utils
import statichelper
import utils
import xbmcaddon


class UpNextSettings(object):
    """Class containing all addon settings"""

    __slots__ = (
        '_store',
        '_get_bool',
        '_get_int',
        '_get_string',
        # Settings state variables
        'api_retry_attempts',
        'auto_play',
        'auto_play_delay',
        'detect_enabled',
        'detect_level',
        'detect_matches',
        'detect_mismatches',
        'detect_period',
        'detect_significance',
        'detector_data_limit',
        'detector_debug',
        'detector_debug_save',
        'detector_filter',
        'detector_resize_method',
        'detector_save_path',
        'detector_threads',
        'disabled',
        'early_queue_reset',
        'enable_movieset',
        'enable_playlist',
        'enable_tmdbhelper_fallback',
        'enable_queue',
        'enable_resume',
        'exact_tmdb_match',
        'import_tmdbhelper',
        'mark_watched',
        'next_season',
        'pause_until_next',
        'played_limit',
        'plugin_main_label',
        'plugin_secondary_label',
        'popup_accent_colour',
        'popup_durations',
        'popup_position',
        'queue_from_tmdb',
        'resume_from_end',
        'show_stop_button',
        'sim_cue',
        'sim_mode',
        'sim_plugin',
        'sim_seek',
        'simple_mode',
        'skin_popup',
        'start_delay',
        'start_trigger',
        'unwatched_only',
        'widget_debug',
        'widget_enable_cast',
        'widget_enable_tags',
        'widget_list_limit',
        'widget_refresh_all',
        'widget_refresh_period',
        'widget_unwatched_only',
    )

    def __init__(self):
        if utils.supports_python_api(20):
            _class = xbmcaddon.Settings
            self._get_bool = _class.getBool
            self._get_int = _class.getInt
            self._get_string = _class.getString
        else:
            _class = xbmcaddon.Addon
            self._get_bool = _class.getSettingBool
            self._get_int = _class.getSettingInt
            self._get_string = _class.getSetting
        self.update()

    def __getitem__(self, name):
        return getattr(self, name, None)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __delitem__(self, name):
        return delattr(self, name)

    def __contains__(self, item):
        return hasattr(self, item)

    @classmethod
    def log(cls, msg, level=utils.LOGDEBUG):
        utils.log(msg, name='Settings', level=level)

    def get_bool(self, key, default=None, echo=True):
        """Get an addon setting as boolean"""

        value = default
        try:
            value = self._get_bool(self._store, key)
            value = bool(value)
        # On Krypton or older, or when not a boolean
        except (AttributeError, TypeError):
            value = self.get_string(key, echo=False)
            value = constants.VALUE_FROM_STR.get(value.lower(), default)
        # Occurs when the addon is disabled
        except RuntimeError:
            value = default

        if echo:
            self.log(msg='{0}: {1}'.format(key, value))
        return value

    def get_int(self, key, default=None, echo=True):
        """Get an addon setting as integer"""

        value = default
        try:
            value = self._get_int(self._store, key)
            value = int(value)
        # On Krypton or older, or when not an integer
        except (AttributeError, TypeError):
            value = self.get_string(key, echo=False)
            value = utils.get_int(value, default=default, strict=True)
        # Occurs when the addon is disabled
        except RuntimeError:
            value = default

        if echo:
            self.log(msg='{0}: {1}'.format(key, value))
        return value

    def get_string(self, key, default='', echo=True):
        """Get an addon setting as string"""

        value = default
        try:
            value = self._get_string(self._store, key)
            value = statichelper.from_bytes(value)
        # Occurs when the addon is disabled
        except RuntimeError:
            value = default

        if echo:
            self.log(msg='{0}: {1}'.format(key, value))
        return value

    def update(self):  # pylint: disable=too-many-statements
        self.log('Loading...')
        if utils.supports_python_api(20):
            self._store = utils.get_addon(constants.ADDON_ID).getSettings()
        else:
            self._store = utils.get_addon(constants.ADDON_ID)
        utils.LOG_ENABLE_SETTING = self.get_int('logLevel')
        utils.DEBUG_LOG_ENABLE = utils.get_global_setting('debug.showloginfo')

        self.simple_mode = self.get_bool('simpleMode')
        self.show_stop_button = self.get_bool('stopAfterClose')
        self.skin_popup = self.get_bool('enablePopupSkin')
        self.popup_position = constants.POPUP_POSITIONS.get(
            self.get_int('popupPosition', default=0)
        )

        accent_colour = constants.POPUP_ACCENT_COLOURS.get(
            self.get_int('popupAccentColour', default=0)
        )
        if not accent_colour:
            if utils.supports_python_api(20):
                accent_colour = self.get_string('popupCustomAccentColour')
            else:
                accent_colour = hex(
                    (self.get_int('popupCustomAccentColourA') << 24)
                    + (self.get_int('popupCustomAccentColourR') << 16)
                    + (self.get_int('popupCustomAccentColourG') << 8)
                    + self.get_int('popupCustomAccentColourB')
                )[2:]
        self.popup_accent_colour = accent_colour

        self.widget_list_limit = self.get_int('widgetListLimit', default=25)
        self.widget_refresh_period = (
            60 * self.get_int('widgetRefreshPeriod', default=10)
        )
        self.widget_refresh_all = self.get_bool('widgetRefreshAll')

        self.widget_enable_cast = self.get_bool('widgetEnableCast')
        self.widget_enable_tags = self.get_bool('widgetEnableTags')
        self.widget_unwatched_only = not self.get_bool('widgetIncludeWatched')

        self.plugin_main_label = (
            self.get_int('pluginMainLabelToken1'),
            self.get_int('pluginMainLabelToken2'),
            self.get_int('pluginMainLabelToken3')
        )
        self.plugin_secondary_label = (
            self.get_int('pluginSecondaryLabelToken1'),
            self.get_int('pluginSecondaryLabelToken2'),
            self.get_int('pluginSecondaryLabelToken3')
        )

        self.auto_play = self.get_int('autoPlayMode') == 1
        self.played_limit = (
            self.get_int('playedInARow')
            if self.auto_play and self.get_bool('enableStillWatching')
            else 0
        )

        self.mark_watched = self.get_int('markWatched')
        self.enable_resume = self.get_bool('enableResume')
        self.pause_until_next = self.get_bool('pauseUntilNext')

        self.unwatched_only = not self.get_bool('includeWatched')
        self.next_season = self.get_bool('nextSeason')
        self.enable_playlist = self.get_bool('enablePlaylist')
        self.enable_movieset = self.get_bool('enableMovieset')

        self.auto_play_delay = self.get_int('autoPlayCountdown')
        self.popup_durations = {
            3600: self.get_int('autoPlayTimeXL'),  # > 60 minutes
            2400: self.get_int('autoPlayTimeL'),   # > 40 minutes
            1200: self.get_int('autoPlayTimeM'),   # > 20 minutes
            600: self.get_int('autoPlayTimeS'),    # > 10 minutes
            0: self.get_int('autoPlayTimeXS')      # < 10 minutes
        } if self.get_bool('customAutoPlayTime') else {
            0: self.get_int('autoPlaySeasonTime')
        }

        self.detect_enabled = self.get_bool('detectPlayTime')
        self.detect_period = self.get_int('detectPeriod')

        self.enable_queue = self.get_bool('enableQueue')
        self.early_queue_reset = self.get_bool('earlyQueueReset')

        self.enable_tmdbhelper_fallback = self.get_bool('enableTMDBHelper')
        self.import_tmdbhelper = (self.enable_tmdbhelper_fallback
                                  and self.get_bool('importTMDBHelper'))
        self.exact_tmdb_match = (self.import_tmdbhelper
                                 and self.get_bool('exactTMDBMatch'))
        self.queue_from_tmdb = (self.import_tmdbhelper
                                and self.get_bool('queueFromTMDB'))

        self.resume_from_end = self.get_int('resumeFromEnd') / 100

        self.start_delay = self.get_int('startDelay')
        self.api_retry_attempts = self.get_int('apiRetryAttempts')
        self.disabled = self.get_bool('disableNextUp')

        # Create valid directory here so that it can be used whenever settings
        # are changed rather than only when a module is imported i.e. on addon
        # start/restart
        self.detector_save_path = file_utils.make_legal_path(
            self.get_string('detectorSavePath')
        )
        self.detector_threads = self.get_int('detectorThreads')
        data_limit = self.get_int('detectorDataLimit')
        self.detector_data_limit = data_limit - data_limit % 8
        self.detector_filter = self.get_bool('detectorFilter')
        self.detector_resize_method = constants.PIL_RESIZE_METHODS.get(
            self.get_int('detectorResizeMethod', default=1)
        )
        self.detect_level = self.get_int('detectLevel')
        self.detect_significance = self.get_int('detectSignificance')
        self.detect_matches = self.get_int('detectMatches')
        self.detect_mismatches = self.get_int('detectMismatches')

        self.sim_mode = self.get_bool('enableSimMode')
        self.sim_seek = self.sim_mode and self.get_int('simSeek')
        self.sim_cue = self.sim_mode and self.get_int('simCue')
        self.sim_plugin = self.sim_mode and self.get_bool('simPlugin')

        self.detector_debug = self.get_bool('detectorDebug')
        self.detector_debug_save = (self.detector_save_path
                                    and self.get_bool('detectorDebugSave'))
        self.widget_debug = self.get_bool('widgetDebug')

        self.start_trigger = self.get_bool('startTrigger')

        self._store = None


SETTINGS = UpNextSettings()
