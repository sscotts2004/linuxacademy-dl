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
from . import __version__, __title__
from .linux_academy import LinuxAcademy
from .exceptions import LinuxAcademyException
from .utils import sys_info
from datetime import datetime
from six.moves import input
import os
import sys
import getpass
import argparse
import logging

logger = logging.getLogger(__title__)


class CLI(object):

    LOG_FORMAT_CONSOLE = '%(levelname)-8s %(message)s'
    LOG_FORMAT_FILE = '%(asctime)s %(levelname)-8s %(message)s'
    LOG_DIR = os.path.join(
        os.path.expanduser('~'), 'linuxacademy-dl', 'log'
    )

    def __init__(self):
        self.argparser = self.argparser_init()

    def argparser_init(self):
        parser = argparse.ArgumentParser(
            description='Fetch all the lectures for a Linux Academy '
                        '(linuxacademy.com) course',
            prog=__title__
        )
        parser.add_argument(
            'link',
            help='Link for Linux Academy course',
            action='store'
        )
        parser.add_argument(
            '-u', '--username',
            help='Username / Email',
            default=None, action='store'
        )
        parser.add_argument(
            '-p', '--password',
            help='Password',
            default=None,
            action='store'
        )
        parser.add_argument(
            '-o', '--output',
            help='Output directory',
            default=None, action='store'
        )
        parser.add_argument(
            '--use-ffmpeg',
            help='Download videos from m3u8/hls with ffmpeg (Recommended)',
            action='store_const',
            const=True,
            default=False
        )
        parser.add_argument(
            '-q', '--video-quality',
            help='Select video quality [default is 1080]',
            default='1080',
            action='store',
            choices=['1080', '720', '480', '360']
        )
        parser.add_argument(
            '--debug',
            help='Enable debug mode',
            action='store_const',
            const=True,
            default=False
        )
        parser.add_argument(
            '-v', '--version',
            help='Display the version of %(prog)s and exit',
            action='version',
            version='%(prog)s {version}'.format(version=__version__)
        )
        return parser

    def get_debug_log_file_name(self):
        return "log_{}.log".format(
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )

    def get_debug_log_file_path(self):
        return os.path.join(
            self.LOG_DIR,
            self.get_debug_log_file_name()
        )

    def get_log_handler(self, error_level, formatter,
                        handler, handler_args={}):
        log_handler = handler(**handler_args)
        log_handler.setLevel(error_level)
        log_handler.setFormatter(
            logging.Formatter(formatter)
        )
        return log_handler

    def get_console_log_handler(self, error_level):
        return self.get_log_handler(
            error_level, self.LOG_FORMAT_CONSOLE,
            logging.StreamHandler
        )

    def get_file_log_handler(self, error_level, log_path):
        return self.get_log_handler(
            error_level, self.LOG_FORMAT_FILE,
            logging.FileHandler,
            {
             "filename": log_path,
             "mode": "w+"
            }
        )

    def init_logger(self, error_level=logging.INFO):
            logger.setLevel(logging.DEBUG)
            logger.addHandler(self.get_console_log_handler(error_level))

            if error_level == logging.DEBUG:
                try:
                    os.makedirs(self.LOG_DIR)
                except:
                    pass
                log_path = self.get_debug_log_file_path()
                logger.addHandler(
                    self.get_file_log_handler(error_level, log_path)
                )
                logger.info('Debug log file created at {}'.format(log_path))

    def _generate_sys_info_log(self, sys_info):
        logger.debug('Python: {}'.format(sys_info['python']))
        logger.debug('Platform: {}'.format(sys_info['platform']))
        logger.debug('OS: {}'.format(sys_info['os']))

    def main(self):
        args = vars(self.argparser.parse_args())

        username = args['username']
        password = args['password']
        debug = args['debug']

        output_folder = os.path.abspath(
            os.path.expanduser(args['output']) if args['output'] else ''
        )

        sys_information = sys_info()

        if not username:
            username = input("Username / Email : ")

        if not password:
            password = getpass.getpass()

        if debug:
            self.init_logger(error_level=logging.DEBUG)
            self._generate_sys_info_log(sys_information)
        else:
            self.init_logger()

        try:
            with LinuxAcademy(
                args['link'], username, password,
                output_folder, args['use_ffmpeg'], args['video_quality']
            ) as la:
                la.analyze()
                la.download()
        except LinuxAcademyException as lae:
            logger.error(lae.args[0])

        except KeyboardInterrupt:
            logger.error("User interrupted the process, exiting...")
        except Exception as e:
            logger.error('Unknown Exception')
            logger.exception(e)
            logger.info(
                'Please report this issue on '
                'https://github.com/vassim/linuxacademy-dl/issues. '
                'Make sure you are using the latest version. '
                'Be sure to call linuxacademy-dl with the --debug flag and '
                'include its complete output.'
            )
        finally:
            sys.exit(1)
