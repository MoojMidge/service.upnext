# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""Implements helper functions used elsewhere in the addon"""

from __future__ import absolute_import, division, unicode_literals

import base64
import binascii
import json
import sys
import threading
from itertools import chain
from operator import itemgetter
from re import (
    compile as re_compile,
    split as re_split,
)
from string import punctuation

from dateutil.parser import parse as dateutil_parse

import constants
import statichelper
import xbmc
import xbmcaddon
import xbmcgui


class Profiler(object):
    """Class used to profile a block of code"""

    __slots__ = ('__weakref__', '_enabled', '_profiler', '_reuse', 'name', )

    from cProfile import Profile as _Profile
    from pstats import Stats as _Stats
    try:
        from StringIO import StringIO as _StringIO
    except ImportError:
        from io import StringIO as _StringIO
    from functools import wraps as _wraps
    _wraps = staticmethod(_wraps)
    from weakref import ref as _ref

    class Proxy(_ref):
        def __call__(self, *args, **kwargs):
            return super(Profiler.Proxy, self).__call__().__call__(
                *args, **kwargs
            )

        def __enter__(self, *args, **kwargs):
            return super(Profiler.Proxy, self).__call__().__enter__(
                *args, **kwargs
            )

        def __exit__(self, *args, **kwargs):
            return super(Profiler.Proxy, self).__call__().__exit__(
                *args, **kwargs
            )

    _instances = set()

    def __new__(cls, *args, **kwargs):
        self = super(Profiler, cls).__new__(cls)
        cls._instances.add(self)
        if not kwargs.get('enabled') or kwargs.get('lazy'):
            self.__init__(*args, **kwargs)
            return cls.Proxy(self)
        return self

    def __init__(self, enabled=True, lazy=True, name=__name__, reuse=False):
        self._enabled = enabled
        self._profiler = None
        self._reuse = reuse
        self.name = name

        if enabled and not lazy:
            self._create_profiler()

    def __del__(self):
        self.__class__._instances.discard(self)  # pylint: disable=protected-access

    def __enter__(self):
        if not self._enabled:
            return

        if not self._profiler:
            self._create_profiler()

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        if not self._enabled:
            return

        log('Profiling stats: {0}'.format(self.get_stats(reuse=self._reuse)),
            name=self.name, level=LOGDEBUG)
        if not self._reuse:
            self.__del__()

    def __call__(self, func=None, name=__name__, reuse=False):
        """Decorator used to profile function calls"""

        if not func:
            self._reuse = reuse
            self.name = name
            return self

        @self.__class__._wraps(func)  # pylint: disable=protected-access
        def wrapper(*args, **kwargs):
            """Wrapper to:
               1) create a new Profiler instance;
               2) run the function being profiled;
               3) print out profiler result to the log; and
               4) return result of function call"""

            name = getattr(func, '__qualname__', None)
            if name:
                # If __qualname__ is available (Python 3.3+) then use it
                pass

            elif args and getattr(args[0], func.__name__, None):
                if isinstance(args[0], type):
                    class_name = args[0].__name__
                else:
                    class_name = args[0].__class__.__name__
                name = '{0}.{1}'.format(class_name, func.__name__)

            elif (func.__class__
                  and not isinstance(func.__class__, type)
                  and func.__class__.__name__ != 'function'):
                name = '{0}.{1}'.format(func.__class__.__name__, func.__name__)

            elif func.__module__:
                name = '{0}.{1}'.format(func.__module__, func.__name__)

            else:
                name = func.__name__

            self.name = name
            with self:
                result = func(*args, **kwargs)

            return result

        if not self._enabled:
            self.__del__()
            return func
        return wrapper

    def _create_profiler(self):
        self._profiler = self._Profile()
        self._profiler.enable()

    def disable(self):
        if self._profiler:
            self._profiler.disable()

    def enable(self, flush=False):
        self._enabled = True
        if flush or not self._profiler:
            self._create_profiler()
        else:
            self._profiler.enable()

    def get_stats(self, flush=True, reuse=False):
        if not (self._enabled and self._profiler):
            return None

        self.disable()

        output_stream = self._StringIO()
        try:
            self._Stats(
                self._profiler,
                stream=output_stream
            ).strip_dirs().sort_stats('cumulative').print_stats(20)
        # Occurs when no stats were able to be generated from profiler
        except TypeError:
            pass
        output = output_stream.getvalue()
        output_stream.close()

        if reuse:
            # If stats are accumulating then enable existing/new profiler
            self.enable(flush)

        return output


def wait(timeout=None):
    if not timeout:
        timeout = 0
    elif timeout < 0:
        timeout = 0.1
    return xbmc.Monitor().waitForAbort(timeout)


