#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mpvshots - automatic screenshot uploader for mpv
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is Free Software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

import asyncore

from .jsonhandler import JsonRequestHandler

class Mpvshotsd(asyncore.dispatcher):

    def __init__(self, host, port, uploader):
        asyncore.dispatcher.__init__(self)

        self.uploader = uploader

        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        JsonRequestHandler(sock, self)

    def exit(self):
        self.uploader.stop()
        self.close()
        asyncore.close_all()
