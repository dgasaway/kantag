#!/usr/bin/env python3

# applykan.py - kantag tool for writing text metadata to audio files.
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
import io
import codecs
import os
import re
import pprint
from argparse import ArgumentParser
from pathlib import Path
from kantag import util
from kantag.tagfile import TagFileBuilder
from kantag.util import ToggleAction
from kantag.exceptions import TaggingError
from kantag import audiofile
from kantag._version import __version__

"""
Set of tag names that will generate a warning if any given file does not contain at least one tag
by that name.
"""
_minimal_tags = {
    'AlbumArtist', 'AlbumArtistSort', 'AlbumArtists', 'AlbumArtistsSort', 'Artist', 'ArtistSort',
    'Date', 'LabelId', 'Title', 'Performer', 'PerformerSort', 'TrackNumber', 'Genre',
    'musicbrainz_albumartistid', 'musicbrainz_albumid', 'musicbrainz_artistid',
    'musicbrainz_trackid',
    'replaygain_album_peak', 'replaygain_album_gain',
    'replaygain_track_peak', 'replaygain_track_gain'
    }

"""
Set of tag names that will generate a warning in single file mode if any given file does not contain
at least one tag by that name.
"""
_single_file_minimal_tags = {
    'Artist', 'ArtistSort', 'Date', 'Title', 'Performer', 'PerformerSort', 'Genre',
    'musicbrainz_artistid', 'musicbrainz_trackid',
    'replaygain_track_peak', 'replaygain_track_gain'
    }

"""
Map where sort names are stored in regular artist tags, and no non-sort names are stored.  For
example, ARTIST=Beatles, The; ARTISTSORT=<undefined>.
"""
_sort_names_only_map = {
    'AlbumArtistSort': 'AlbumArtist',
    'ArrangerSort'   : 'Arranger',
    'ArtistSort'     : 'Artist',
    'ComposerSort'   : 'Composer',
    'ConductorSort'  : 'Conductor',
    'LyricistSort'   : 'Lyricist',
    'PerformerSort'  : 'Performer',
    'WriterSort'     : 'Writer',
    'AlbumArtist'    : None,
    'Arranger'       : None,
    'Artist'         : None,
    'Composer'       : None,
    'Lyricist'       : None,
    'Performer'      : None,
    'Writer'         : None
    }

"""
Map where sort names are stored in regular artist tags, and non-sort names are stored in special
'nonsort' tags.  For example, ARTIST=Beatles, The; ARTISTNONSORT=The Beatles.
"""
_sort_and_nonsort_names_map = {
    'AlbumArtistSort': 'AlbumArtist',
    'ArrangerSort'   : 'Arranger',
    'ArtistSort'     : 'Artist',
    'ComposerSort'   : 'Composer',
    'ConductorSort'  : 'Conductor',
    'LyricistSort'   : 'Lyricist',
    'PerformerSort'  : 'Performer',
    'WriterSort'     : 'Writer',
    'AlbumArtist'    : 'AlbumAristNonSort',
    'Arranger'       : 'ArrangerNonSort',
    'Artist'         : 'ArtistNonSort',
    'Composer'       : 'ComposerNonSort',
    'Lyricist'       : 'LyricistNonSort',
    'Performer'      : 'PerformerNonSort',
    'Writer'         : 'WriterNonSort'
    }

# --------------------------------------------------------------------------------------------------
def main():
    """
    Parse the command line arguments and initiate main operation.
    """
    args = parse_args()
    if args.verbose >= 3:
        print('<Arguments>')
        print(pprint.PrettyPrinter(indent=2).pformat(vars(args)) + '\n')

    try:
        process_files(args)
    except TaggingError as e:
        print('An exception occurred:\n' + ';'.join(e.args), file=sys.stderr)
        exit(2)

