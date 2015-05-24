#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" twitter.py

This module is the Twitter backend of mpvshots, and handles uploading images to
the popular microblogging service.

"""

import os

from slowtils import file

from twitter import Twitter, OAuth, oauth_dance, read_token_file
from twitter.api import TwitterHTTPError
from ._backend import Backend

# TODO: this must be configurable later on
CONSUMER_KEY = "P0SQXtC4wrYUTzyK5ZcPBrGwP"
CONSUMER_SECRET = "yOjZ8yGLFzgfH1vvt7oYrrIH9847pAjPOXlv8zWN2T96q2h1KC"
CREDENTIALS_FILE = "~/.mpvshots/credentials"
# TODO: it should probably be possible to have more than one user later, this
# would require separate token files.
OAUTH_TOKEN_FILE = os.path.expanduser("~/.mpvshots/oauth_token")


class TwitterBackend(Backend):

    """ The Twitter backend for mpvshots.

    """

    def __init__(self):
        if not file.exists(OAUTH_TOKEN_FILE):
            oauth_dance("mpvshots",
                        CONSUMER_KEY,
                        CONSUMER_SECRET,
                        OAUTH_TOKEN_FILE)

        oauth_token, oauth_secret = read_token_file(OAUTH_TOKEN_FILE)

        oauth = OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET)
        self._twitter = Twitter(auth=oauth)
        self._upload = Twitter(domain="upload.twitter.com", auth=oauth)

    def upload_image(self, image):
        try:
            upload_status = self._upload.media.upload(media=image)
        except TwitterHTTPError:
            return False
        img_id = str(upload_status["media_id"])
        try:
            self._twitter.statuses.update(media_ids=img_id)
        except TwitterHTTPError:
            return False
        return True

