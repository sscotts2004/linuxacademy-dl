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

from __future__ import unicode_literals, absolute_import, \
                    print_function, with_statement
from Crypto.Cipher import AES
from tempfile import SpooledTemporaryFile
from six import PY2, string_types, int2byte
from .exceptions import HLSDecryptException


class HLSDecryptAES128(object):

    POOL_SIZE = 1024 * 1024 * 5  # 5MB

    def __init__(self, chunk_stream, key, iv):
        self.chunk_stream = chunk_stream
        self.key = key
        self.iv = self.iv_from_int(
            int(iv, 16) if isinstance(iv, string_types) else iv
        )

    @property
    def chunk_stream(self):
        return self.__chunk_stream

    @chunk_stream.setter
    def chunk_stream(self, val):
        if hasattr(val, 'read'):
            try:
                val.seek(0)
            except:
                pass
            self.__chunk_stream = val
        else:
            raise HLSDecryptException(
                'chunk_stream must be a '
                'file like object or an HTTP response'
            )

    def iv_from_int(self, int_iv):
        return b''.join([int2byte((int_iv >> (i * 8)) & 0xFF)
                         for i in range(AES.block_size)[::-1]])

    def pkcs7_reverse_padded_chunk(self, chunk):
        # in PY2 type(chunk[-1]) == <str>
        if PY2:
            padding_length = ord(chunk[-1])
        else:
            padding_length = chunk[-1]

        return chunk[:-padding_length]

    def decrypt(self):
        decrypted_chunk = SpooledTemporaryFile(
            max_size=self.POOL_SIZE,
            mode='wb+'
        )
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)

        next_chunk = ''
        finished = False

        while not finished:
            chunk, next_chunk = next_chunk, \
                self.chunk_stream.read(1024 * AES.block_size)

            chunk = cipher.decrypt(chunk)

            if len(next_chunk) == 0:
                chunk = self.pkcs7_reverse_padded_chunk(chunk)
                finished = True
            if chunk:
                decrypted_chunk.write(chunk)

        decrypted_chunk.seek(0)
        return decrypted_chunk
