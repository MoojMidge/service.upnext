# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals
import api
import dialog
import utils


class UpNextPopupHandler(object):  # pylint: disable=useless-object-inheritance
    """Controller for UpNext popup and playback of next item"""

    __slots__ = (
        'monitor',
        'player',
        'state',
        'popup',
        'running',
        'sigstop',
        'sigterm'
    )

    def __init__(self, monitor, player, state):
        self.log('Init')

        self.monitor = monitor
        self.player = player
        self.state = state
        self.popup = None
        self.running = False
        self.sigstop = False
        self.sigterm = False

    @classmethod
    def log(cls, msg, level=utils.LOGDEBUG):
        utils.log(msg, name=cls.__name__, level=level)

    def _create_popup(self, next_item, source=None):
        # Only use Still Watching? popup if played limit has been reached
        if self.state.played_limit:
            show_upnext = self.state.played_limit > self.state.played_in_a_row
        # Don't show Still Watching? popup if played limit is zero, unless
        # played in a row count has been set to zero for testing
        else:
            show_upnext = self.state.played_limit != self.state.played_in_a_row

        self.log('Auto played in a row: {0} of {1}'.format(
            self.state.played_in_a_row, self.state.played_limit
        ), utils.LOGINFO)

        # Filename for dialog XML
        filename = 'script-upnext{0}{1}{2}.xml'.format(
            '-upnext' if show_upnext else '-stillwatching',
            '-simple' if self.state.simple_mode else '',
            '' if self.state.skin_popup else '-original'
        )

        self.popup = dialog.UpNextPopup(
            filename,
            utils.get_addon_path(),
            'default',
            '1080i',
            item=next_item,
            shuffle=self.state.shuffle if source == 'library' else None,
            stop_button=self.state.show_stop_button
        )

        return self._get_popup_state(done=True, show_upnext=show_upnext)

    def _display_popup(self, popup_state):
        # Get video details, exit if no video playing
        with self.player as check_fail:
            total_time = self.player.getTotalTime()
            play_time = self.player.getTime()
            check_fail = False
        if check_fail:
            return self._get_popup_state(popup_state, done=False)

        # If cue point was provided then UpNext will auto play after a fixed
        # delay time, rather than waiting for the end of the file
        if popup_state['play_on_cue']:
            popup_duration = self.state.auto_play_delay
            if popup_duration:
                popup_start = max(play_time, self.state.get_popup_time())
                total_time = min(popup_start + popup_duration, total_time)

        if not self._show_popup():
            return self._get_popup_state(popup_state, done=False)

        # Current file can stop, or next file can start, while update loop is
        # running. Check state and abort popup update if required
        while (not self.monitor.abortRequested()
               and self.player.isPlaying()
               and popup_state['done']
               and not self.state.starting
               and self.state.playing
               and not self.sigstop
               and not self.sigterm):
            remaining = total_time - self.player.getTime()
            popup_state = self._get_popup_state(
                popup_state,
                done=self._has_popup(),
                remaining=remaining
            )

            # Decrease wait time and increase loop speed to try and avoid
            # missing the end of video when fast forwarding
            wait_time = 1 / max(1, self.player.get_speed())
            self.monitor.waitForAbort(max(0.1, min(wait_time, remaining)))

            # If end of file or user has closed popup then exit update loop
            remaining -= wait_time
            if (remaining <= 0
                    or popup_state['cancel']
                    or popup_state['play_now']):
                popup_done = True
                break
        else:
            popup_done = False

        return self._get_popup_state(popup_state, done=popup_done)

    def _get_popup_state(self, old_state=None, **kwargs):
        default_state = old_state if old_state else {
            'auto_play': self.state.auto_play,
            'cancel': False,
            'done': False,
            'play_now': False,
            'play_on_cue': self.state.auto_play and self.state.popup_cue,
            'show_upnext': False,
            'shuffle': False,
            'shuffle_start': False,
            'stop': False
        }

        for keyword in kwargs:
            if keyword in default_state:
                default_state[keyword] = kwargs[keyword]

        if not self._has_popup():
            return default_state

        with self.popup as check_fail:
            remaining = kwargs.get('remaining')
            if remaining is not None:
                self.popup.update_progress(remaining)

            current_state = {
                'auto_play': (
                    self.state.auto_play
                    and default_state['show_upnext']
                    and not self.popup.is_cancel()
                    and not self.popup.is_playnow()
                ),
                'cancel': self.popup.is_cancel(),
                'done': default_state['done'],
                'play_now': self.popup.is_playnow(),
                'play_on_cue': (
                    self.state.auto_play
                    and default_state['show_upnext']
                    and not self.popup.is_cancel()
                    and not self.popup.is_playnow()
                    and self.state.popup_cue
                ),
                'show_upnext': default_state['show_upnext'],
                'shuffle': self.popup.is_shuffle(),
                'shuffle_start': (
                    not self.state.shuffle
                    and self.popup.is_shuffle()
                ),
                'stop': self.popup.is_stop()
            }
            check_fail = False
        if check_fail:
            return default_state
        return current_state

    def _has_popup(self):
        return hasattr(self, 'popup') and self.popup

    def _play_next_video(self, next_item, source, popup_state):
        # Primary method is to play next playlist item
        if source[-len('playlist'):] == 'playlist' or self.state.queued:
            # Can't just seek to end of file as this triggers inconsistent Kodi
            # behaviour:
            # - Will sometimes continue playing past the end of the file
            #   preventing next file from playing
            # - Will sometimes play the next file correctly then play it again
            #   resulting in loss of UpNext state
            # - Will sometimes play the next file immediately without
            #   onPlayBackStarted firing resulting in tracking not activating
            # - Will sometimes work just fine
            # Can't just wait for next file to play as VideoPlayer closes all
            # video threads when the current file finishes
            if popup_state['play_now'] or popup_state['play_on_cue']:
                api.play_playlist_item(
                    # Use previously stored next playlist position if available
                    position=next_item.get('playlist_position', 'next'),
                    resume=self.state.enable_resume
                )

        # Fallback addon playback method, used if addon provides play_info
        elif source[:len('addon')] == 'addon':
            api.play_addon_item(
                self.state.data,
                self.state.encoding,
                self.state.enable_resume
            )

        # Fallback library playback method, not normally used
        else:
            api.play_kodi_item(next_item, self.state.enable_resume)

        # Determine playback method. Used for logging purposes
        self.log('Playback requested: {0}, from {1}{2}'.format(
            popup_state, source, ' using queue' if self.state.queued else ''
        ))

    def _post_run(self, play_next, keep_playing):
        # Update playback state
        self.state.playing_next = play_next

        # Dequeue and stop playback if not playing next file
        if not play_next and self.state.queued:
            self.state.queued = api.dequeue_next_item()
        if not keep_playing:
            self.log('Stopping playback', utils.LOGINFO)
            self.player.stop()

        # Reset signals
        self.sigstop = False
        self.sigterm = False
        self.running = False

    def _remove_popup(self):
        if not self._has_popup():
            return

        with self.popup:
            self.popup.close()
            utils.clear_property('service.upnext.dialog')

        del self.popup
        self.popup = None

    def _run(self):
        self.log('Started')
        self.running = True

        next_item, source = self.state.get_next()
        # No next item to play, get out of here
        if not next_item:
            self.log('Exiting: no next item to play')

            play_next = False
            keep_playing = True
            self._post_run(play_next, keep_playing)
            has_next_item = False
            return has_next_item

        # Add next file to playlist if existing playlist is not being used
        if self.state.enable_queue and source[-len('playlist'):] != 'playlist':
            self.state.queued = api.queue_next_item(self.state.data, next_item)

        # Create Kodi dialog to show UpNext or Still Watching? popup
        popup_state = self._create_popup(next_item, source)
        # Display popup and update state of controls
        popup_state = self._display_popup(popup_state)
        # Close dialog once we are done with it
        self._remove_popup()

        # Update played in a row count if auto_play otherwise reset
        self.state.played_in_a_row = (
            self.state.played_in_a_row + 1 if popup_state['auto_play'] else 1
        )

        # Update shuffle state
        self.state.shuffle = popup_state['shuffle']

        # Signal to Trakt that current item has been watched
        utils.event(
            message='NEXTUPWATCHEDSIGNAL',
            data={'episodeid': self.state.get_episodeid()},
            encoding='base64'
        )

        # Popup closed prematurely
        if not popup_state['done']:
            self.log('Exiting: popup force closed', utils.LOGWARNING)
            has_next_item = False

        # Shuffle start request
        elif popup_state['shuffle_start']:
            self.log('Exiting: shuffle requested')
            has_next_item = False
            popup_state['done'] = False

        elif not (popup_state['auto_play'] or popup_state['play_now']):
            self.log('Exiting: playback not selected')
            has_next_item = True
            popup_state['done'] = False

        if not popup_state['done']:
            play_next = False
            # Stop playing if Stop button was clicked on popup, or if Still
            # Watching? popup was shown (to prevent unwanted playback that can
            # occur if fast forwarding through popup), or not starting shuffle
            keep_playing = (
                not popup_state['stop']
                and (
                    popup_state['show_upnext']
                    or popup_state['shuffle_start']
                )
            )
            self._post_run(play_next, keep_playing)

            # Run again if shuffle started to get new random episode
            if popup_state['shuffle_start']:
                return self._run()

            return has_next_item

        # Request playback of next file based on source and type
        self._play_next_video(next_item, source, popup_state)

        play_next = True
        keep_playing = True
        self._post_run(play_next, keep_playing)
        has_next_item = True
        return has_next_item

    def _show_popup(self):
        if not self._has_popup():
            return False

        with self.popup:
            self.popup.show()
            utils.set_property('service.upnext.dialog', 'true')
            return True

    def cancel(self):
        self.stop()

    def start(self, called=[False]):  # pylint: disable=dangerous-default-value
        # Exit if popuphandler previously requested
        if called[0]:
            has_next_item = False
            return has_next_item
        # Stop any existing popuphandler
        self.stop()
        called[0] = True

        # Show popup and get new playback state
        has_next_item = self._run()

        called[0] = False
        return has_next_item

    def stop(self, terminate=False):
        if terminate:
            self.sigterm = self.running
        else:
            self.sigstop = self.running

        # popuphandler does not run in a separate thread, but stop() can be
        # called from another thread
        while self.running:
            # Wait until execution has finished to ensure references/resources
            # can be safely released
            pass

        # Free references/resources
        if terminate:
            self._remove_popup()
            del self.monitor
            self.monitor = None
            del self.player
            self.player = None
            del self.state
            self.state = None
