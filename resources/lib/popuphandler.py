# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals

import api
import dialog
import utils
from settings import SETTINGS


class UpNextPopupHandler(object):
    """Controller for UpNext popup and playback of next item"""

    __slots__ = (
        'player',
        'state',
        'popup',
        '_running',
        '_sigcont',
        '_sigstop',
        '_sigterm',
    )

    def __init__(self, player, state):
        self.log('Init')

        self.player = player
        self.state = state
        self.popup = None
        self._running = utils.create_event()
        self._sigcont = utils.create_event()
        self._sigstop = utils.create_event()
        self._sigterm = utils.create_event()

    @classmethod
    def log(cls, msg, level=utils.LOGDEBUG):
        utils.log(msg, name=cls.__name__, level=level)

    def _create_popup(self, next_item):
        # Only use Still Watching? popup if played limit has been reached
        if SETTINGS.played_limit:
            show_upnext = SETTINGS.played_limit > self.state.played_in_a_row
        # Don't show Still Watching? popup if played limit is zero, unless
        # played in a row count has been set to zero for testing
        else:
            show_upnext = SETTINGS.played_limit != self.state.played_in_a_row

        self.log('Auto played in a row: {0} of {1}'.format(
            self.state.played_in_a_row, SETTINGS.played_limit
        ), utils.LOGINFO)

        # Filename for dialog XML
        filename = 'script-upnext{0}{1}{2}.xml'.format(
            '-upnext' if show_upnext else '-stillwatching',
            '-simple' if SETTINGS.simple_mode else '',
            '' if SETTINGS.skin_popup else '-original'
        )

        self.popup = dialog.UpNextPopup(
            filename,
            utils.get_addon_path(),
            'default',
            '1080i',
            item=next_item,
            shuffle_on=(
                self.state.shuffle_on if next_item['source'] == 'library'
                else None
            ),
            stop_button=SETTINGS.show_stop_button,
            popup_position=SETTINGS.popup_position,
            accent_colour=SETTINGS.popup_accent_colour
        )

        return self._popup_state(abort=False, show_upnext=show_upnext)

    def _popup_state(self, old_state=None, **kwargs):
        old_state = old_state or {
            'auto_play': SETTINGS.auto_play,
            'cancel': False,
            'abort': False,
            'play_now': False,
            'play_on_cue': SETTINGS.auto_play and self.state.popup_cue,
            'show_upnext': False,
            'shuffle_on': False,
            'shuffle_start': False,
            'stop': False
        }

        for kwarg, value in kwargs.items():
            if kwarg in old_state:
                old_state[kwarg] = value

        with utils.ContextManager(self, 'popup') as (popup, error):
            if error is AttributeError:
                raise error
            remaining = kwargs.get('remaining')
            if remaining is not None:
                popup.update_progress(remaining)

            cancel = popup.is_cancel()
            play_now = popup.is_playnow()
            shuffle_on = popup.is_shuffle_on()
            stop = popup.is_stop()

            error = False
        if error or old_state['abort']:
            old_state['abort'] = True
            return old_state

        current_state = {
            'auto_play': (
                SETTINGS.auto_play
                and old_state['show_upnext']
                and not cancel
                and not play_now
            ),
            'cancel': cancel,
            'abort': old_state['abort'],
            'play_now': play_now,
            'play_on_cue': (
                SETTINGS.auto_play
                and old_state['show_upnext']
                and not cancel
                and not play_now
                and self.state.popup_cue
            ),
            'show_upnext': old_state['show_upnext'],
            'shuffle_on': shuffle_on,
            'shuffle_start': (
                not self.state.shuffle_on
                and shuffle_on
            ),
            'stop': stop
        }
        return current_state

    def _play_next_video(self, next_item, popup_state):
        forced = self.player.player_state.forced('playing')
        source = next_item['source']
        if SETTINGS.enable_resume:
            resume = next_item['details'].get('resume')
            if resume and resume['total'] and resume['position']:
                resume = 100 * resume['position'] / resume['total']
            else:
                resume = False
        else:
            resume = False

        keep_playing = not SETTINGS.pause_until_next
        # Primary method is to play next playlist item
        if source.endswith('playlist') or self.state.queued:
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
            if popup_state['play_now'] or popup_state['play_on_cue'] or forced:
                api.play_playlist_item('next', resume)
            else:
                keep_playing = True

        # Fallback plugin playback method, or if plugin provides play_info
        elif source.startswith('plugin'):
            api.play_plugin_item(self.state.data, self.state.encoding, resume)

        # Fallback library playback method, not normally used
        else:
            api.play_kodi_item(next_item, resume)

        # Determine playback method. Used for logging purposes
        self.log('Playback requested: {0}, from {1}{2}'.format(
            popup_state, source, ' using queue' if self.state.queued else ''
        ))
        return keep_playing

    def _remove_popup(self):
        with utils.ContextManager(self, 'popup') as (popup, error):
            if error is AttributeError:
                raise error
            popup.close()
            utils.clear_property('service.upnext.dialog')
            del self.popup
            self.popup = None

    def _run(self, item=None):
        next_item = item if item else self.state.get_next()
        # No next item to play, get out of here
        if not next_item:
            self.log('Exiting: no next item to play')
            play_next = False
            keep_playing = True
            restart = False
            return next_item, play_next, keep_playing, restart

        # Add next file to playlist if existing playlist is not being used
        if (SETTINGS.enable_queue
                and not next_item['source'].endswith(('playlist', 'direct'))):
            self.state.queued = api.queue_next_item(self.state.data, next_item)

        # Create Kodi dialog to show UpNext or Still Watching? popup
        popup_state = self._create_popup(next_item)
        # Show popup and update state of controls
        popup_state = self._update_popup(popup_state)
        # Close dialog once we are done with it
        self._remove_popup()

        # Update shuffle state
        self.state.shuffle_on = popup_state['shuffle_on']

        # Signal to Trakt that current item has been watched
        utils.event(message='NEXTUPWATCHEDSIGNAL',
                    data=api.get_item_id(self.state.current_item),
                    encoding='base64')

        play_next = False
        # Stop playing if Stop button was clicked on popup, or if Still
        # Watching? popup was shown (to prevent unwanted playback that can
        # occur if fast forwarding through popup or if race condition occurs
        # between player starting and popup terminating)
        keep_playing = not popup_state['stop'] and (
            popup_state['show_upnext'] or self._sigcont.is_set()
        )
        restart = self._sigcont.is_set()

        # Popup closed prematurely
        if popup_state['abort']:
            self.log('Exiting: popup force closed', utils.LOGWARNING)
            next_item = None if not restart else next_item

        # Shuffle start request
        elif popup_state['shuffle_start']:
            self.log('Exiting: shuffle requested')
            next_item = None
            keep_playing = True
            restart = True

        elif not (popup_state['auto_play'] or popup_state['play_now']):
            self.log('Exiting: playback not selected')
            next_item = None

        else:
            play_next = True
            # Request playback of next file based on source and type
            keep_playing = self._play_next_video(next_item, popup_state)
            # Update played in a row count if auto_play otherwise reset
            self.state.played_in_a_row = (1 if popup_state['play_now']
                                          else self.state.played_in_a_row + 1)

        return next_item, play_next, keep_playing, restart

    def _show_popup(self):
        with utils.ContextManager(self, 'popup') as (popup, error):
            if error is AttributeError:
                raise error
            popup.show()
            utils.set_property('service.upnext.dialog', 'true')
            return True
        return False

    def _update_popup(self, popup_state):
        # Get video details, exit if no video playing or no popup available
        with utils.ContextManager(self, 'player') as (player, error):
            if error is AttributeError:
                raise error
            total_time = player.getTotalTime()
            play_time = player.getTime()
            speed = player.get_speed()
            error = False
        if error or not self._show_popup():
            return self._popup_state(old_state=popup_state, abort=True)

        # If cue point was provided then UpNext will auto play after a fixed
        # delay time, rather than waiting for the end of the file
        if popup_state['play_on_cue']:
            popup_duration = SETTINGS.auto_play_delay
            if popup_duration:
                popup_start = max(play_time, self.state.get_popup_time())
                total_time = min(popup_start + popup_duration, total_time)

        # Current file can stop, or next file can start, while update loop is
        # running. Check state and abort popup update if required
        popup_abort = False
        remaining = 0
        state = self.state
        while not (popup_abort
                   or error
                   or popup_state['abort']
                   or state.starting
                   or (self._sigstop.is_set() and remaining > 1)
                   or self._sigterm.is_set()):
            # Update popup time remaining
            remaining = total_time - play_time
            popup_state = self._popup_state(
                old_state=popup_state, remaining=remaining
            )

            # Decrease wait time and increase loop speed to try and avoid
            # missing the end of video when fast forwarding
            wait_time = 1 / max(1, speed)
            popup_abort = utils.wait(min(wait_time, remaining))

            # If end of file or user has closed popup then exit update loop
            remaining -= wait_time
            if (popup_abort
                    or remaining <= 0
                    or popup_state['cancel']
                    or popup_state['play_now']):
                break

            with utils.ContextManager(self, 'player') as (player, error):
                if error is AttributeError:
                    raise error
                if state.get_tracked_file() != player.getPlayingFile():
                    break
                play_time = player.getTime()
                speed = player.get_speed()
                error = False
        else:
            popup_abort = True

        return self._popup_state(old_state=popup_state, abort=popup_abort)

    def cancel(self):
        self.stop()

    def start(self):
        # Exit if popuphandler previously requested
        if self._running.is_set():
            return False

        self.log('Started')
        self._running.set()

        next_item = None
        player = self.player
        state = self.state
        while True:
            # Show popup and get new playback state
            next_item, play_next, keep_playing, restart = self._run(next_item)

            # Update playback state
            state.playing_next = play_next
            state.keep_playing = keep_playing

            if not keep_playing:
                # Pause playback until next file starts
                if play_next:
                    self.log('Pause playback', utils.LOGINFO)
                    player.pause()
                # Stop playback and dequeue if not playing next file
                else:
                    self.log('Stopping playback', utils.LOGINFO)
                    player.stop()
            if not play_next and state.queued:
                state.queued = api.dequeue_next_item()

            # Run again if shuffle started to get new random episode, or
            # restart triggered
            if not restart:
                break
            if self._sigcont.is_set():
                self._sigstop.clear()
                self._sigcont.clear()

        # Reset signals
        self.log('Stopped')
        self._sigcont.clear()
        self._sigstop.clear()
        self._sigterm.clear()
        self._running.clear()

        return bool(next_item)

    def stop(self, restart=False, terminate=False):
        # Set terminate or stop signals if popuphandler is running
        if self._running.is_set():
            if terminate:
                self._sigterm.set()
            else:
                self._sigstop.set()
                if restart:
                    self._sigcont.set()

        # Wait until execution has finished to ensure references/resources can
        # be safely released. Can't use self._running.wait(5) as popuphandler
        # does not run in a separate thread even if stop() can.
        timeout = 5
        wait_time = 0.1
        while self._running.is_set() and not utils.wait(wait_time):
            timeout -= wait_time
            if timeout <= 0:
                break
        if self._running.is_set():
            if getattr(self, 'popup', False):
                self.log('Popup taking too long to close', utils.LOGWARNING)
            else:
                self._sigcont.clear()
                self._sigstop.clear()
                self._sigterm.clear()
                self._running.clear()

        # Free references/resources
        if terminate:
            self._remove_popup()
            del self.player
            self.player = None
            del self.state
            self.state = None
