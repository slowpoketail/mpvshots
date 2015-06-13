#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mpvshots - automatic screenshot uploader for mpv
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is Free Software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

import plac
import tempfile
import subprocess
import socket
import daemon
import asyncore
import json

from . import mpv
from . import backends
from .uploader import Uploader
from .daemon import Mpvshotsd

class Mpvshots:

    commands = (
        "shot",
        "upload",
        "daemon",
    )

    def __enter__(self):
        self._mpv = mpv.Mpv()
        self._mpv.start()

    def __exit__(self, etype, exc, tb):
        self._mpv.stop()

    def shot(self,
             subtitles: ("include subtitles in the video", "flag", "s"),
             show:      ("preview the screenshot", "flag", "f"),
             upload:    ("immediately upload the screenshot", "flag", "u"),
             host:      ("address the daemon is listening on",
                         "option", "a") = "localhost",
             port:      ("port the daemon is listening on",
                         "option", "p") = 9001,
             ):
        """Take a screenshot in mpv."""
        fname = tempfile.mktemp(
            prefix="mpvshots",
            suffix=".jpeg"
        )
        if subtitles:
            mode = "subtitles"
        else:
            mode = "video"
        reply = self._mpv.send_command("screenshot_to_file", fname, mode)
        if not reply.ask()["error"] == "success":
            yield "screenshot failed"
        # take the regular screenshot
        reply = self._mpv.send_command("screenshot", mode)
        if not reply.ask()["error"] == "success":
            yield "regular screenshot failed"

        if show:
            try:
                subprocess.call(["xdg-open", fname])
            except:
                yield "something went wrong while previewing the screenshot"
                yield "do you have xdg-utils installed?"
        if upload:
            yield "attempting to upload the screenshot"
            list(self.upload(fname, host, port))

    def daemon(self,
               shutdown: ("shutdown the daemon", "flag", "s"),
               backend:  ("upload backend to use (default: twitter; "
                          "pass 'list' to get a list of supported backends)",
                          "option", "b")                         = "twitter",
               host:     ("address to listen on", "option", "a") = "localhost",
               port:     ("port to listen on", "option", "p")    = 9001,
               ):
        """Start the mpvshots daemon."""
        if shutdown:
            self._send_cmd(host, port, "shutdown")
            return
        if backend == "list":
            for b in backends.list():
                print(b)
            return
        if not backend in backends.list():
            yield("backend '{}' does not exist".format(backend))
            exit(1)
        uploader = Uploader(backends.get(backend))
        uploader.start()
        mpvshotsd = Mpvshotsd(host, port, uploader)
        asyncore.loop()

    def upload(self,
               path: "image to upload",
               host: ("address the daemon is listening on",
                      "option", "a") = "localhost",
               port: ("port the daemon is listening on",
                      "option", "p") = 9001,
               ):
        """Queue an image for upload via the daemon."""
        try:
            self._send_cmd(host, port, "upload", path)
        except socket.error:
            yield "something went wrong, is the daemon running?"

    @staticmethod
    def _send_cmd(host, port, cmd_name, *params):
        """Send a command to the daemon."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        json_cmd = Mpvshots._make_json_command(cmd_name, *params)
        sock.send(json_cmd)
        sock.close()

    @staticmethod
    def _make_json_command(cmd_name, *params):
        command = [cmd_name]
        command.extend(params)
        msg = {"command": command}
        return json.dumps(msg).encode() + b"\n"
