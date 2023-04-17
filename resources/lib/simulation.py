# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""Implements UpNext simulation mode functions used for runtime testing UpNext"""

from __future__ import absolute_import, division, unicode_literals

import constants
import plugin
import upnext
import utils
from settings import SETTINGS

_EVENT_TRIGGERED = {
    'playback': False,
    'general': False,
}


def log(msg, level=utils.LOGDEBUG):
    utils.log(msg, name=__name__, level=level)


def handle_sim_mode(player, state, now_playing_item):
    _EVENT_TRIGGERED['general'] = False
    if not SETTINGS.sim_mode or _EVENT_TRIGGERED['playback']:
        _EVENT_TRIGGERED['playback'] = False
        return _EVENT_TRIGGERED['general']

    utils.notification('UpNext sim mode', 'Active')
    log('Active')

    # Force use of plugin data method if sim plugin mode is enabled
    if state.get_plugin_type() is None and SETTINGS.sim_plugin:
        addon_id = utils.get_addon_id()
        upnext_info = plugin.generate_library_plugin_data(
            now_playing_item, addon_id, state
        )
        if upnext_info:
            log('Plugin data sent')
            _EVENT_TRIGGERED['playback'] = True
            _EVENT_TRIGGERED['general'] = True
            upnext.send_signal(addon_id, upnext_info)

    if not SETTINGS.sim_seek:
        return _EVENT_TRIGGERED['general']

    with utils.ContextManager(handler=player) as (_, error):
        if error is AttributeError:
            raise error
        # Seek to 15s before end of video
        if SETTINGS.sim_seek == constants.SIM_SEEK_15S:
            seek_time = player.getTotalTime() - 15
        # Seek to popup start time
        elif SETTINGS.sim_seek == constants.SIM_SEEK_POPUP_TIME:
            seek_time = state.get_popup_time()
        # Seek to detector start time
        else:
            seek_time = state.get_detect_time() or state.get_popup_time()
        log('Seeking to end')
        player.seekTime(seek_time)

        # Seek workaround required for AML HW decoder on certain videos
        # to avoid buffer desync and playback hangs
        utils.wait(3)
        if player.getTime() <= seek_time:
            log('Seek workaround')
            player.seekTime(seek_time + 3)

        error = False
    if error:
        log('Nothing playing', utils.LOGWARNING)

    _EVENT_TRIGGERED['general'] = True
    return _EVENT_TRIGGERED['general']
