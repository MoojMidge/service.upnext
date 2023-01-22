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

    dbid = dummydata.LIBRARY['episodes'][0]['episodeid']
    test_complete = plugin.run([
        'plugin://service.upnext/play_media',
        '1',
        '?db_type=episode&db_id={0}'.format(dbid)
    ])
    assert test_complete is True


def test_movie_plugin():
    if SKIP_TEST_ALL or SKIP_TEST_PLUGIN:
        assert True
        return

    addon_id = 'video.test_movie_plugin'

    dbid = dummydata.LIBRARY['movies'][0]['movieid']
    dbtype = 'movie'
    current_video = api.get_from_library(media_type=dbtype, db_id=dbid)
    current_item = utils.create_item_details(current_video, 'library', dbtype)

    next_item = utils.create_item_details(
        api.get_next_from_library(item=current_item),
        source='library',
        media_type=dbtype
    )

    upnext_info = {
        'current_video': upnext.create_listitem(current_item),
        'play_url': 'plugin://{0}/play_media/?db_type={1}&db_id={2}'.format(
            1, dbtype, next_item['db_id']
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
