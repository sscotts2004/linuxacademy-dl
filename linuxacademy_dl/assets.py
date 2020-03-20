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
from .downloader import DownloadEngine
from .parsers import PlaylistParser, ChunkListParser
from .utils import clean_html
from ._session import session
from .url_templates import BASE_URL
from six.moves.urllib.parse import urljoin
import re
import os
import logging


logger = logging.getLogger(__title__)
REGEX_M3U8 = "var wowzaUrl2 = " \
             "'([a-zA-Z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\(\)\*\+\,\;\=\`]+)';"


class LessonProcessor(object):

    m3u8_grabber = re.compile(REGEX_M3U8)

    def __init__(self, url, title, video_quality='1080'):
        self.url = url
        self.title = title
        self.video_quality = video_quality

    def get_m3u8_playlist_url(self, lesson_page_source):
        return LessonProcessor.m3u8_grabber.findall(lesson_page_source)[0]

    def process(self):
        lesson_page_source = clean_html(session.get(
                    urljoin(BASE_URL, self.url[1:])
                ).text
        )
        play_list_url = self.get_m3u8_playlist_url(lesson_page_source)
        play_list_url_base = play_list_url.rsplit("/", 1)[0]
        play_list_data = session.get(play_list_url).text

        parser = PlaylistParser()
        parser.feed(play_list_data)
        play_list_url = "{}/{}".format(
            play_list_url_base,
            parser.parsed_data[self.video_quality]
        )

        parser = ChunkListParser()
        parser.feed(session.get(play_list_url).text)

        result = {
            'data': map(
                lambda x: "{}/{}".format(play_list_url_base, x),
                parser.parsed_data['chunks']
            ),
            'save_resource_as': "{}.{}".format(self.title, "mp4"),
            'd_type': 'hls_data'
        }

        if parser.parsed_data['encryption']:
            result.update({
                'encryption': parser.parsed_data['encryption'],
                'key_uri': parser.parsed_data['uri']
            })

            iv = parser.parsed_data['iv']

            if iv:
                result.update({'iv': iv})

        return [result]

    def __call__(self):
        return self.process()


class Asset(object):
    def __init__(self, url, title, download_params, download_at=''):
        self.url = url
        self.title = title
        self.download_params = download_params
        self.save_to = os.path.join(
            self.download_params.output_dir, download_at
        )
        self._download_engine = DownloadEngine(self.download_params.use_ffmpeg)

        self._resources = None

    def get_asset_processor(self):
        if self.url.find("/cp/courses/lesson") > -1:
            return LessonProcessor(
                url=self.url, title=self.title,
                video_quality=self.download_params.video_quality
            )
        return lambda *args, **kwargs: []

    def get_resources(self):
        processor = self.get_asset_processor()
        return processor()

    def analyze(self):
        self._resources = self.get_resources()

    def download(self):
        if self._resources is None:
            self.analyze()

        for resource in self._resources:
            self._download_engine(
                    resource,
                    self.save_to
            )
