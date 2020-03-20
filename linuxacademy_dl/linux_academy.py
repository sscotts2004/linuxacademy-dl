# -*- coding: utf-8 -*-
#
#
# This file is a part of 'linuxacademy-dl' project.
#
# Copyright (c) 2016-2017, Vassim Shahir
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

from __future__ import unicode_literals, absolute_import, print_function
from . import __title__
from distutils.spawn import find_executable
from .url_templates import render_url
from ._session import session
from .exceptions import LinuxAcademyException
from .course import Course

from .url_templates import LOGIN_URL, LOGOUT_URL

import os
import logging

logger = logging.getLogger(__title__)


class DownloadParams(object):
    def __init__(self, output_dir, use_ffmpeg=False,
                 video_quality='1080'):
        self.output_dir = output_dir
        self.use_ffmpeg = use_ffmpeg
        self.video_quality = video_quality

    @property
    def output_dir(self):
        return self.__output_dir

    @output_dir.setter
    def output_dir(self, value):
        if os.path.exists(value):
            if not os.access(value, os.W_OK):
                raise LinuxAcademyException(
                    'The output directory does not have write permission.'
                )
        else:
            raise LinuxAcademyException(
                'The output directory does not exist.'
            )
        self.__output_dir = value

    @property
    def use_ffmpeg(self):
        return self.__use_ffmpeg

    @use_ffmpeg.setter
    def use_ffmpeg(self, value):
        if value and not find_executable('ffmpeg'):
            raise LinuxAcademyException(
                'ffmpeg is not found. Please install it.'
            )
        self.__use_ffmpeg = value

    @property
    def video_quality(self):
        return self.__video_quality

    @video_quality.setter
    def video_quality(self, value):
        if value not in ['1080', '720', '480', '360']:
            raise LinuxAcademyException(
                'Video quality is invalid.'
            )
        self.__video_quality = value


class LinuxAcademy(object):
    def __init__(self, course_url, username, password, output_dir,
                 use_ffmpeg=False, video_quality='1080'):

        self.username = username
        self.password = password

        self._course = Course(
            course_id=self.get_course_id(course_url),
            download_params=DownloadParams(
                output_dir,
                use_ffmpeg,
                video_quality
            )
        )

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, *args):
        self.logout()

    def get_course_id(self, url):
        return int(url.rsplit("/", 1)[1])

    def login(self):
        logger.info('Logging in ...')

        status_code = render_url(
            session, LOGIN_URL,
            payload={
                "username": self.username,
                "password": self.password
            }
        ).status_code

        # There will be a redirect if the login is successful.
        # Otherwise it will be an invalid login
        if status_code == 200:
            raise LinuxAcademyException(
                'Username or email not found! Please try again.'
            )

    def logout(self):
        render_url(session, LOGOUT_URL)
        logger.info('Logged Out!')

    def analyze(self):
        logger.info('Analyzing ...')
        self._course.assets()

    def download(self):
        logger.info('Downloading files ...')
        self._course.download()
        logger.info('Downloaded all files.')