def abort_requested():
    return xbmc.Monitor().abortRequested()


def jsonrpc(batch=None, **kwargs):
    """Perform JSONRPC calls"""

    if not batch and not kwargs:
        return None

    do_response = False
    for request_id, kwargs in enumerate(batch or (kwargs, )):
        do_response = (not kwargs.pop('no_response', False)) or do_response
        if do_response and 'id' not in kwargs:
            kwargs['id'] = request_id
        kwargs['jsonrpc'] = '2.0'

    request = json.dumps(batch or kwargs, default=tuple)
    response = xbmc.executeJSONRPC(request)
    return json.loads(response) if do_response else None


def get_addon(addon_id=None, retry_attempts=3):
    """Return addon instance"""

    addon = None

    # Not sure why the retries are needed but Kodi sometimes thinks the addon
    # is disabled when it is starting the service. Some kind of race condition?
    attempts_left = 1 + retry_attempts
    while attempts_left > 0:
        try:
            if addon_id:
                addon_id = statichelper.from_unicode(addon_id)
                addon = xbmcaddon.Addon(addon_id)
            else:
                addon = xbmcaddon.Addon()
            break
        except RuntimeError:
            pass

        attempts_left -= 1
        if attempts_left > 0:
            wait(1)

    return addon


ADDON = get_addon(constants.ADDON_ID)
_KODI_MAJOR_VERSION = jsonrpc(
    method='Application.GetProperties',
    params={'properties': ['version']}
).get('result').get('version').get('major')


def get_addon_info(key):
    """Return addon information"""

    key = statichelper.from_unicode(key)
    value = ADDON.getAddonInfo(key)
    return statichelper.to_unicode(value)


def get_addon_id():
    """Return addon ID"""

    return get_addon_info('id')


def get_addon_path():
    """Return addon path"""

    return get_addon_info('path')


def supports_python_api(version):
    """Return True if Kodi supports target Python API version"""

    return _KODI_MAJOR_VERSION >= version


def get_property(key, window_id=constants.WINDOW_HOME):
    """Get a Window property"""

    key = statichelper.from_unicode(key)
    value = xbmcgui.Window(window_id).getProperty(key)
    return statichelper.to_unicode(value)


def set_property(key, value, window_id=constants.WINDOW_HOME):
    """Set a Window property"""

    # setProperty accepts bytes/str/unicode in Kodi18+ but truncates bytes
    # when a null byte (\x00) is encountered in Kodi19+
    key = statichelper.from_unicode(key)
    value = statichelper.from_unicode(value)
    return xbmcgui.Window(window_id).setProperty(key, value)


def clear_property(key, window_id=constants.WINDOW_HOME):
    """Clear a Window property"""

    key = statichelper.from_unicode(key)
    return xbmcgui.Window(window_id).clearProperty(key)


def get_int(obj, key=None, default=constants.UNDEFINED, strict=False):
    """Returns an object or value for the given key in object, as an integer.
       Returns default value if key or object is not available.
       Returns value if value cannot be converted to integer."""

    try:
        val = obj.get(key, default) if key else obj
    except (AttributeError, TypeError):
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default if strict or not val else val


def encode_data(data, encoding='base64'):
    """Encode data for a notification event"""

    encode_methods = {
        'hex': binascii.hexlify,
        'base64': base64.b64encode
    }
    encode_method = encode_methods.get(encoding)

    if not encode_method:
        log('Unknown encoding type: {0}'.format(encoding), level=LOGWARNING)
        return None

    try:
        json_data = json.dumps(data).encode()
        encoded_data = encode_method(json_data)
    except (TypeError, ValueError, binascii.Error):
        log('{0} encode error: {1}'.format(encoding, data), level=LOGWARNING)
        return None

    if sys.version_info[0] > 2:
        encoded_data = encoded_data.decode('ascii')

    return encoded_data


def decode_data(encoded_data=None, serialised_json=None, compat_mode=True):
    """Decode JSON data coming from a notification event"""

    decoded_data = None
    encoding = None

    # Compatibility with Addon Signals which wraps serialised data in square
    # brackets to generate an array/list
    if compat_mode and encoded_data:
        try:
            encoded_data = json.loads(encoded_data)[0]
        except (IndexError, TypeError, ValueError):
            encoded_data = None

    if encoded_data:
        decode_methods = {
            'hex': binascii.unhexlify,
            'base64': base64.b64decode
        }

        for encoding, decode_method in decode_methods.items():
            try:
                serialised_json = decode_method(encoded_data)
                break
            except (TypeError, binascii.Error):
                pass
        else:
            encoding = None

    if serialised_json:
        try:
            # NOTE: With Python 3.5 and older json.loads() does not support
            # bytes or bytearray, so we convert to unicode
            serialised_json = statichelper.to_unicode(serialised_json)
            decoded_data = json.loads(serialised_json)
        except (TypeError, ValueError):
            pass

    return decoded_data, encoding


