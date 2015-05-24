#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains the basic definition of a backend for mpvshots."""

from abc import ABCMeta, abstractmethod

class Backend(metaclass=ABCMeta):

    @abstractmethod
    def upload_image(self, image_data):
        """This method must take a raw image, and upload it to the service.

        It returns True if successful and False otherwise.

        TODO: This is bad error handling, but should suffice for now.

        """
        return NotImplemented
