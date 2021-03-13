# setup.py - kantag setup configuration.
# Copyright (C) 2018 David Gasaway
# https://github.com/dgasaway/kantag

# This program is free software; you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program; if not,
# see <http://www.gnu.org/licenses>.
from setuptools import setup, find_packages
import os
import io
from kantag._version import __version__

# Read the long description from the README.
basedir = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(basedir, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='kantag',
    version=__version__,
    description='Manage audio file metadata using external text files.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='David Gasaway',
    author_email='dave@gasaway.org',
    url='https://github.com/dgasaway/kantag',
    download_url='https://github.com/dgasaway/kantag/releases',
    license='GNU GPL v2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'applykan = kantag.applykan:main',
            'initkan = kantag.initkan:main',
            'showkan = kantag.showkan:main',
        ],
    },
    python_requires='~=3.7',
    install_requires=[
        'mutagen >= 1.40',
    ],
    extras_require={
        'MusicBrainz': ['musicbrainzngs >= 0.6'],
    },
    keywords='audio music metadata tags',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
    ],
)
