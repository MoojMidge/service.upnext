# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals

import utils
from settings import SETTINGS


def log(msg, level=utils.LOGERROR):
    """Log wrapper"""

    utils.log(msg, name=__name__, level=level)


class Import(object):  # pylint: disable=too-few-public-methods
    def __new__(cls, name=None):
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
            module = __import__('themoviedb_helper', fromlist=[name])
            base_class = getattr(module, name)
            initialised = True
        except (AttributeError, ImportError):
            from traceback import format_exc
            log('ImportError: TMDBHelper {0}\n{1}'.format(name, format_exc()))
            base_class = object
            initialised = False

        return type(name, (base_class,), {
            '_initialised': initialised,
            '_substitute': classmethod(substitute),
            'is_initialised': classmethod(is_initialised),
        })


TMDb = Import('TMDb')  # pylint: disable=invalid-name
Players = Import('Players')  # pylint: disable=invalid-name


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
        if not SETTINGS.exact_tmdb_match:
            return player
        assert_keys = set(
            self.players.get(player['file'], {})
            .get('assert', {})
            .get('play_episode', [])
        )
        if {'showname', 'season', 'episode'} - assert_keys:
            return None
        return player

    def failed(self):
        return not self._success

    @Players._substitute  # pylint: disable=no-member
    def get_resolved_path(self, *args, **kwargs):
        path = super(Player, self).get_resolved_path(*args, **kwargs)
        self._success = (self.action_log[-2] == 'SUCCESS!')
        return path

    @Players._substitute  # pylint: disable=no-member
    def select_player(self, *args, **kwargs):
        if SETTINGS.exact_tmdb_match:
            return None
        return super(Player, self).select_player(*args, **kwargs)
