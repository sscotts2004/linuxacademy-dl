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

from __future__ import with_statement,  unicode_literals
from linuxacademy_dl.parsers import SyllabusParser, \
            PlaylistParser, ChunkListParser
import os
import pickle
import pytest


DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')


@pytest.mark.parametrize(("ip_file_path", "op_file_path", "parser_obj"), [
    (
     os.path.join(DATA_PATH, 'syllabus_response'),
     os.path.join(DATA_PATH, 'syllabus_parsed'),
     SyllabusParser()
    ),
    (
     os.path.join(DATA_PATH, 'playlist_m3u8_response'),
     os.path.join(DATA_PATH, 'playlist_m3u8_parsed'),
     PlaylistParser()
    ),
    (
     os.path.join(DATA_PATH, 'chunklist_b2000000_m3u8_response'),
     os.path.join(DATA_PATH, 'chunklist_b2000000_m3u8_parsed'),
     ChunkListParser()
    ),
    (
     os.path.join(DATA_PATH, 'chunklist_b800000_m3u8_response'),
     os.path.join(DATA_PATH, 'chunklist_b800000_m3u8_parsed'),
     ChunkListParser()
    ),
])
def test_parser(ip_file_path, op_file_path, parser_obj):
    with open(ip_file_path, 'rb') as in_data_raw, \
            open(op_file_path, 'rb') as out_data_pickled:

        in_data = in_data_raw.read().decode('utf-8')
        parser_obj.feed(in_data)
        out_data = pickle.load(out_data_pickled)

    assert parser_obj.parsed_data == out_data
