# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""Implements UpNext demo mode functions used for runtime testing UpNext"""

from __future__ import absolute_import, division, unicode_literals
import xbmc
import plugin
import upnext
import utils


def log(msg, level=utils.LOGINFO):
    utils.log(msg, name=__name__, level=level)


def handle_demo_mode(state, player, now_playing_item):
    if not state.demo_mode:
        return

    utils.notification('UpNext demo mode', 'Active')

    # Force use of addon data method if demo plugin mode is enabled
    if not state.has_addon_data() and state.demo_plugin:
        addon_id = utils.addon_id()
        upnext_info = plugin.generate_data(
            now_playing_item, addon_id, state
        )
        if upnext_info:
            upnext.send_signal(addon_id, upnext_info)

    if not state.demo_seek:
        return
    # Seek to popup start time
    if state.demo_seek == 2:
        seek_time = state.get_popup_time()
    # Seek to detector start time
    elif state.demo_seek == 3:
        seek_time = state.get_detect_time()
    # Otherwise no specific seek point set
    else:
        seek_time = 0

    # Need to wait for some time before seeking as otherwise Kodi playback can
    # become desynced
    xbmc.Monitor().waitForAbort(5)
    with player as check_fail:
        # Seek to 15s before end of video if no seek point set
        if not seek_time:
            seek_time = player.getTotalTime() - 15
        player.seekTime(seek_time)
        check_fail = False
    if check_fail:
        log('Error: demo seek, nothing playing', utils.LOGWARNING)
