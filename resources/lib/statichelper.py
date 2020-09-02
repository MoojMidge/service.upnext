# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
"""Implements static helper functions used elsewhere in the add-on"""

from __future__ import absolute_import, division, unicode_literals
import sys


IS_PYTHON2 = sys.version_info.major == 2


def to_unicode(text, encoding='utf-8', errors='strict'):
    """Force text to unicode"""
    if IS_PYTHON2 and isinstance(text, (bytes, str)):
        return text.decode(encoding, errors)
    return text


def from_unicode(text, encoding='utf-8', errors='strict'):
    """Force unicode to text"""
    if IS_PYTHON2 and isinstance(text, unicode):  # noqa: F821; pylint: disable=undefined-variable,useless-suppression
        return text.encode(encoding, errors)
    return text
