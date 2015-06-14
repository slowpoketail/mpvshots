#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mpvshots - automatic screenshot uploader for mpv
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is Free Software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

import pykka
import asynchat, asyncore

from concurrent.futures import Future
from queue import Queue, Empty

import socket
import json

from slowtils import trace

# TODO: get this from a config file
MPV_SOCKET_PATH = "/tmp/mpv.sock"

class MpvClient(asynchat.async_chat):

    """ An asynchronous interface to mpv's JSON IPC.

    """

    def __init__(self, mpv_sock_path):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connect(mpv_sock_path)
        self.set_terminator(b"\n")

        self._events = Queue()
        self._awaiting_reply = Queue()
        self._ibuffer = []

    @staticmethod
    def _make_json_command(cmd_name, *params):
        command = [cmd_name]
        command.extend(params)
        msg = {"command": command}
        return json.dumps(msg).encode() + b"\n"

    def _read_json(self, jstring):
        what = json.loads(jstring)
        if "error" in what.keys():
            try:
                future = self._awaiting_reply.get_nowait()
                future.set_result(what)
            except Empty:
                pass
        elif "event" in what.keys():
            self._events.put(what)
        else:
            pass

    def send_command(self, cmd_name, *params):
        """Send a command to mpv.

        This method will return a future as a reply.

        """
        cmd = self._make_json_command(cmd_name, *params)
        reply_future = Future()
        self._awaiting_reply.put(reply_future)
        self.send(cmd)
        return reply_future

    def collect_incoming_data(self, data):
        self._ibuffer.append(data)

    def found_terminator(self):
        data = b"".join(self._ibuffer).decode()
        self._ibuffer = []
        self._read_json(data)

    def get_event(self, block=True, timeout=None):
        return self._events.get(block, timeout)

    def get_event_nowait(self):
        return self.get_event(block=False)
