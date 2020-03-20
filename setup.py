from __future__ import with_statement, print_function, unicode_literals
from setuptools import setup
from linuxacademy_dl import __title__, __version__,\
        __author__, __email__, __license__
import subprocess
import tempfile


try:
    with tempfile.NamedTemporaryFile('w+') as rst_file:
        subprocess.call(
            [
             "pandoc", "README.md", "-f", "markdown", "-t", "rst",
             "-o", rst_file.name
            ]
        )
        rst_file.seek(0)
        long_description = rst_file.read()
except OSError:
    print('Pandoc not installed!!')
    long_description = open('README.md', 'r').read()


setup(
    name=__title__,
    version=__version__,

    description='Download videos from Linux Academy (linuxacademy.com)'
                ' for personal offline use',
    long_description=long_description,

    author=__author__,
    author_email=__email__,
    url='https://github.com/vassim/{}'.format(__title__),
    license=__license__,

    packages=['linuxacademy_dl'],
    install_requires=map(
        lambda x: x.strip(),
        open('requirements.txt', 'r').readlines()
    ),
    entry_points={
        'console_scripts': [
            '{}=linuxacademy_dl.__main__:main'.format(__title__)
        ]
    },
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'Environment :: Console',
        u'Intended Audience :: Developers',
        u'License :: OSI Approved :: BSD License',
        u'Operating System :: OS Independent',
        u'Programming Language :: Python',
        u'Programming Language :: Python :: 2',
        u'Programming Language :: Python :: 2.7',
        u'Programming Language :: Python :: 3',
        u'Programming Language :: Python :: 3.5',
        u'Topic :: Terminals',
        u'Topic :: Utilities',
        u'Topic :: Multimedia :: Video'
    ],
)
