#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mpvshots - automatic screenshot uploader for mpv
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is Free Software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

import asynchat
import json

class JsonRequestHandler(asynchat.async_chat):

    def __init__(self, sock, dispatcher):
        asynchat.async_chat.__init__(self, sock=sock)
        # the parent dispatcher object
        self._dispatcher = dispatcher
        self._incoming_buffer = []
        self.set_terminator(b"\n")

    def _wipe_incoming_buffer(self):
        self._incoming_buffer = []

    def collect_incoming_data(self, data):
        self._incoming_buffer.append(data)

    def found_terminator(self):
        data = b"".join(self._incoming_buffer).decode()
        self._wipe_incoming_buffer()
        msg = json.loads(data)
        if "command" in msg:
            self.handle_command(msg["command"])

    def handle_command(self, cmd):
        cmdname = cmd[0]
        params = cmd[1:]

        if cmdname == "shutdown":
            print("shutting down…")
            self._dispatcher.exit()
        elif cmdname == "upload":
            path = params[0]
            print("uploading '{}'…".format(path))
            self._dispatcher.uploader.queue_image(path)
