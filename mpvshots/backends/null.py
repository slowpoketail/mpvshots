#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mpvshots - automatic screenshot uploader for mpv
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is Free Software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

from ._backend import Backend

class NullBackend(Backend):

    """A backend that discards all images it receives.

    For testing purposes only.

    """

    def upload_image(self, _):
        return True
