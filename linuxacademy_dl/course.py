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
from .parsers import SyllabusParser
from .url_templates import render_url
from ._session import session
from .exceptions import LinuxAcademyException
from .assets import Asset

from .url_templates import COURSE_LIST, COURSE_SYLLABUS

import json
import logging

logger = logging.getLogger(__title__)


class Course(object):
    def __init__(self, course_id, download_params):
        self.course_id = course_id
        self.download_params = download_params

        self._assets = None

    def get_title(self):
        all_courses = json.loads(render_url(session, COURSE_LIST).text)
        for course in all_courses:
            if self.course_id == int(course["id"]):
                return course["title"]

    def _fetch_syllabus(self):
        return render_url(
            session,
            COURSE_SYLLABUS,
            {
             "course_id": self.course_id
            }
        ).text

    def _parse_syllabus(self):
        sp = SyllabusParser()
        sp.feed(self._fetch_syllabus())
        return sp.parsed_data

    def assets(self):
        syllabus = self._parse_syllabus()
        if not syllabus:
            raise LinuxAcademyException('Course not found!')
        self._assets = []
        for chapter_title, chapter_contents in syllabus.items():
            chapter_folder = "{} - {}".format(
                    chapter_contents['index'],
                    chapter_title
            )
            for idx, content in enumerate(chapter_contents['contents'], 1):
                self._assets.append(Asset(
                    url=content['url'],
                    title='{} - {}'.format(idx, content['title']),
                    download_at=chapter_folder,
                    download_params=self.download_params
                ))

    def download(self):
        if self._assets is None:
            self.assets()

        for asset in self._assets:
            asset.download()
