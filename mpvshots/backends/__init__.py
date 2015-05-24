#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mpvshots - automatic screenshot uploader for mpv
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is Free Software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

from .twitter import TwitterBackend

_map = {
    "twitter": TwitterBackend,
}

# already initialized backend objects
_init = {}

def register(name, backend, overwrite=False):
    """Register a new backend class.

    A backend must derive from mpvshots.backends.Backend and implement the
    upload_image method.

    Per default, this function refuses to register a backend with a name
    that already exists. Set overwrite=True to change this.
    """
    global _map
    if name in _map and not overwrite:
        raise KeyError("backend named '{}' already exists.".format(name))
    _map[name] = backend


def get(name):
    """Get an initialized backend object."""
    global _init, _map
    if name not in _map:
        _err_does_not_exit(name)
    if name not in _init:
        backend = _map[name]
        return _init.setdefault(name, backend())
    else:
        return _init[name]

def reinit(name):
    """Reload the given backend and return it."""
    global _init, _map
    if name not in _map:
        _err_does_not_exit(name)
    if name in _init:
        del _init[name]
    return get(name)


def _err_does_not_exit(name):
    raise KeyError("backend '{}' does not exist".format(name))


def list():
    return tuple(_map.keys())
