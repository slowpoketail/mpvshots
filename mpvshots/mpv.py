#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mpvshots - automatic screenshot uploader for mpv
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is Free Software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

from threading import Thread
from queue import Queue, Empty

from . import promise

import socket
import json

from slowtils import trace

# TODO: get this from a config file
MPV_SOCKET_PATH = "/tmp/mpv.sock"

class Mpv(Thread):

    """ An interface to mpv's JSON IPC.

    """


    def __init__(self):
        super().__init__()
        self._events = Queue()
        self._awaiting_reply = Queue()
        self._mpvsock = self._make_socket()
        self._keep_going = True

    @staticmethod
    def _make_socket():
        return socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    @staticmethod
    def _connect_socket(sock):

        sock.connect(MPV_SOCKET_PATH)

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
                fulfill = self._awaiting_reply.get_nowait()
                fulfill(what)
            except Empty:
                pass
        elif "event" in what.keys():
            self._events.put(what)
        else:
            pass

    def send_command(self, cmd_name, *params):
        """Send a command to mpv.

        This method will return a promise as a reply, which can be ask()'d for
        its value. This will block until the reply arrives.

        """
        if not self.is_alive():
            raise Exception("Listening process is no longer alive.")
        cmd = self._make_json_command(cmd_name, *params)
        reply_promise, fulfill = promise.new()
        self._awaiting_reply.put(fulfill)
        self._mpvsock.send(cmd)
        return reply_promise

    def run(self):
        self._connect_socket(self._mpvsock)
        # temporary storage for partial lines
        partial_line = ""
        while self._keep_going:
            data = partial_line + self._mpvsock.recv(4096).decode()
            if data == "":
                break
            lines = data.split("\n")
            for line in lines[:-1]:
                self._read_json(line)

            partial_line = lines[-1]
        self._mpvsock.close()

    def get_event(self, block=True, timeout=None):
        return self._events.get(block, timeout)

    def get_event_nowait(self):
        return self.get_event(block=False)

    def stop(self):
        """Stop the daemon."""
        self._keep_going = False
        # we send a command to get the loop to terminate
        self.send_command("get_property", "pause")
