#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mpvshots - automatic screenshot uploader for mpv
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is Free Software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

import threading

from queue import Queue

class Uploader(threading.Thread):

    def __init__(self, backend):
        super().__init__()
        self._backend = backend
        self._upload_queue = Queue()
        self._keep_going = True
        self._retry = None

    def queue_image(self, path):
        """Queue an image for upload."""
        self._upload_queue.put(path)

    def run(self):
        while self._keep_going:
            if self._retry is None:
                path = self._upload_queue.get()
            else:
                path = self._retry
            if path is None:
                break
            with open(path, "rb") as img:
                success = self._backend.upload_image(img.read())
            if not success:
                # try again
                self._retry = path
            else:
                self._retry = None

    def stop(self):
        """Terminate the thread."""
        self._keep_going = False
        self._upload_queue.put(None)
