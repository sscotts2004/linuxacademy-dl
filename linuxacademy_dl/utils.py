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

from __future__ import unicode_literals, print_function, absolute_import
import re
import platform
import sys


def clean_filename(name, replacer=''):
    return re.sub('[\'\"<>:\\\/|?*]', replacer, name)


def clean_html(data):
    """
     cleaning the data by removing all new-line characters
     and unwanted white-spaces
    """
    return ' '.join(data.replace("\n", "").split())


def sys_info():
    result = {
        'platform': '{} [{}]'.format(platform.platform(), platform.version()),
        'python': '{} {}'.format(
            platform.python_implementation(),
            sys.version.replace('\n', '')
        ),
        'os': 'Unknown'
    }

    linux_ver = platform.linux_distribution()
    mac_ver = platform.mac_ver()
    win_ver = platform.win32_ver()

    if linux_ver[0]:
        result['os'] = 'Linux - {}'.format(' '.join(linux_ver))
    elif mac_ver[0]:
        result['os'] = 'OS X - {}'.format(' '.join(mac_ver[::2]))
    elif win_ver[0]:
        result['os'] = 'Windows - {}'.format(' '.join(win_ver[:2]))

    return result
