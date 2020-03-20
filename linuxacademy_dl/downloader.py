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

from __future__ import unicode_literals, print_function, with_statement
from . import __title__
from ._session import session
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from .hls_decrypt import HLSDecryptAES128
from six import BytesIO
from contextlib import closing
import sys
import os
import subprocess
import multiprocessing
import tempfile
import logging

logger = logging.getLogger(__title__)


class DownloadEngine(object):

    POOL_SIZE = multiprocessing.cpu_count() * 2

    def __init__(self, use_ffmpeg=True, skip_existing=True):
        self.use_ffmpeg = use_ffmpeg
        self.skip_existing = skip_existing
        self.session = FuturesSession(
            executor=ThreadPoolExecutor(max_workers=self.POOL_SIZE),
            session=session
        )

    def hls_download(self, hls_data, save_as):
        try:
            contents = [
                self.session.get(
                    url, background_callback=lambda s, r: r.close()
                )
                for url in hls_data['data']
            ]

            ts_accumulator = tempfile.NamedTemporaryFile() \
                if self.use_ffmpeg \
                else open(save_as, "wb")

            for idx, content in enumerate(contents, 0):
                chunk_resp = content.result()
                chunk = chunk_resp.content

                logger.debug(
                    'Fetched chunk_resp #{} ({}/{})'.format(
                        idx, chunk_resp.headers['Content-Length'], len(chunk)
                    )
                )

                if hls_data.get('encryption'):
                    iv = hls_data.get('iv', idx)
                    key = session.get(hls_data.get('key_uri')).content
                    with closing(BytesIO(chunk)) as fp:
                        with HLSDecryptAES128(
                                    fp, key, iv
                                ).decrypt() as dec_itm:
                            ts_accumulator.write(dec_itm.read())
                else:
                    ts_accumulator.write(chunk)

            if self.use_ffmpeg:
                self.ffmpeg_process(ts_accumulator.name, save_as)

        except OSError as exc:
            logger.critical('Failed to download: %s', exc)

        finally:
            ts_accumulator.close()

    def safe_process_download_path(self, save_path, file_name, make_dirs=True):
        sys_encoding = sys.getdefaultencoding()

        d, f = map(
            lambda x: x.encode(sys_encoding, 'ignore').decode('utf-8'),
            (save_path, file_name)
        ) if sys_encoding != 'utf-8' else (save_path, file_name)

        if make_dirs:
            try:
                os.makedirs(d)
            except:
                pass

        return os.path.join(d, f)

    def __call__(self, download_info, save_to):

        final_path = self.safe_process_download_path(
            save_to, download_info['save_resource_as']
        )

        if self.skip_existing and os.path.exists(final_path):
            logger.info("Skipping already existing file {}".format(final_path))
        else:
            logger.info("Downloading {}".format(final_path))
            self.hls_download(download_info, final_path)
            logger.info("Downloaded {}".format(final_path))

    def ffmpeg_process(self, input_file_name, output_file_name):
        command = [
            'ffmpeg',
            '-loglevel', 'fatal',
            '-i', input_file_name,
            '-y',
            '-bsf:a', 'aac_adtstoasc',
            '-vcodec', 'copy',
            '-c', 'copy',
            '-crf', '50',
            '-f', 'mp4', output_file_name
        ]
        logger.debug('Executing FFMPEG Command "{}"'.format(' '.join(command)))
        subprocess.call(command)
