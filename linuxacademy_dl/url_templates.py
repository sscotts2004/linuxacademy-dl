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
from string import Template
from six import text_type
from six.moves.urllib.parse import urljoin


BASE_URL = 'https://linuxacademy.com'

USER_AGENT = 'Mozilla/5.0 ' \
            '(X11; Ubuntu; Linux x86_64; rv:50.0) ' \
            'Gecko/20100101 Firefox/50.0'

LOGIN_URL = {
    'url': urljoin(BASE_URL, '/cp/login'),
    'method': 'POST',
    'headers': {
        'Referer': urljoin(BASE_URL, '/cp/login')
    },
    "allow_redirects": False,
    'data': {
        'username': None,
        'password': None,
        'request_uri': '/cp/login',
        'submit': 1
    }
}

LOGOUT_URL = {
    'url': urljoin(BASE_URL, 'cp/login/quit'),
    'method': 'GET',
    'headers': {
        'Referer': urljoin(BASE_URL, '/cp/login')
    },
    "allow_redirects": False
}

COURSE_URL = {
    'url': urljoin(BASE_URL, '/cp/modules/view/id/$course_id')
}

COURSE_LIST = {
    'url': urljoin(BASE_URL, '/cp/socialize/course_module_search'),
    'method': 'GET',
    'headers': {
        'Referer': urljoin(BASE_URL, '/cp/login'),
        'X-Requested-With': 'XMLHttpRequest'
    }
}

COURSE_SYLLABUS = {
    'url': urljoin(BASE_URL, '/cp/modules/syllabus/id/$course_id'),
    'method': 'GET',
    'headers': {
        'Referer': urljoin(BASE_URL, '/cp/modules/view/id/$course_id'),
        'X-Requested-With': 'XMLHttpRequest'
    }
}


def render_url(session, url_template,
               template_params={"base_url": BASE_URL}, payload={}):
    def render(source):
        for k, v in source.items():
            if isinstance(v, dict):
                render(v)
            elif isinstance(v, text_type):
                source[k] = Template(v).safe_substitute(template_params)
            elif v is None:
                source[k] = payload.get(k, None)
        return source
    return getattr(session, 'request')(**render(dict(url_template)))
