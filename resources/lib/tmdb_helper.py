# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import utils
from settings import SETTINGS


def log(msg, level=utils.LOGERROR):
    """Log wrapper"""

    utils.log(msg, name=__name__, level=level)


class Import(object):  # pylint: disable=too-few-public-methods
    def __new__(cls, object_name=None):
        def substitute(cls, func=None, default_return=None):
            def wrapper(*_args, **_kwargs):
                return default_return

            def decorator(func):
                if cls._initialised:
                    return func
                from functools import wraps
                return wraps(func)(wrapper)

            if func:
                return decorator(func)
            return decorator

        def is_initialised(cls):
            return cls._initialised

        try:
            module_name = 'themoviedb_helper'
            module = __import__(module_name, fromlist=[object_name])
            imported_object = getattr(module, object_name)
            initialised = True
        except (AttributeError, ImportError):
            from traceback import format_exc
            log('ImportError: {0}.{1}\n{2}'.format(module_name, object_name,
                                                   format_exc()))
            imported_object = object
            initialised = False

        if isinstance(imported_object, type):
            return type(object_name, (imported_object,), {
                '_initialised': initialised,
                '_substitute': classmethod(substitute),
                'is_initialised': classmethod(is_initialised),
            })
        return imported_object


TMDb = Import('TMDb')  # pylint: disable=invalid-name
Players = Import('Players')  # pylint: disable=invalid-name
get_next_episodes = Import('get_next_episodes')  # pylint: disable=invalid-name


class TMDB(TMDb):  # pylint: disable=inherit-non-class,too-few-public-methods
    @TMDb._substitute(default_return=(None, None))  # pylint: disable=no-member
    def get_details(self, title, season, episode):
        tmdb_id = self.get_tmdb_id(
            tmdb_type='tv', query=title, season=season, episode=episode
        )
        if not tmdb_id:
            return None, None
        details = super(TMDB, self).get_details(
            tmdb_type='tv', tmdb_id=tmdb_id, season=season, episode=episode
        )
        return tmdb_id, details


class Player(Players):  # pylint: disable=inherit-non-class,too-few-public-methods
    @Players._substitute  # pylint: disable=no-member
    def __init__(self, **kwargs):
        if 'tmdb_id' not in kwargs:
            kwargs['tmdb_id'] = TMDb().get_tmdb_id(**kwargs)  # pylint: disable=not-callable
        super(Player, self).__init__(**kwargs)
        self._success = False

    @Players._substitute  # pylint: disable=no-member
    def _get_path_from_actions(self, actions, is_folder=True):
        if SETTINGS.exact_tmdb_match and 'dialog' in actions:
            actions['dialog'] = False
        return super(Player, self)._get_path_from_actions(
            actions, is_folder
        )

    @Players._substitute  # pylint: disable=no-member
    def _get_player_or_fallback(self, *args, **kwargs):
        player = super(Player, self)._get_player_or_fallback(*args, **kwargs)
        if player and SETTINGS.exact_tmdb_match:
            assert_keys = set(
                self.players.get(player.get('file'), {})
                .get('assert', {})
                .get('play_episode', [])
            )
            if {'showname', 'season', 'episode'} - assert_keys:
                return None
        self.current_player = player  # pylint: disable=attribute-defined-outside-init
        return player

    @Players._substitute  # pylint: disable=no-member
    def get_resolved_path(self, *args, **kwargs):
        path = super(Player, self).get_resolved_path(*args, **kwargs)
        self._success = (self.action_log and self.action_log[-2] == 'SUCCESS!')
        if not self._success:
            utils.notification('UpNext', 'Unable to play video')
        elif not SETTINGS.queue_from_tmdb:
            self.current_player['make_playlist'] = 'false'
        return path

    def get_next_episodes(self):
        player = self.current_player or self.get_default_player()
        if not player:
            return None
        episodes = get_next_episodes(self.tmdb_id, self.season, self.episode,  # pylint: disable=not-callable
                                     player.get('file'))
        return episodes

    def queue(self):
        self.current_player = self.get_default_player()  # pylint: disable=attribute-defined-outside-init
        self.queue_next_episodes(route='make_playlist')

    @Players._substitute  # pylint: disable=no-member
    def select_player(self, *args, **kwargs):
        if SETTINGS.exact_tmdb_match:
            return None
        return super(Player, self).select_player(*args, **kwargs)


def generate_tmdbhelper_play_url(upnext_data, player):
    video_details = upnext_data.get('next_video')
    offset = 0
    play_url = 'plugin://service.upnext/play_plugin?{0}'
    if not video_details:
        video_details = upnext_data.get('current_video')
        offset = 1
        play_url = 'plugin://plugin.video.themoviedb.helper/?{0}'

    tmdb_id = video_details.get('tmdb_id', '')
    title = video_details.get('showtitle', '')
    season = utils.get_int(video_details, 'season')
    episode = utils.get_int(video_details, 'episode') + offset

    query = urlencode({
        'info': 'play',
        'mode': 'play',
        'player': player,
        'tmdb_type': 'tv',
        'tmdb_id': tmdb_id,
        'query': title,
        'season': season,
        'episode': episode
    })

    return play_url.format(query)