# --------------------------------------------------------------------------------------------------
def parse_args():
    """
    Parse and return the command line arguments.
    """
    parser = ArgumentParser(
        description='Reads the tag_file and applies the tags to the audio ' +
        '(Ogg Vorbis, Ogg Opus, FLAC, MP3, or M4A) files.')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-v', '--verbose',
        help='verbose output (can be specified up to three times)',
        action='count', default=0)
    parser.add_argument('-p', '--pretend',
        help='do not modify the audio files',
        action='store_true', default=False)
    parser.add_argument('-1', '--single-file',
        help='enable single file mode that does not require a track number',
        action='store_true', default=False)
    parser.add_argument('-P', '--path-regex',
        help='the regular expression used to determine disc and tracknumer from the '
        'path/filename; the expression may contain named groups <disc> and <track>; the default '
        'expression parses a filename in the form "<disc><track> - title.ext", where <track> must '
        'be two digits and <disc> may be zero or more digits',
        metavar='EXPRESSION', action='store', type=str, default=disc_track_regex())
    parser.add_argument('tag_file',
        help='kantag tag definition file, or "-" for STDIN',
        action='store')
    parser.add_argument('audio_files',
        help='audio files (Ogg Vorbis, Ogg Opus, FLAC, MP3, M4A); if not provided, writes the '
        'tags to the supported audio files in the folder containing `tag_file`',
        action='store', metavar='audio_file', nargs='*')

    group = parser.add_argument_group(title='tag edit arguments')
    group.add_argument('-w', '--work-title',
        help='build a Title from Work and Part tags [default=y]',
        action=ToggleAction, dest='work_title', choices=['y', 'n'], default=True)

    group = parser.add_argument_group(title='sort name handling arguments')
    exgroup = group.add_mutually_exclusive_group()
    exgroup.add_argument('--preserve-names',
        help='preserve artist name tags as they appear in the tag file (default)',
        action='store_const', dest='sort_map', const=None, default=None)
    exgroup.add_argument('--sort-names-only',
        help='store artist sort-names in regular name tags, discard unsorted names',
        action='store_const', dest='sort_map', const=_sort_names_only_map)
    exgroup.add_argument('--nonsort-names',
        help='store artist sort-names in regular name tags, unsorted names in NONSORT tags',
        action='store_const', dest='sort_map', const=_sort_and_nonsort_names_map)

    group = parser.add_argument_group(title='warning display arguments')
    group.add_argument('-W', '--disable-warnings',
        help='disable all warnings',
        action='store_false', dest='warn', default=True)
    group.add_argument('-u', '--disable-unrecognized-warning',
        help='disable warnings about unrecognized tags in the tag file',
        action='store_false', dest='warn_unrecognized', default=True)
    group.add_argument('-U', '--disable-unused-warning',
        help='disable warnings about unused lines from the tag file',
        action='store_false', dest='warn_unused', default=True)

    args = parser.parse_args()

    # Check for tags to read.
    if args.tag_file == '-':
        sys.stdin.reconfigure(encoding='utf-8')
    elif os.path.isfile(args.tag_file):
        args.tag_file = Path(args.tag_file)
    else:
        parser.error('tag file not found: ' + args.tag_file)

    # By default, tags are applied to all supported audio files in the directory containing the
    # tags file.  Otherwise, files must be provided.  However, in some cases, e.g., globs may not
    # have been expanded by the shell.  In the end, args.audio_files will have pathlib objects.
    if len(args.audio_files) > 0:
        args.audio_files = util.expand_globs(args.audio_files)
    elif args.tag_file != '-':
        args.audio_files = util.get_supported_audio_files(args.tag_file.parent)

    # If we still don't have audio files, there's nothing to do.
    if (len(args.audio_files) == 0):
        parser.error('no matching audio files found')

    return args

# --------------------------------------------------------------------------------------------------
def disc_track_regex():
    """
    Return a regex to determine disc/track number from path/filename.
    """
    regex = r'/(?P<disc>\d*)(?P<track>\d\d) - [^/]+$'
    return regex.replace('/', re.escape(os.sep))

# --------------------------------------------------------------------------------------------------
def build_work_part_title(tags):
    """
    Build a title tag from work and part information.
    """
    title = ''
    if 'Work' in tags:
        title = title + ' / '.join(tags['Work'])
        if 'Part' in tags:
            title = title + ': '
    if 'Part' in tags:
        title = title + ' / '.join(tags['Part'])
    return title