def event(message, data=None, sender=None, encoding='base64'):
    """Send internal notification event"""

    data = data or {}
    sender = sender or get_addon_id()

    encoded_data = encode_data(data, encoding=encoding)
    if not encoded_data:
        return None

    return jsonrpc(
        method='JSONRPC.NotifyAll',
        params={
            'sender': '{0}.SIGNAL'.format(sender),
            'message': message,
            'data': [encoded_data],
        }
    )


def get_global_setting(setting):
    """Get a Kodi setting"""

    result = jsonrpc(
        method='Settings.GetSettingValue',
        params={'setting': setting}
    )
    return result.get('result', {}).get('value')


# Log levels                      | v18 | v19
LOGDEBUG = xbmc.LOGDEBUG        # |  0  |  0
LOGINFO = xbmc.LOGINFO          # |  1  |  1
# LOGNOTICE = xbmc.LOGNOTICE    # |  2  |  Deprecated
LOGWARNING = xbmc.LOGWARNING    # |  3  |  2
LOGERROR = xbmc.LOGERROR        # |  4  |  3
# LOGSEVERE = xbmc.LOGSEVERE    # |  5  |  Deprecated
LOGFATAL = xbmc.LOGFATAL        # |  6  |  4
LOGNONE = xbmc.LOGNONE          # |  7  |  5

LOG_ENABLE_SETTING = constants.LOG_ENABLE_DEBUG
DEBUG_LOG_ENABLE = get_global_setting('debug.showloginfo')
MIN_LOG_LEVEL = LOGINFO if supports_python_api(19) else LOGINFO + 1


def log(msg, name=__name__, level=LOGINFO):
    """Log information to the Kodi log"""

    # Log everything
    if LOG_ENABLE_SETTING == constants.LOG_ENABLE_DEBUG:
        log_enable = level != LOGNONE
    # Only log important messages
    elif LOG_ENABLE_SETTING == constants.LOG_ENABLE_INFO:
        log_enable = LOGDEBUG < level < LOGNONE
    # Log nothing
    else:
        log_enable = False

    if not log_enable:
        return

    # Force minimum required log level to display in Kodi event log
    if not DEBUG_LOG_ENABLE and level < MIN_LOG_LEVEL:  # pylint: disable=consider-using-max-builtin
        level = MIN_LOG_LEVEL

    # Convert to unicode for string formatting with Unicode literal
    msg = statichelper.to_unicode(msg)
    msg = '[{0}] {1} -> {2}'.format(get_addon_id(), name, msg)
    # Convert back for older Kodi versions
    msg = statichelper.from_unicode(msg)
    xbmc.log(msg, level=level)


def localize(string_id):
    """Return the translated string from the .po language files"""

    string = ADDON.getLocalizedString(string_id)
    return statichelper.to_unicode(string)


def get_year(date_string):
    """Extract year from a date string. Returns year, or input if unable to
    parse"""

    try:
        date_object = dateutil_parse(date_string)
        return date_object.year
    except ValueError:
        return date_string


def iso_datetime(date_string, separator=str(' ')):
    """Parse arbitrary date string and output in YYYY-MM-DD hh:mm:ss format"""

    try:
        date_object = dateutil_parse(date_string).replace(microsecond=0)
    except ValueError:
        return date_string

    return date_object.isoformat(separator)


def localize_date(date_string):
    """Localize date format"""

    date_format = xbmc.getRegion('dateshort')

    try:
        date_object = dateutil_parse(date_string)
    except ValueError:
        return None, date_string

    return date_object, date_object.strftime(date_format)


def localize_time(time_object):
    """Localize time format"""

    time_format = xbmc.getRegion('time')

    # Fix a bug in Kodi v18.5 and older causing double hours
    # https://github.com/xbmc/xbmc/pull/17380
    time_format = time_format.replace('%H%H:', '%H:')

    # Strip off seconds
    time_format = time_format.replace(':%S', '')

    return time_object.strftime(time_format)


def notification(heading, message,
                 icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=False):
    """Display a notification in Kodi with notification sound off by default"""

    heading = statichelper.from_unicode(heading)
    message = statichelper.from_unicode(message)
    xbmcgui.Dialog().notification(heading, message, icon, time, sound)


def create_lock():
    return threading.Lock()


