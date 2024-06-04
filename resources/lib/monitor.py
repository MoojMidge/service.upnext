# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals

from time import time

import api
import constants
import detector
import player
import popuphandler
import simulation
import state
import statichelper
import utils
import xbmc
from settings import SETTINGS


class UpNextMonitor(xbmc.Monitor, object):
    """Monitor service for Kodi"""

    __slots__ = (
        '_idle',
        '_monitoring',
        '_queue_length',
        '_started',
        '_detector',
        '_popuphandler',
        'detector',
        'player',
        'popuphandler',
        'state',
    )

    def __init__(self):
        if SETTINGS.disabled:
            return

        self.log('Init')

        self._idle = [constants.IDLE_STATE['idle'], 0]
        self._monitoring = False
        self._queue_length = 0
        self._started = False

        self._detector = None
        self._popuphandler = None

        self.detector = None
        self.player = None
        self.popuphandler = None
        self.state = None

        super(UpNextMonitor, self).__init__()

    @classmethod
    def log(cls, msg, level=utils.LOGDEBUG):
        utils.log(msg, name=cls.__name__, level=level)

    # pylint: disable=too-many-return-statements
    def _check_video(self, plugin_data=None, player_data=None):
        # Only process one start at a time unless plugin data has been received
        if self.state.starting and not plugin_data:
            return
        # Increment starting counter
        self.state.starting += 1
        start_num = max(1, self.state.starting)
        self.log('Starting video check attempt #{0}'.format(start_num))

        # onPlayBackEnded for current file can trigger after next file starts
        # Wait additional 5s after onPlayBackEnded or last start
        wait_count = SETTINGS.start_delay * start_num
        while not self.abortRequested() and wait_count > 0:
            self.waitForAbort(1)
            wait_count -= 1

        # Get video details, exit if no video playing
        api.cache_invalidate()
        play_info = self._get_playback_details(player_data)
        if not play_info:
            self.log('Skip video check: nothing playing', utils.LOGWARNING)
            self.state.starting = 0
            return
        self.log('Playing: {item} - {file}'.format(**play_info))

        # Exit if starting counter has been reset or new start detected or
        # starting state has been reset by playback error/end/stop
        if not self.state.starting or start_num != self.state.starting:
            self.log('Skip video check: playing item not fully loaded')
            return
        self.state.starting = 0

        if (play_info['file'].startswith((
                'bluray://', 'dvd://', 'udf://', 'iso9660://', 'cdda://'
        )) or play_info['file'].endswith((
                '.bdmv', '.iso', '.ifo'
        ))):
            self.log('Skip video check: Blu-ray/DVD/CD playing')
            return

        if utils.get_property('PseudoTVRunning') == 'True':
            self.log('Skip video check: PseudoTV detected')
            return

        if self.player.isExternalPlayer():
            self.log('Skip video check: external player detected')
            return

        # Exit if UpNext playlist handling has not been enabled
        playlist_position, playlist_remaining = api.get_playlist_position()
        if playlist_remaining and not SETTINGS.enable_playlist:
            self.log('Skip video check: playlist handling not enabled')
            return

        # Exit if UpNext movie set handling has not been enabled
        if (not playlist_remaining
                and not SETTINGS.enable_movieset
                and play_info['type'] == 'movie'):
            self.log('Skip video check: movie set handling not enabled')
            return

        # Use new plugin data if provided or erase old plugin data.
        # Note this may cause played in a row count to reset incorrectly if
        # playlist of mixed non-plugin and plugin content is used
        self.state.set_plugin_data(plugin_data)
        plugin_type = self.state.get_plugin_type(playlist_remaining)

        # Start tracking if UpNext can handle the currently playing video
        # Process now playing video to get episode details and save playcount
        now_playing_item = self.state.process_now_playing(
            playlist_position if playlist_remaining else None,
            plugin_type,
            play_info
        )
        if now_playing_item and now_playing_item['details']:
            self.state.start_tracking(play_info['file'])
            self.state.reset_queue()

            # Store popup time and check if cue point was provided
            self.state.set_popup_time(play_info['duration'])

            # Handle sim mode functionality and notification
            skip_tracking = simulation.handle_sim_mode(
                player=self.player,
                state=self.state,
                now_playing_item=now_playing_item
            )

            if not skip_tracking:
                self._start_tracking(play_info)
            return

        self.log('Skip video check: UpNext unable to handle playing item')
        if self.state.is_tracking():
            self.state.reset()

    def _event_handler_av_start(self, **kwargs):
        # Delay event handler execution to allow events to queue up
        self.waitForAbort(1)
        # Clear queue to stop processing additional queued events
        self._queue_length = 0

        # Remove remnants from previous operations
        self._stop_detector()
        self._stop_popuphandler()

        # Playback can start without triggering a stop callback on previous
        # video. Reset state if playback was not requested by UpNext
        if not self.state.playing_next and not self.state.starting:
            self.state.reset()
        # Otherwise just ensure details of current/next item to play are reset
        else:
            self.state.reset_item()
        self.state.playing_next = False

        data, _ = utils.decode_data(serialised_json=kwargs.get('data'))
        # Check whether UpNext can start tracking
        self._check_video(player_data=data)

    def _event_handler_player_general(self, **_kwargs):
        # Delay event handler execution to allow events to queue up
        self.waitForAbort(1)
        # Only process this event if it is the last in the queue
        if self._queue_length != 1:
            return

        play_info = self._get_playback_details()

        # Update stored video resolution if detector is running
        if play_info and self.detector and not self.detector.credits_detected():
            self.detector.get_video_resolution(_cache=[None])
            if (play_info['speed'] == 1
                    and not self.state.is_tracking()
                    and not self.detector.is_alive()):
                utils.run_threaded(self.detector.start)

        # Restart tracking if previously enabled
        self._start_tracking(play_info)

    def _event_handler_player_start(self, **_kwargs):
        # Workaround for service.trakt failing to track watched time if current
        # playlist position changes after its onAVStarted callback executes
        self.state.reset_queue()

    def _event_handler_player_stop(self, **_kwargs):
        # Delay event handler execution to allow events to queue up
        self.waitForAbort(1)
        # Only process this event if it is the last in the queue
        if self._queue_length != 1:
            return

        # Remove remnants from previous operations
        self._stop_detector()
        self._stop_popuphandler()

        self.state.reset_queue()
        # OnStop can occur before/after the next video has started playing
        # Full reset of state if UpNext has not requested the next file to play
        if not self.state.playing_next and not self.state.starting:
            self.state.reset()
        # Otherwise just ensure details of current/next item to play are reset
        else:
            self.state.reset_item()

    def _event_handler_screensaver_off(self, **kwargs):
        # Don't handle event if Kodi is shutting down
        data, _ = utils.decode_data(serialised_json=kwargs.get('data'))
        if data and data.get('shuttingdown'):
            return

        # Update idle state for widget refresh
        self._idle[0] = constants.IDLE_STATE['idle']

        # Delay event handler execution to allow events to queue up
        self.waitForAbort(1)
        # Only process this event if it is the last in the queue
        if self._queue_length != 1:
            return

        # Restart tracking if previously enabled
        self._start_tracking()

        self._widget_reload()

    def _event_handler_screensaver_on(self, **_kwargs):
        # Update idle state for widget refresh
        self._idle[0] = constants.IDLE_STATE['sleeping']

    def _event_handler_upnext_trigger(self, **_kwargs):
        # Remove remnants from previous operations
        self._stop_popuphandler(restart=True)
        # If existing popuphandler is running, allow it to restart
        if self.popuphandler:
            return

        play_info = self._get_playback_details()

        # Exit if not playing, paused, or rewinding
        if not play_info or play_info['speed'] < 1:
            self.log('Skip trigger: nothing playing', utils.LOGINFO)
            return

        # Determine time until popup is required, scaled to real time
        popup_delay = utils.calc_wait_time(
            end_time=self.state.get_popup_time(),
            start_time=play_info['time'],
            rate=play_info['speed']
        )

        # Schedule popuphandler to start when required
        if popup_delay is not None:
            self.log('Popuphandler starting in {0}s'.format(popup_delay))
            self._popuphandler = utils.run_threaded(
                self._launch_popup,
                delay=popup_delay
            )

    def _event_handler_upnext_signal(self, **kwargs):
        # Delay event handler execution to allow events to queue up
        self.waitForAbort(1)
        # Clear queue to stop processing additional queued events
        self._queue_length = 0

        sender = kwargs.get('sender').replace('.SIGNAL', '')
        data = kwargs.get('data')

        decoded_data, encoding = utils.decode_data(data)
        if not decoded_data or not isinstance(decoded_data, dict):
            self.log('{0} plugin, sent {1} as {2}'.format(
                sender, decoded_data, data
            ), utils.LOGWARNING)
            return
        self.log('Data received from {0}'.format(sender), utils.LOGINFO)
        decoded_data.update(id='{0}_play_action'.format(sender))

        # Initial processing of data to start tracking
        self._check_video(plugin_data=(decoded_data, encoding))

    def _get_playback_details(self, player_data=None):
        if player_data:
            item_details = player_data.get('item', {})
            player_details = player_data.get('player')
        else:
            item_details = {}
            player_details = None

        with utils.ContextManager(self, 'player') as (_player, error):
            if error is AttributeError:
                raise error
            if not _player.isPlaying(use_info=False):
                return None
            play_info = {
                'playerid': (player_details.get('playerid') if player_details
                             else None),
                'file': _player.getPlayingFile(),
                'item': item_details,
                'type': (item_details.get('type') if item_details
                         else _player.get_media_type()),
                'speed': (player_details.get('speed') if player_details
                          else _player.get_speed()),
                'time': _player.getTime(),
                'duration': _player.getTotalTime(),
            }
            error = False
        if error:
            return None

        # Update idle state for widget refresh
        self._idle[0] = constants.IDLE_STATE['active']

        return play_info

    def _launch_detector(self):
        del self._detector
        self._detector = None

        play_info = self._get_playback_details()
        # Exit if not playing, paused, or rewinding
        if not play_info or play_info['speed'] < 1:
            return

        # Start detector to detect end credits and trigger popup
        self.log('Detector started at {time}s of {duration}s'.format(
            **play_info), utils.LOGINFO)
        if not self.detector:
            self.detector = detector.UpNextDetector(
                player=self.player,
                state=self.state
            )

        self.detector.start()

    def _launch_popup(self):
        del self._popuphandler
        self._popuphandler = None

        play_info = self._get_playback_details()
        if not play_info:
            return

        # Stop second thread and popup from being created after next video
        # has been requested but not yet loaded
        self.state.stop_tracking()

        # Start popuphandler to show popup and handle playback of next video
        self.log('Popuphandler started at {time}s of {duration}s'.format(
            **play_info), utils.LOGINFO)
        if not self.popuphandler:
            self.popuphandler = popuphandler.UpNextPopupHandler(
                player=self.player,
                state=self.state
            )
        # Check if popuphandler found a video to play next
        # pylint: disable=assignment-from-no-return
        has_next_item = self.popuphandler.start()
        # And check whether popup/playback was cancelled/stopped by the user
        playback_cancelled = (
                has_next_item
                and self.state.keep_playing
                and not self.state.playing_next
        )
        # Stop popuphandler and release resources
        self._stop_popuphandler(terminate=True)

        # Update playcount and reset resume point of previous file
        if not playback_cancelled and SETTINGS.mark_watched and self.state:
            utils.run_threaded(target=api.handle_just_watched,
                               delay=5,
                               kwargs={
                                   'item': self.state.current_item.copy(),
                                   'reset_playcount': (SETTINGS.mark_watched ==
                                                       constants.SETTING_OFF),
                                   'resume_from_end': SETTINGS.resume_from_end,
                               })

        if not self.detector:
            self._stop_detector()
            return

        # If credits were (in)correctly detected and popup is cancelled
        # by the user, then restart tracking loop to allow detector to
        # restart, or to launch popup at default time
        if self.detector.credits_detected() and playback_cancelled:
            # Reset detector match counts
            self.detector.reset()

            # Reset popup time, restart tracking, and trigger a new popup
            self.state.set_popup_time(play_info['duration'])
            self.state.start_tracking(play_info['file'])
            utils.event('upnext_trigger', internal=True)
            return

        # Store hashes and timestamp for current video
        # Stop detector and release resources
        self._stop_detector(terminate=True, store=True)

    def _start_tracking(self, play_info=None):
        if not play_info:
            play_info = self._get_playback_details()

        # Exit if tracking disabled
        if not self.state.is_tracking():
            return

        # Remove remnants from previous operations
        self._stop_detector()
        self._stop_popuphandler()

        # Exit if not playing, paused, or rewinding
        if not play_info or play_info['speed'] < 1:
            self.log('Skip tracking: nothing playing', utils.LOGINFO)
            return

        # Stop tracking if new stream started
        if self.state.get_tracked_file() != play_info['file']:
            self.log('Unknown file playing', utils.LOGWARNING)
            self.state.reset_tracking()
            self._stop_detector(terminate=True, store=True)
            return

        # Determine time until popup is required, scaled to real time
        popup_delay = utils.calc_wait_time(
            end_time=self.state.get_popup_time(),
            start_time=play_info['time'],
            rate=play_info['speed']
        )

        # Determine time until detector is required, scaled to real time
        detector_delay = utils.calc_wait_time(
            end_time=self.state.get_detect_time(),
            start_time=play_info['time'],
            rate=play_info['speed']
        )

        # Schedule detector to start when required
        if detector_delay is not None:
            self.log('Detector starting in {0}s'.format(detector_delay))
            self._detector = utils.run_threaded(
                self._launch_detector,
                delay=detector_delay
            )

        # Schedule popuphandler to start when required
        if popup_delay is not None:
            self.log('Popuphandler starting in {0}s'.format(popup_delay))
            self._popuphandler = utils.run_threaded(
                self._launch_popup,
                delay=popup_delay
            )

    def _stop_detector(self, terminate=False, store=False):
        detector_timer = getattr(self, '_detector', None)
        if detector_timer:
            detector_timer.cancel()
            del self._detector
            self._detector = None

        detector_instance = getattr(self, 'detector', None)
        if detector_instance:
            if store:
                detector_instance.store_data()
            detector_instance.stop(terminate=terminate)
            if terminate:
                del self.detector
                self.detector = None
                self.log('Cleanup detector')

    def _stop_popuphandler(self, restart=False, terminate=False):
        popuphandler_timer = getattr(self, '_popuphandler', None)
        if popuphandler_timer:
            popuphandler_timer.cancel()
            del self._popuphandler
            self._popuphandler = None

        popuphandler_instance = getattr(self, 'popuphandler', None)
        if popuphandler_instance:
            popuphandler_instance.stop(restart=restart, terminate=terminate)
            if terminate:
                del self.popuphandler
                self.popuphandler = None
                self.log('Cleanup popuphandler')

    def _widget_reload(self, init=False):
        if self._idle[0] != constants.IDLE_STATE['idle']:
            return 0
        now = int(time())
        if init:
            if xbmc.getCondVisibility('System.ScreenSaverActive'):
                self._idle[0] = constants.IDLE_STATE['sleeping']
            self._idle[1] = now
        delta = now - self._idle[1]
        if delta <= SETTINGS.widget_refresh_period - 10:
            return delta
        self.log('Widget reload')
        self._idle[1] = now
        utils.set_property(constants.WIDGET_RELOAD_PROPERTY_NAME, str(now))
        return 0

    def start(self, **kwargs):
        if SETTINGS.disabled:
            return

        self.log('UpNext starting', utils.LOGINFO)

        self.state = kwargs.get('state') or state.UpNextState()
        self.player = kwargs.get('player') or player.UpNextPlayer()

        self._started = True

        # Re-trigger player play/start event if addon started mid playback
        if SETTINGS.start_trigger and self.player.isPlaying():
            # This is a fake event, use Other.OnAVStart
            utils.event('OnAVStart', internal=True)

        if self._monitoring:
            return
        self._monitoring = True

        # Set initial idle state for widget refresh
        delta = self._widget_reload(init=True)

        # Wait indefinitely until addon is terminated, but periodically
        # update widgets
        while not self.waitForAbort(SETTINGS.widget_refresh_period - delta):
            delta = self._widget_reload()

        # Cleanup when abort requested
        self.stop()

    def stop(self):
        self.log('UpNext exiting', utils.LOGINFO)

        # Free references/resources
        self._stop_detector(terminate=True)
        self._stop_popuphandler(terminate=True)
        self.waitForAbort(1)

        del self.state
        self.state = None
        self.log('Cleanup state')
        del self.player
        self.player = None
        self.log('Cleanup player')

        self._started = False

    EVENTS_MAP = {
        'Other.upnext_credits_detected': _event_handler_upnext_trigger,
        'Other.upnext_data': _event_handler_upnext_signal,
        'Other.upnext_trigger': _event_handler_upnext_trigger,
        'Other.OnAVStart': _event_handler_av_start,
        'GUI.OnScreensaverActivated': _event_handler_screensaver_on,
        'GUI.OnScreensaverDeactivated': _event_handler_screensaver_off,
        'Player.OnPause': _event_handler_player_general,
        'Player.OnResume': _event_handler_player_general,
        'Player.OnSpeedChanged': _event_handler_player_general,
        # Use OnAVChange if available. It is also fired when OnSeek fires, so
        # only handle one event, not both
        'Player.OnAVChange': _event_handler_player_general,
        'Player.OnSeek': (
            _event_handler_player_general
            if not utils.supports_python_api(18)
            else None
        ),
        # Use OnAVStart if available as OnPlay can fire too early for UpNext
        'Player.OnAVStart': _event_handler_av_start,
        'Player.OnPlay': (
            _event_handler_av_start
            if not utils.supports_python_api(18)
            else _event_handler_player_start if SETTINGS.early_queue_reset
            else None
        ),
        'Player.OnStop': _event_handler_player_stop
    }

    # pylint: disable=invalid-name
    def onNotification(self, sender, method, data=None):
        """Handler for Kodi events and data transfer from plugins"""

        if SETTINGS.disabled:
            return

        sender = statichelper.from_bytes(sender)
        method = statichelper.from_bytes(method)
        data = statichelper.from_bytes(data) if data else ''
        self.log(' - '.join([sender, method, data]))

        handler = UpNextMonitor.EVENTS_MAP.get(method)
        if not handler:
            return

        # Player events can fire in quick succession, increment queue length to
        # allow event handlers to skip through the queue
        self._queue_length += 1
        # Call event handler and reduce queue length
        handler(self, sender=sender, data=data)
        if self._queue_length:
            self._queue_length -= 1

    def onSettingsChanged(self):  # pylint: disable=invalid-name
        SETTINGS.update()
        if SETTINGS.disabled and self._started:
            self.log('UpNext disabled', utils.LOGINFO)
            self.stop()
        elif self._started:
            self._widget_reload()
        else:
            self.log('UpNext enabled', utils.LOGINFO)
            self.start()
