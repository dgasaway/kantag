#!/usr/bin/env python3

# applykan.py - kantag tool for inspecting audio file metadata.
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
import sys
import os
import argparse
import pprint
from kantag.util import expand_globs
from kantag.exceptions import TaggingError
from kantag import audiofile
from kantag._version import __version__

# --------------------------------------------------------------------------------------------------
def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(
        description='Outputs to STDOUT a list of tags in the source files.')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-v', '--verbose',
        help='verbose output',
        action='count', default=0)
    parser.add_argument('-f', '--filename-format',
        help='specify the advanced formatting expression used to format the filename',
        action='store', default='{0}')
    parser.add_argument('--file-trailer',
        help='specify a string printed after each file',
        action='store', default='')
    parser.add_argument('-t', '--tag-format',
        help='specify the advanced formatting expression used to format each tag',
        action='store', default='\t{0:30} = {1}')
    parser.add_argument('--no-sort',
        help='display tags in file order',
        action='store_false', dest='sort')
    parser.add_argument('-W', '--no-warn',
        help='disable all warnings',
        action='store_false', dest='warn')
    parser.add_argument('audio_files',
        help='audio files (Ogg Vorbis, Ogg Opus, FLAC, MP3, M4A)',
        action='store', metavar='audio_file', nargs='+')

    args = parser.parse_args()

    if args.verbose >= 1:
        print('<Arguments>')
        print(pprint.PrettyPrinter(indent=2).pformat(vars(args)) + '\n')

    # Expand any glob patterns left by the shell.
    args.audio_files = expand_globs(args.audio_files)

    # Write the output.
    try:
        for filename in args.audio_files:
            print(args.filename_format.format(filename))
            print_tags(filename, args)
            if args.file_trailer != '':
                print(args.file_trailer)

    except TaggingError as e:
        print('An exception occurred:\n' + ';'.join(e.args), file=sys.stderr)
        exit(2)

# --------------------------------------------------------------------------------------------------
def print_tags(filename, args):
    tags = audiofile.read_raw(filename, args.warn)
    if args.sort:
        tags.sort(key=lambda item: item.tag)
    for item in tags:
        print(args.tag_format.format(item.tag, item.value))

# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    #main(sys.argv[1:])
    main()
