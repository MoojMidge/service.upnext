# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals
import threading
import xbmc
import api
import playbackmanager
import player
import state
import statichelper
import utils


PLAYER_MONITOR_EVENTS = [
    'Player.OnPause',
    'Player.OnResume',
    'Player.OnSpeedChanged',
    # 'Player.OnSeek',
    'Player.OnAVChange'
]


class UpNextMonitor(xbmc.Monitor):
    """Service and player monitor/tracker for Kodi"""
    # Set True to enable threading.Thread method for triggering a popup
    # Will continuously poll playtime in a threading.Thread to track popup time
    # Default True
    use_thread = True
    # Set True to enable threading.Timer method for triggering a popup
    # Will schedule a threading.Timer to start tracking when popup is required
    # Default False
    use_timer = False
    # Set True to force a playback event on addon start. Used for testing.
    # Set False for normal addon start
    # Default False
    test_trigger = False

    def __init__(self):
        self.state = state.UpNextState()
        self.player = player.UpNextPlayer()
        self.playbackmanager = None
        self.tracker = None
        self.running = False
        self.sigstop = False
        self.sigterm = False

        xbmc.Monitor.__init__(self)
        self.log('Init', 2)

    @classmethod
    def log(cls, msg, level=2):
        utils.log(msg, name=cls.__name__, level=level)

    def run(self):
        # Re-trigger player event if addon started mid playback
        if self.test_trigger and self.player.isPlaying():
            if utils.get_kodi_version() < 18:
                method = 'Player.OnPlay'
            else:
                method = 'Player.OnAVStart'
            self.onNotification('UpNext', method)

        # Wait indefinitely until addon is terminated
        self.waitForAbort()

        # Cleanup when abort requested
        if self.playbackmanager:
            self.playbackmanager.remove_popup(terminate=True)
            self.log('Cleanup popup', 2)
        self.stop_tracking(terminate=True)
        del self.tracker
        self.tracker = None
        self.log('Cleanup tracker', 2)
        del self.state
        self.state = None
        self.log('Cleanup state', 2)
        del self.player
        self.player = None
        self.log('Cleanup player', 2)
        del self.playbackmanager
        self.playbackmanager = None
        self.log('Cleanup playbackmanager', 2)

    def start_tracking(self):
        if not self.state.is_tracking():
            return
        self.stop_tracking()

        # threading.Timer method not used by default. More testing required
        if self.use_timer:
            with self.player as check_fail:
                play_time = self.player.getTime()
                speed = self.player.get_speed()
                check_fail = False
            if check_fail or speed < 1:
                return

            # Determine play time left until popup is required
            popup_time = self.state.get_popup_time()
            delay = popup_time - play_time
            # Scale play time to real time minus a 10s offset
            delay = max(0, int(delay / speed) - 10)
            msg = 'Tracker - starting at {0}s in {1}s'
            self.log(msg.format(popup_time, delay), 2)

            # Schedule tracker to start when required
            self.tracker = threading.Timer(delay, self.track_playback)
            self.tracker.start()

        # Use while not abortRequested() loop in a separate thread to allow for
        # continued monitoring in main thread
        elif self.use_thread:
            self.tracker = threading.Thread(target=self.track_playback)
            # Daemon threads may not work in Kodi, but enable it anyway
            self.tracker.daemon = True
            self.tracker.start()

        else:
            if self.running:
                self.sigstop = False
            else:
                self.track_playback()

    def stop_tracking(self, terminate=False):
        # Set terminate or stop signals if tracker is running
        if terminate:
            self.sigterm = self.running
            if self.playbackmanager:
                self.playbackmanager.remove_popup(terminate=True)
        else:
            self.sigstop = self.running

        if not self.tracker:
            return

        # Wait for thread to complete
        if self.running:
            self.tracker.join()
        # Or if tracker has not yet started on timer then cancel old timer
        elif self.use_timer:
            self.tracker.cancel()

        # Free resources
        del self.tracker
        self.tracker = None

    def track_playback(self):
        # Only track playback if old tracker is not running
        if self.running:
            return
        self.log('Tracker started', 2)
        self.running = True

        # Loop unless abort requested
        while not self.abortRequested() and not self.sigterm:
            # Exit loop if stop requested or if tracking stopped
            if self.sigstop or not self.state.is_tracking():
                self.log('Tracker - exit', 2)
                break

            tracked_file = self.state.get_tracked_file()
            with self.player as check_fail:
                current_file = self.player.getPlayingFile()
                total_time = self.player.getTotalTime()
                play_time = self.player.getTime()
                check_fail = False
            if check_fail:
                self.log('No file is playing', 2)
                self.state.set_tracking(False)
                continue
            # New stream started without tracking being updated
            if tracked_file and tracked_file != current_file:
                self.log('Error - unknown file playing', 1)
                self.state.set_tracking(False)
                continue

            popup_time = self.state.get_popup_time()
            # Media hasn't reach popup time yet, waiting a bit longer
            if play_time < popup_time:
                self.waitForAbort(min(1, popup_time - play_time))
                continue

            # Stop second thread and popup from being created after next file
            # has been requested but not yet loaded
            self.state.set_tracking(False)
            self.sigstop = True

            # Start Up Next to handle playback of next file
            msg = 'Popup - due at {0}s - file ({1}s runtime) ends in {2}s'
            msg = msg.format(popup_time, total_time, total_time - play_time)
            self.log(msg, 2)
            self.playbackmanager = playbackmanager.PlaybackManager(
                player=self.player,
                state=self.state
            )
            self.playbackmanager.launch_up_next()
            break
        else:
            self.log('Tracker - abort', 1)

        # Reset thread signals
        self.log('Tracker - stopped', 2)
        self.running = False
        self.sigstop = False
        self.sigterm = False

    def check_video(self, data=None, encoding=None):
        # Only process one start at a time unless addon data has been received
        if self.state.starting and not data:
            return
        self.log('Starting video check', 2)
        # Increment starting counter
        self.state.starting += 1
        start_num = max(1, self.state.starting)

        # onPlayBackEnded for current file can trigger after next file starts
        # Wait additional 5s after onPlayBackEnded or last start
        wait_count = 5 * start_num
        while not self.abortRequested() and wait_count:
            self.waitForAbort(1)
            wait_count -= 1

        # Exit if no file playing
        with self.player as check_fail:
            playing_file = self.player.getPlayingFile()
            total_time = self.player.getTotalTime()
            check_fail = False
        if check_fail:
            self.log('Skip video check - stream not playing', 2)
            return
        self.log('Playing - %s' % playing_file, 2)

        # Exit if starting counter has been reset or new start detected or
        # starting state has been reset by playback error/end/stop
        if not self.state.starting or start_num != self.state.starting:
            self.log('Skip video check - stream not fully loaded', 2)
            return
        self.state.starting = 0
        self.state.playing = 1

        if utils.get_property('PseudoTVRunning') == 'True':
            self.log('Skip video check - PsuedoTV detected', 2)
            return

        if self.player.isExternalPlayer():
            self.log('Skip video check - external player detected', 2)
            return

        # Check what type of video is being played
        is_playlist_item = api.get_playlist_position()
        # Use new addon data if provided or erase old addon data.
        # Note this may cause played in a row count to reset incorrectly if
        # playlist of mixed non-addon and addon content is used
        has_addon_data = self.state.set_addon_data(data, encoding)
        is_episode = xbmc.getCondVisibility('videoplayer.content(episodes)')

        # Exit if Up Next playlist handling has not been enabled
        if is_playlist_item and not self.state.enable_playlist:
            self.log('Skip video check - playlist handling not enabled', 2)
            return

        # Start tracking if Up Next can handle the currently playing video
        if is_playlist_item or has_addon_data or is_episode:
            self.state.set_tracking(playing_file)
            self.state.reset_queue()

            # Get details of currently playing video to save playcount
            if has_addon_data:
                self.state.handle_addon_now_playing()
            else:
                self.state.handle_library_now_playing()

            # Store popup time and check if cue point was provided
            self.state.set_popup_time(total_time)

            # Start tracking playback in order to launch popup at required time
            self.start_tracking()

        else:
            self.log('Skip video check - Up Next unable to handle video', 2)
            if self.state.is_tracking():
                self.state.reset()

    def onSettingsChanged(self):  # pylint: disable=invalid-name
        self.log('Settings changed', 2)
        self.state.update_settings()

        # Shutdown tracking loop if disabled
        if self.state.is_disabled():
            self.log('Up Next disabled', 0)
            if self.playbackmanager:
                self.playbackmanager.remove_popup(terminate=True)
            self.stop_tracking(terminate=True)

    def onScreensaverDeactivated(self):  # pylint: disable=invalid-name
        # Restart tracking if previously tracking
        self.start_tracking()


    def onNotification(self, sender, method, data=None):  # pylint: disable=invalid-name
        """Handler for Kodi events and data transfer from addons"""
        if self.state.is_disabled():
            return

        sender = statichelper.to_unicode(sender)
        method = statichelper.to_unicode(method)
        data = statichelper.to_unicode(data) if data else ''

        if (utils.get_kodi_version() < 18 and method == 'Player.OnPlay'
                or method == 'Player.OnAVStart'):
            # Update player state and remove any existing popups
            self.player.state.set('time', force=False)
            if self.playbackmanager:
                self.playbackmanager.remove_popup()

            # Increase playcount and reset resume point of previous file
            if self.state.playing_next:
                self.state.playing_next = False
                # TODO: Add settings to control whether file is marked as
                # watched and resume point is reset when next file is played
                api.handle_just_watched(
                    episodeid=self.state.episodeid,
                    playcount=self.state.playcount,
                    reset_resume=True
                )

            # Check whether Up Next can start tracking
            self.check_video()

        elif method == 'Player.OnStop':
            if self.playbackmanager:
                self.playbackmanager.remove_popup()
            self.stop_tracking()
            self.state.reset_queue()
            # OnStop can occur before/after the next file has started playing
            # Reset state if Up Next has not requested the next file to play
            if not self.state.playing_next:
                self.state.reset()

        elif method in PLAYER_MONITOR_EVENTS:
            # Restart tracking if previously tracking
            self.start_tracking()

        # Data transfer from addons
        elif method.endswith('upnext_data'):
            decoded_data, encoding = utils.decode_json(data)
            sender = sender.replace('.SIGNAL', '')
            if not isinstance(decoded_data, dict) or not decoded_data:
                msg = 'Addon data error - {0} sent {1} as {2}'
                self.log(msg.format(sender, decoded_data, data), 1)
                return
            decoded_data.update(id='%s_play_action' % sender)

            # Initial processing of data to start tracking
            self.check_video(decoded_data, encoding)
