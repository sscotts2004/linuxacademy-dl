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
from io import StringIO
from .utils import clean_filename, clean_html
from six.moves.html_parser import HTMLParser
from six import binary_type


class SyllabusParser(HTMLParser, object):

    def __init__(self):
        self.__flag_write_to_buffer = False
        self.__text_store = StringIO()
        self.total_module_count = 0

        self.parsed_data = {}

        self.__buffer = {}
        self.__buffer_lesson_data = {}

        super(SyllabusParser, self).__init__()

    def __reset_text_store(self):
            self.__text_store.truncate(0)
            self.__text_store.seek(0)

    def feed(self, data):
        super(SyllabusParser, self).feed(clean_html(data))
        self.handle_end_of_doc()

    def __update_parsed_data(self):
        if self.__buffer.get('contents', None) and \
                len(self.__buffer['contents']) > 0:
            title = self.__buffer.pop('title')
            self.parsed_data[title] = self.__buffer
            self.total_module_count += 1
            self.__buffer = {}
            self.__buffer_lesson_data = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        the_tag = tag.lower()
        if the_tag == "h3" and attributes['class'] == "syllabus-section-title":
            self.__update_parsed_data()
            self.__flag_write_to_buffer = True

        if the_tag == "a":
            self.__flag_write_to_buffer = True
            self.__buffer_lesson_data = {'url': attributes['href']}

    def handle_endtag(self, tag):
        the_tag = tag.lower()
        if the_tag == "h3" and self.__flag_write_to_buffer:

            self.__flag_write_to_buffer = False
            self.__buffer = {
                'title': clean_filename(self.__text_store.getvalue().strip()),
                'contents': [],
                'index': self.total_module_count + 1
            }
            self.__reset_text_store()

        elif the_tag == "a" and self.__flag_write_to_buffer:
            self.__flag_write_to_buffer = False
            self.__buffer_lesson_data['title'] = clean_filename(
                self.__text_store.getvalue().strip()
            )
            self.__buffer['contents'].append(
                    self.__buffer_lesson_data
            )
            self.__reset_text_store()

    def handle_data(self, data):
        if isinstance(data, binary_type):
            data = data.decode('utf8')
        if self.__flag_write_to_buffer:
            self.__text_store.write(data)

    def handle_end_of_doc(self):
        self.__update_parsed_data()
        self.__text_store.close()


class HLSParser(object):

    def __init__(self):
        self.__raw_data = None

    def feed(self, data):
        self.__raw_data = data
        self.__goahead()

    def handle_x_stream_inf(self, stream, metadata):
        pass

    def handle_x_key(self, attributes):
        pass

    def handle_extinf(self, stream):
        pass

    def extract_attribute_list(self, line):
        tag, attrs_raw = line.split(":", 1)
        attrs = {
            k: v for k, v in
            map(lambda x: x.split("="), attrs_raw.split(","))
        }
        return (tag, attrs)

    def __goahead(self):
        if len(self.__raw_data) > 0:
            detected_x_stream_inf = False
            detected_extinf = False
            splitted_data = self.__raw_data.split("\n")
            metadata = None

            for line in splitted_data:
                if detected_x_stream_inf:
                    self.handle_x_stream_inf(line, metadata)
                    detected_x_stream_inf = False

                elif line.startswith("#EXT-X-STREAM-INF:"):
                    metadata = self.extract_attribute_list(line)[1]
                    detected_x_stream_inf = True

                if detected_extinf:
                    self.handle_extinf(line)
                    detected_extinf = False

                elif line.startswith("#EXTINF:"):
                    detected_extinf = True

                if line.startswith("#EXT-X-KEY:"):
                    self.handle_x_key(self.extract_attribute_list(line)[1])


class PlaylistParser(HLSParser):

    def __init__(self):
        self.parsed_data = {}
        super(PlaylistParser, self).__init__()

    def handle_x_stream_inf(self, stream, metadata):
        self.parsed_data[metadata["RESOLUTION"].split("x")[1]] = stream


class ChunkListParser(HLSParser):

    def __init__(self):
        self.parsed_data = {
            "encryption": None,
            "uri": None,
            "iv": None,
            "chunks": []
        }
        super(ChunkListParser, self).__init__()

    def handle_extinf(self, stream):
        self.parsed_data['chunks'].append(stream)

    def handle_x_key(self, attributes):
        self.parsed_data["encryption"] = attributes.get('METHOD', None)
        uri = attributes.get('URI', None)
        if uri.startswith('"'):
            self.parsed_data["uri"] = uri[1:-1] if uri.startswith('"') else uri
        self.parsed_data["iv"] = attributes.get('IV', None)
