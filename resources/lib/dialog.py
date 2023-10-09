# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals

import datetime

import api
import constants
import statichelper
import utils
import xbmcgui


class UpNextPopup(xbmcgui.WindowXMLDialog, object):
    """Class for UpNext popup state variables and methods"""

    __slots__ = (
        'item',
        'shuffle_on',
        'stop_enable',
        'popup_position',
        'accent_colour',
        'cancel',
        'stop',
        'playnow',
        'countdown_total_time',
        'current_progress_percent',
        'progress_control',
    )

    def __init__(self, *args, **kwargs):
        self.log('Init: {0}'.format(args[0]))

        self.item = kwargs.get('item')
        self.shuffle_on = kwargs.get('shuffle_on')
        self.stop_enable = kwargs.get('stop_button')
        self.popup_position = kwargs.get('popup_position')
        self.accent_colour = kwargs.get('accent_colour')

        # Set info here rather than onInit to avoid dialog update flash
        self.set_info()

        self.cancel = False
        self.stop = False
        self.playnow = False
        self.countdown_total_time = None
        self.current_progress_percent = 100
        self.progress_control = None

        super(UpNextPopup, self).__init__(*args)

    # __enter__ and __exit__ allows UpNextPopup to be used as a contextmanager
    # to check whether popup is still open before accessing attributes
    def __enter__(self):
        return (self, True)

    def __exit__(self, exc_type, exc_value, traceback):
        return exc_type == AttributeError

    @classmethod
    def log(cls, msg, level=utils.LOGDEBUG):
        utils.log(msg, name=cls.__name__, level=level)

    def onInit(self):  # pylint: disable=invalid-name
        try:
            self.progress_control = self.getControl(
                constants.PROGRESS_CTRL_ID
            )
        # Occurs when skin does not include progress control
        except RuntimeError:
            self.progress_control = None
        else:
            self.update_progress_control()

    def onAction(self, action):  # pylint: disable=invalid-name
        if action == xbmcgui.ACTION_STOP:
            self.set_cancel(True)
            self.set_stop(True)
            self.close()
        elif action == xbmcgui.ACTION_NAV_BACK:
            self.set_cancel(True)
            self.close()

    def onClick(self, controlId):  # pylint: disable=invalid-name
        # Play now - Watch now / Still Watching
        if controlId == constants.PLAY_CTRL_ID:
            self.set_playnow(True)
            self.close()
        # Cancel - Close / Stop
        elif controlId == constants.CLOSE_CTRL_ID:
            self.set_cancel(True)
            if self.stop_enable:
                self.set_stop(True)
            self.close()
        # Shuffle play
        elif controlId == constants.SHUFFLE_CTRL_ID:
            if self.is_shuffle_on():
                self.set_shuffle(False)
            else:
                self.set_shuffle(True)
                self.set_cancel(True)
                self.close()

    def setProperty(self, key, value):  # pylint: disable=invalid-name
        # setProperty accepts bytes/str/unicode in Kodi18+ but truncates bytes
        # when a null byte (\x00) is encountered in Kodi19+
        key = statichelper.from_unicode(key)
        if isinstance(value, (bool, int, float)):
            value = str(value)
        value = statichelper.from_unicode(value)
        return super(UpNextPopup, self).setProperty(key, value)

    def set_info(self):
        self.setProperty(
            'stop_close_label',
            utils.localize(
                constants.STOP_STR_ID if self.stop_enable
                else constants.CLOSE_STR_ID
            )
        )
        self.setProperty('shuffle_enable', (self.shuffle_on is not None))
        self.setProperty('shuffle_on', bool(self.shuffle_on))
        self.setProperty('popup_position', self.popup_position)
        self.setProperty('accent_colour', self.accent_colour)

        if not self.item or 'details' not in self.item:
            self.item = None
            return

        details = self.item['details']
        media_type = self.item.get('type')

        if details:
            show_spoilers = utils.get_global_setting(
                'videolibrary.showunwatchedplots'
            ) if utils.supports_python_api(18) else constants.DEFAULT_SPOILERS

            date, date_string = utils.localize_date(
                str(details.get('firstaired', ''))
            )
            self.setProperty('firstaired', date_string)
            self.setProperty('premiered', date_string)

            art = details.get('art')
            if media_type == 'episode':
                self.setProperty('year', date_string)
                if constants.UNWATCHED_EPISODE_THUMB in show_spoilers:
                    art = api.art_fallbacks(
                        art=art, art_map=api.EPISODE_ART_MAP, replace=False
                    )
                else:
                    art = constants.NO_SPOILER_ART

            elif media_type == 'movie':
                self.setProperty('year', date.year if date else date_string)
                art = api.art_fallbacks(art=art)

            self.setProperty('fanart', art.get('fanart', ''))
            self.setProperty('landscape', art.get('landscape', ''))
            self.setProperty('clearart', art.get('clearart', ''))
            self.setProperty('clearlogo', art.get('clearlogo', ''))
            self.setProperty('poster', art.get('poster', ''))
            self.setProperty('thumb', art.get('thumb', ''))

            self.setProperty(
                'plot',
                details.get('plot', '')
                if constants.UNWATCHED_EPISODE_PLOT in show_spoilers else ''
            )
            self.setProperty('tvshowtitle', details.get('showtitle', ''))
            self.setProperty('title', details.get('title', ''))
            season = details.get('season')
            self.setProperty('season', '' if season is None else season)
            episode = details.get('episode', '')
            self.setProperty('episode', episode)
            self.setProperty(
                'seasonepisode',
                episode if season is None or episode == ''
                else constants.SEASON_EPISODE.format(season, episode)
            )
            rating = details.get('rating')
            self.setProperty(
                'rating',
                '' if rating is None else round(float(rating), 1)
            )
            self.setProperty('playcount', details.get('playcount', 0))
            self.setProperty('runtime', details.get('runtime', ''))
        self.item = details

    def set_item(self, item):
        self.item = item

    def update_progress(self, remaining):
        # Run time and end time for next episode
        runtime = utils.get_int(self.item, 'runtime', 0)
        if runtime:
            runtime = datetime.timedelta(seconds=runtime)
            endtime = utils.localize_time(datetime.datetime.now() + runtime)
            self.setProperty('endtime', endtime)

        # Remaining time countdown for current episode
        remaining_str = '{0:02.0f}'.format(remaining)
        self.log(remaining_str)
        self.setProperty('remaining', remaining_str)

        if not self.progress_control:
            return

        # Set total countdown time on initial progress update
        if remaining and self.countdown_total_time is None:
            self.countdown_total_time = remaining
        # Calculate countdown progress on subsequent updates
        elif remaining:
            percent = 100 * remaining / self.countdown_total_time
            self.current_progress_percent = min(100, max(0, percent))

        self.update_progress_control()

    def update_progress_control(self):
        self.progress_control.setPercent(self.current_progress_percent)

    def set_cancel(self, cancel):
        self.cancel = cancel

    def is_cancel(self):
        return self.cancel

    def set_stop(self, stop):
        self.stop = stop

    def is_stop(self):
        return self.stop

    def set_playnow(self, playnow):
        self.playnow = playnow

    def is_playnow(self):
        return self.playnow

    def set_shuffle(self, shuffle_state):
        self.shuffle_on = shuffle_state
        self.setProperty('shuffle_on', shuffle_state)

    def is_shuffle_on(self):
        return self.shuffle_on
