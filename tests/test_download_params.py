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
from linuxacademy_dl.linux_academy import DownloadParams
from linuxacademy_dl.exceptions import LinuxAcademyException
import pytest


@pytest.fixture
def download_params(mocker):
    with mocker.patch('linuxacademy_dl.linux_academy.DownloadParams.__init__',
                      return_value=None):
        return DownloadParams()


@pytest.mark.parametrize("video_quality", ['1080', '720', '480', '360'])
def test_dp_video_quality(download_params, video_quality):
    download_params.video_quality = video_quality
    assert download_params.video_quality == video_quality


@pytest.mark.parametrize("video_quality", ['640', 720, None, '', {}, 'Blah'])
def test_dp_video_quality_invalid(download_params, video_quality):
    with pytest.raises(LinuxAcademyException):
        download_params.video_quality = video_quality


def test_dp_output_dir(mocker, download_params):
    with mocker.patch('os.path.exists', return_value=True),\
            mocker.patch('os.access', return_value=True):
        download_params.output_dir = 'blah'
        assert download_params.output_dir == 'blah'


@pytest.mark.parametrize("path,access", [
    (True, False),
    (False, True),
    (False, False),
])
def test_dp_output_dir_invalid(mocker, download_params, path, access):
    with mocker.patch('os.path.exists', return_value=path),\
            mocker.patch('os.access', return_value=access):
        with pytest.raises(LinuxAcademyException):
            download_params.output_dir = 'blah'


def test_dp_checking_ffmpeg(mocker, download_params):
    with mocker.patch('linuxacademy_dl.linux_academy.find_executable',
                      return_value=None):
            with pytest.raises(LinuxAcademyException):
                download_params.use_ffmpeg = True
