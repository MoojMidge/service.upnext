# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals

import sys
from importlib import import_module
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import constants
import utils
from settings import SETTINGS


def log(msg, level=utils.LOGDEBUG):
    """Log wrapper"""

    utils.log(msg, name=__name__, level=level)


class Import(object):  # pylint: disable=too-few-public-methods
    def __new__(cls, name, mod_attrs=None):
        try:
            try:
                module = sys.modules[name]
            except KeyError:
                module = import_module(name)
            if mod_attrs is not None:
                module.__dict__.update(mod_attrs)
        except ImportError:
            from traceback import format_exc

            log('ImportError: {0}'.format(format_exc()))
            module = None
        return module


class ObjectImport(Import):  # pylint: disable=too-few-public-methods
    # pylint: disable-next=arguments-differ
    def __new__(cls, name, obj_name, obj_attrs=None, **kwargs):
        module = super(ObjectImport, cls).__new__(cls, name, **kwargs)
        try:
            imported_obj = getattr(module, obj_name)
            if obj_attrs is not None:
                imported_obj.__dict__.update(obj_attrs)
        except AttributeError:
            from traceback import format_exc

            log('ImportError: {0}'.format(format_exc()))
            imported_obj = None
        return imported_obj


class ClassImport(ObjectImport):  # pylint: disable=too-few-public-methods
    def __new__(cls, name, obj_name, obj_attrs=None, **kwargs):
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

        if 'obj' in kwargs:  # pylint: disable=consider-using-get
            imported_obj = kwargs['obj']
        else:
            imported_obj = super(ClassImport, cls).__new__(
                cls, name, obj_name, **kwargs
            )
        if imported_obj:
            initialised = True
        else:
            imported_obj = object
            initialised = False

        _dict = {
            '_initialised': initialised,
            '_substitute': classmethod(substitute),
            'is_initialised': classmethod(is_initialised),
        }
        if obj_attrs is not None:
            _dict.update(obj_attrs)
        return type(obj_name, (imported_obj,), _dict)


# pylint: disable=invalid-name
TMDb = ClassImport(
    'tmdbhelper_lib.api.tmdb.api',
    'TMDb',
    obj_attrs={'api_key': 'b5004196f5004839a7b0a89e623d3bd2'},
)
get_next_episodes = ObjectImport(
    'tmdbhelper_lib.player.details',
    'get_next_episodes',
    mod_attrs={'TMDb': TMDb},
)
get_item_details = ObjectImport(
    'tmdbhelper_lib.player.details',
    'get_item_details',
    mod_attrs={'TMDb': TMDb},
)
Players = ClassImport(
    'tmdbhelper_lib.player.players',
    'Players',
    mod_attrs={
        'TMDb': TMDb,
        'get_item_details': get_item_details,
    },
)


class TMDB(TMDb):  # pylint: disable=inherit-non-class,too-few-public-methods
    def get_id_details(self, title, season, episode):
        tmdb_id = self.get_tmdb_id(
            tmdb_type='tv', query=title, season=season, episode=episode
        )
        if not tmdb_id:
            return None, None
        details = self.get_details(
            tmdb_type='tv', tmdb_id=tmdb_id, season=season, episode=episode
        )
        return tmdb_id, details


# pylint: disable=inherit-non-class,too-few-public-methods
class Player(Players):
    @Players._substitute  # pylint: disable=no-member
    def __init__(self, **kwargs):
        if 'tmdb_id' not in kwargs:
            # pylint: disable-next=no-value-for-parameter,not-callable
            kwargs['tmdb_id'] = TMDB().get_tmdb_id(**kwargs)
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
        # pylint: disable-next=attribute-defined-outside-init
        self.current_player = player
        return player

    @Players._substitute  # pylint: disable=no-member
    def get_resolved_path(self, *args, **kwargs):
        path = super(Player, self).get_resolved_path(*args, **kwargs)
        self._success = (self.action_log and self.action_log[-2] == 'SUCCESS!')
        if not self._success:
            utils.notification('UpNext', 'Unable to play video')
            from xbmc import Player as _Player, PlayList, PLAYLIST_VIDEO

            playlist = PlayList(PLAYLIST_VIDEO)
            playlist.clear()
            _Player().stop()
        elif not SETTINGS.queue_from_tmdb:
            self.current_player['make_playlist'] = 'false'
        return path

    def get_next_episodes(self):
        player = self.current_player or self.get_default_player()
        if not player:
            return None
        # pylint: disable-next=not-callable
        episodes = get_next_episodes(self.tmdb_id, self.season, self.episode,
                                     player.get('file')) or []
        for episode in episodes:
            episode.path = 'plugin://service.upnext/play_plugin'
        return episodes

    @staticmethod
    def queue(episodes):
        from xbmc import PlayList, PLAYLIST_VIDEO

        playlist = PlayList(PLAYLIST_VIDEO)
        if playlist.getposition() == -1:
            return False

        for li in episodes[1:]:
            listitem = li.get_listitem()
            playlist.add(listitem.getPath(), listitem)
        return True

    @Players._substitute  # pylint: disable=no-member
    def select_player(self, *args, **kwargs):
        if SETTINGS.exact_tmdb_match:
            return None
        return super(Player, self).select_player(*args, **kwargs)


def generate_tmdbhelper_play_url(upnext_data, player):
    video_details = upnext_data.get('next_video')
    if video_details:
        offset = 0
        play_url = ''.join((
            'plugin://',
            constants.ADDON_ID,
            '/play_plugin?{0}',
        ))
    else:
        video_details = upnext_data.get('current_video')
        offset = 1
        play_url = ''.join((
            'plugin://',
            constants.TMDBH_ADDON_ID,
            '/?{0}',
        ))

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
