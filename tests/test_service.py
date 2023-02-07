# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""UpNext script and service tests"""

from __future__ import absolute_import, division, unicode_literals

import api
import dummydata
import plugin
import script
import upnext
import utils

SKIP_TEST_ALL = False
SKIP_TEST_POPUP = False
SKIP_TEST_PLUGIN = False
SKIP_TEST_WIDGET = False
SKIP_TEST_OVERALL = False


def test_popup():
    if SKIP_TEST_ALL or SKIP_TEST_POPUP:
        assert True
        return

    test_complete = script.run(['', 'test_window', 'upnext'])
    assert test_complete is True


def test_plugin():
    if SKIP_TEST_ALL or SKIP_TEST_PLUGIN:
        assert True
        return

    db_id = dummydata.LIBRARY['episodes'][0]['episodeid']
    test_complete = plugin.run([
        'plugin://service.upnext/play_media',
        '1',
        '?type=episode&id={0}'.format(db_id)
    ])
    assert test_complete is True


def test_movie_plugin():
    if SKIP_TEST_ALL or SKIP_TEST_PLUGIN:
        assert True
        return

    addon_id = 'video.test_movie_plugin'

    db_id = dummydata.LIBRARY['movies'][0]['movieid']
    current_video = api.get_from_library(db_type='movie', db_id=db_id)
    current_item = utils.create_item_details(current_video, 'library')
    next_item = utils.create_item_details(
        api.get_next_from_library(item=current_item), 'library',
    )

    upnext_info = {
        'current_video': upnext.create_listitem(current_item),
        'play_url': 'plugin://{0}/play_media/?type={1}&id={2}'.format(
            1, next_item['type'], next_item['id']
        )
    }
    test_complete = upnext.send_signal(addon_id, upnext_info)
    test_complete = test_complete and test_complete.get('result')

    assert test_complete == 'OK'


def test_widget():
    if SKIP_TEST_ALL or SKIP_TEST_WIDGET:
        assert True
        return

    test_complete = (
        plugin.run(['plugin://service.upnext/', '1', ''])
        and plugin.run(['plugin://service.upnext/next_episodes', '1', ''])
        and plugin.run(['plugin://service.upnext/next_movies', '1', ''])
        and plugin.run(['plugin://service.upnext/next_media', '1', ''])
        and plugin.run(['plugin://service.upnext/similar_movies', '1', ''])
        and plugin.run(['plugin://service.upnext/similar_tvshows', '1', ''])
        and plugin.run(['plugin://service.upnext/similar_media', '1', ''])
        and plugin.run(['plugin://service.upnext/watched_movies', '1', ''])
        and plugin.run(['plugin://service.upnext/watched_tvshows', '1', ''])
        and plugin.run(['plugin://service.upnext/watched_media', '1', ''])
    )
    assert test_complete is True


def test_overall():
    if SKIP_TEST_ALL or SKIP_TEST_OVERALL:
        assert True
        return

    test_run = script.run(['', 'test_upnext', 'upnext'])
    test_complete = test_run.waitForAbort()
    assert test_complete is True