# --------------------------------------------------------------------------------------------------
def write_tags_to_file(tags, filename, args):
    """
    Write a TagSet to an audio file.
    """
    # Display tags
    if args.verbose == 2:
        for tag, lst in tags.items():
            for value in lst:
                print('\t' + tag + '=' + value)
    elif args.verbose >= 3:
        print(pprint.PrettyPrinter(indent=2).pformat(tags))

    # Write the tags to file.
    if not args.pretend:
        audiofile.write(filename, tags)

# --------------------------------------------------------------------------------------------------
def get_disc_track(regex, path):
    """
    Use a regular expression to get the disc and track number of a file based on path/filename.  The
    result is a tuple of (discnum, tracknum).
    """
    # Use path and regex to get the disc/track number of the file.
    discnum = None
    tracknum = None
    match = re.search(regex, path)
    if match:
        parts = match.groupdict()
        discnum = parts['disc'] if 'disc' in parts and parts['disc'].isdigit() else None
        tracknum = parts['track'] if 'track' in parts and parts['track'].isdigit() else None

    return (discnum, tracknum)

# --------------------------------------------------------------------------------------------------
def process_file(tagf, filename, args):
    """
    Write matching tags from a TagFile to an audiofile, where matching is based on disc/track number
    from the filename, while also looking for certain inconsistencies that suggest issues with the
    tag file.
    """
    if args.verbose >= 1:
        print(filename)

    # Use path and regex to get the disc/track number of the file.
    path = os.path.abspath(filename)
    (discnum, tracknum) = get_disc_track(args.path_regex, path)
    if args.warn and tracknum is None and not args.single_file:
        print('warning: unable to determine track number from filename; file will be skipped',
            file=sys.stderr)
        return

    # Get the tags that apply to the file.
    tags = tagf.get_matching(discnum, tracknum)

    # Add a track number tag.
    if tracknum is not None and 'TrackNumber' not in tags:
        tags.append('TrackNumber', tracknum.zfill(2))

    # Add a title tag from work and part info if no title present.
    if args.work_title and 'Title' not in tags and ('Work' in tags or 'Part' in tags):
        tags.append('Title', build_work_part_title(tags))

    # Check for essential tags.
    if args.warn:
        # Use a set difference to find the missing tags.
        if args.single_file:
            missing_tags = _single_file_minimal_tags - set(tags.keys())
        else:
            missing_tags = _minimal_tags - set(tags.keys())
        if len(missing_tags) > 0:
            print('warning: file missing minimal tags: ' + ', '.join(missing_tags),
                file=sys.stderr)

    # Check for other irregularities.
    if args.warn:
        if 'Work' in tags and not 'Composer' in tags:
            print('warning: work without composer', file=sys.stderr)

    # Finalize.
    write_tags_to_file(tags, filename, args)

# --------------------------------------------------------------------------------------------------
def process_files(args):
    """
    Write tags from the tags file to the selected files.  When all have been written, look for tags
    in the file that were not used (usually a sign of a tag file issue).
    """
    if args.tag_file == '-':
        reader = sys.stdin
    else:
        reader = io.open(args.tag_file, mode='rt', encoding='utf-8')

    # Note that we work on a TagFile object rather than translating to a more structured TagStore
    # so that we preserve the ordering presented in the kantag file.
    tagf = TagFileBuilder(reader=reader, warn=args.warn and args.warn_unrecognized).tags

    if args.verbose >= 3:
        print('<TagFile>')
        print(tagf.pprint(True))

    if args.sort_map is not None:
        tagf.apply_map(args.sort_map)

    for filename in args.audio_files:
        process_file(tagf, filename, args)

    # Search and warn about unused tag lines.
    if args.warn and args.warn_unused:
        for source_line in [line.source_line for line in tagf.lines if not line.used]:
            print('warning: unused tag line:', file=sys.stderr)
            print(source_line, file=sys.stderr)

# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    #main(sys.argv[1:])
    main()