def create_event():
    return threading.Event()


def run_threaded(target, delay=None, args=None, kwargs=None):
    """Executes the target in a separate thread or timer"""

    if args is None:
        args = ()

    if kwargs is None:
        kwargs = {}

    if delay is not None:
        thread = threading.Timer(delay, target, args=args, kwargs=kwargs)
    else:
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    # Daemon threads may not work in Kodi, but enable it anyway
    thread.daemon = True
    thread.start()
    return thread


def time_to_seconds(time_str):
    """Convert a time string in the format hh:mm:ss to seconds as an integer"""

    seconds = 0

    time_split = time_str.split(':')
    try:
        seconds += int(time_split[-1])
        seconds += int(time_split[-2]) * 60
        seconds += int(time_split[-3]) * 3600
    except (IndexError, ValueError):
        pass

    return seconds


def calc_wait_time(end_time=None, start_time=0, rate=None):
    if not end_time or not rate or rate < 1:
        return None

    return max(0, (end_time - start_time) // rate)


def create_item_details(item, source=None,
                        media_type=None, playlist_position=None):
    """Create item_details dict used by state, api and plugin modules"""

    if item == 'empty':
        return {
            'details': {},
            'source': None,
            'media_type': None,
            'db_id': constants.UNDEFINED,
            'group_name': None,
            'group_idx': constants.UNDEFINED,
        }

    if not item or not source:
        return None

    is_episode = (media_type == 'episode') or ('tvshowid' in item)

    if playlist_position:
        group_name = constants.MIXED_PLAYLIST
        group_idx = playlist_position

    elif is_episode:
        group_name = '-'.join((
            str(get_int(item, 'tvshowid')),
            item.get('showtitle', constants.UNTITLED),
            str(get_int(item, 'season'))
        ))
        group_idx = get_int(item, 'episode')

    else:
        group_name = '-'.join((
            str(get_int(item, 'setid')),
            item.get('set', constants.UNTITLED),
        ))
        group_idx = playlist_position

    item_details = {
        'details': item,
        'source': source,
        'media_type': 'episode' if is_episode else media_type,
        'db_id': (
            get_int(item, 'episodeid' if is_episode else 'movieid', None)
            or get_int(item, 'id')
        ),
        'group_name': group_name,
        'group_idx': group_idx,
    }
    return item_details


def merge_iterable(*iterables, **kwargs):
    sort = kwargs.get('sort')

    merged = chain.from_iterable(iterables)
    if sort:
        descending = kwargs.get('ascending', True)
        key = None if isinstance(sort, bool) else itemgetter(sort)
        threshold = kwargs.get('threshold')

        if key and threshold is not None:
            merged = (item for item in merged if key(item) > threshold)

        merged = sorted(merged, key=key, reverse=descending)
    return merged


def strip_punctuation(value,  # pylint: disable=dangerous-default-value, too-many-arguments
                      table=dict.fromkeys(map(ord, punctuation)),
                      _frozenset=frozenset,
                      _len=len,
                      _punctuation=set(punctuation)):

    length = _len(value)
    if length < 3:
        return ''
    upper = value.upper()
    if length == 3 and value != upper:
        return ''
    if _punctuation & _frozenset(upper):
        return upper.translate(table)
    return upper


def tokenise(values,  # pylint: disable=too-many-arguments
             split=True,
             strip=strip_punctuation,
             remove=frozenset({
                 '', 'ABOUT', 'AFTER', 'FROM', 'HAVE', 'HERS', 'INTO', 'ONLY',
                 'OVER', 'THAN', 'THAT', 'THEIR', 'THERE', 'THEM', 'THEN',
                 'THEY', 'THIS', 'WHAT', 'WHEN', 'WHERE', 'WILL', 'WITH',
                 'YOUR', 'DURINGCREDITSSTINGER', 'AFTERCREDITSSTINGER',
                 'COLLECTION'
             }),
             _frozenset=frozenset,
             _map=map,
             _split=re_compile(r'[_\.,]* |[\|/\\]').split):

    tokens = _frozenset()
    for value in values:
        if not value:
            continue
        if split is True:
            tokens = tokens | _frozenset(_split(value))
        elif split:
            tokens = tokens | _frozenset(re_split(split, value))
        else:
            tokens = tokens | _frozenset(value)
    if strip:
        tokens = _frozenset(_map(strip, tokens))
    if remove:
        tokens = tokens - remove
    return tokens


if supports_python_api(19):
    from collections import deque

    def modify_iterable(function, sequence):
        deque(map(function, sequence), maxlen=0)
else:
    modify_iterable = map  # pylint: disable=invalid-name
