#!/usr/bin/env python3

# initkan.py - kantag tool for generation of text metadata.
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
import io
import glob
import pprint
import re
import argparse
import importlib.util
from argparse import ArgumentParser
from kantag.util import ToggleAction, expand_globs
from kantag.exceptions import TaggingError
from kantag._version import __version__
from kantag.tagfile import TagFileBuilder
from kantag.tagstores import Release, Disc, Track, ReleaseBuilder

# Lists of initkan supported tags.
_release_tags = frozenset([
    'Album', 'AlbumArtist', 'AlbumArtistSort', 'AlbumArtists', 'AlbumArtistsSort', 'Arranger',
    'ArrangerSort', 'Artist', 'ArtistSort', 'ASIN', 'Barcode', 'CatalogNumber', 'Comment',
    'Composer', 'ComposerSort',  'Conductor', 'ConductorSort', 'Date', 'Genre', 'LabelId',
    'Lyricist', 'LyricistSort', 'OriginalDate', 'Part', 'Performer', 'PerformerSort',
    'Title', 'Version', 'Writer', 'Work', 'WriterSort',
    ])
_disc_tags = frozenset([
    'AlbumArtist', 'AlbumArtistSort', 'AlbumArtists', 'AlbumArtistsSort', 'Arranger',
    'ArrangerSort', 'Artist', 'ArtistSort', 'Comment', 'Composer', 'ComposerSort',
    'Conductor', 'ConductorSort', 'CoverNumber', 'Date', 'DiscNumber', 'DiscSubtitle',
    'Genre', 'Lyricist', 'LyricistSort', 'OriginalDate', 'Part', 'Performer',
    'PerformerSort', 'Title', 'Version', 'Work', 'Writer', 'WriterSort'
    ])
_track_tags = frozenset([
    'Arranger', 'ArrangerSort', 'Artist', 'ArtistSort', 'Artists', 'ArtistsSort', 'Comment',
    'Composer', 'ComposerSort', 'Conductor', 'ConductorSort', 'CoverNumber', 'Genre',
    'Lyricist', 'LyricistSort', 'Part', 'Performer', 'PerformerSort', 'Title', 'TrackNumber',
    'Version', 'Work', 'Writer', 'WriterSort'
    ])
_musicbrainz_tags = [
    'musicbrainz_albumid', 'musicbrainz_albumartistid', 'musicbrainz_artistid',
    'musicbrainz_discid', 'musicbrainz_releasegroupid', 'musicbrainz_releasetrackid',
    'musicbrainz_trackid', 'musicbrainz_workid', 'acoustid_id'
    ]
_replaygain_tags = [
    'replaygain_album_peak', 'replaygain_album_gain', 'replaygain_track_peak',
    'replaygain_track_gain'
    ]

# --------------------------------------------------------------------------------------------------
def main():
    """
    Parse command line argument and initiate main operation.
    """
    # Parse the command line arguments.
    parser = ArgumentParser(
        description='Outputs to STDOUT a tag defintion file based on tags in the source files, the '
        'current path, the filenames passed, and calls to the MusicBrainz service.')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-v', '--verbose',
        help='verbose output (can be specified up to two times)',
        action='count', default=0)
    parser.add_argument('-o', '--output',
        help='output file, or "-" for STDOUT (default=STDOUT)',
        action='store', default='-')
    parser.add_argument('-W', '--disable-warnings',
        help='disable all warnings',
        action='store_false', dest='warn', default=True)
    parser.add_argument('audio_files',
        help='audio files (Ogg Vorbis, Ogg Opus, FLAC, MP3, M4A)',
        action='store', metavar='audio_file', nargs='+')

    group = parser.add_argument_group(title='tag edit arguments')
    group.add_argument('-p', '--infer-from-path',
        help='use path and filename to fill gaps in metadata',
        action='store_true')
    group.add_argument('-P', '--path-regex',
        help='the regular expression used by --infer-from-path to parse metadata from path; '
        'the expression may contain named groups <artist>, <album>, <date>, <disc>, <track>, '
        'and <title>; the default expression parses a path in the form '
        '"<artist>/<album>/<disc><track> - <title>.ext", where <track> must be two digits and '
        '<disc> may be zero or more digits',
        metavar='EXPRESSION', action='store', type=str, default=path_parts_regex())
    group.add_argument('-V', '--various-artists',
        help='string to use as artist for various-artist releases [default="Various"]',
        action='store', dest='various', default='Various')
    group.add_argument('-t', '--parse-title',
        help='parse Work and/or Part from Title [default=y]',
        action=ToggleAction, choices=['y', 'n'], default=True)
    group.add_argument('-d', '--parse-disc',
        help='parse DiscNumber and/or DiscSubtitle from Album [default=n]',
        action=ToggleAction, choices=['y', 'n'], default=False)
    group.add_argument('-i', '--remove-instruments',
        help='remove instrument information from Performer tags [default=y]',
        action=ToggleAction, choices=['y', 'n'], default=True)
    group.add_argument('-c', '--classical',
        help='enable additional edits for classical releases [default=n]',
        action=ToggleAction, choices=['y', 'n'], default=False)
    group.add_argument('-M', '--call-musicbrainz',
        help='enable calls to the musicbrainz web service [default=n]',
        action=ToggleAction, choices=['y', 'n'], default=False)
    parser.add_argument('-1', '--single-file',
        help='enable single file mode that does not generate tags that only apply to albums',
        action='store_true', default=False)
    group.add_argument('--release-mbid',
        help='unique id of the release to lookup in the musicbrainz database; optional if an id is '
        'present in the existing tags, but given preference over a tag value',
        metavar="MBID", action='store', type=str)
    group.add_argument('--locale',
        help='artist alias locale to use for musicbrainz data [default=en]',
        action='store', type=str, default='en')
    group.add_argument('-A', '--ascii-punctuation',
        help='replace non-ascii punctuation in titles with ascii equivalents [default=y]',
        action=ToggleAction, choices=['y', 'n'], default=True)
    # Keep common/shared tags from removal from lower levels.  WILL BREAK some assumptions and make
    # a mess of the output.  DEBUG USE ONLY.
    group.add_argument('--keep-common',
        help=argparse.SUPPRESS,
        action=ToggleAction, choices=['y', 'n'], default=False)

    group = parser.add_argument_group(title='output format arguments')
    group.add_argument('-S', '--structured',
        help='output in structured format (default)',
        action='store_true', default=True)
    group.add_argument('-U', '--unstructured',
        help='output in unstructured format',
        action='store_false', dest='structured', default=True)

    group = parser.add_argument_group(title='structured output arguments')
    group.add_argument('-s', '--standard',
        help='output standard (non-replaygain and non-musicbrainz) tags [default=y]',
        action=ToggleAction, choices=['y', 'n'], default=True)
    group.add_argument('-m', '--musicbrainz',
        help='output musicbrainz identifiers [default=y]',
        action=ToggleAction, choices=['y', 'n'], default=True)
    group.add_argument('-r', '--replaygain',
        help='output replaygain tags [default=y]',
        action=ToggleAction, choices=['y', 'n'], default=True)
    group.add_argument('-a', '--artist-block',
        help='output artists in blocks before track list [default=y]',
        action=ToggleAction, choices=['y', 'n'], default=True)
    group.add_argument('-b', '--break-tracks',
        help='add a line break between tracks [default=n]',
        action=ToggleAction, choices=['y', 'n'], default=False)
    group.add_argument('-w', '--work-block',
        help='output works in a block before the track list [default=n]',
        action=ToggleAction, choices=['y', 'n'], default=False)
    group.add_argument('--track-artists',
        help='output multi-artist Arists tags for tracks [default=n]',
        action=ToggleAction, choices=['y', 'n'], default=False)
    group.add_argument('-u', '--output-unsupported',
        help='output tags that are not explicitly supported [default=n]',
        action=ToggleAction, choices=['y', 'n'], default=False)

    parser.set_defaults(keep_common=False)
    global args
    args = parser.parse_args()
    if args.verbose >= 2:
        print('<Arguments>', file=sys.stderr)
        print(pprint.PrettyPrinter(indent=2).pformat(vars(args)) + '\n', file=sys.stderr)

    # Check for presence of musicbrainsngs.
    if args.call_musicbrainz == True:
        if importlib.util.find_spec('musicbrainzngs') is None:
            parser.error("musicbrainzngs package must be installed to use '--call-musicbrainz'")
        
    # Expand any glob patterns left by the shell.
    args.audio_files = expand_globs(args.audio_files)
    if (len(args.audio_files) == 0):
        parser.error('no matching audio files found')

    # Write the output.
    try:
        process_files()
    except TaggingError as e:
        print('An exception occurred:\n' + ';'.join(e.args), file=sys.stderr)
        exit(2)

# --------------------------------------------------------------------------------------------------
def path_parts_regex():
    """
    Return a regex usable to get metadata from path/filename.
    """
    regex = \
        r'/(?P<artist>[^/]+)' \
        r'/(?P<album>[^/]+)' \
        r'/(?P<disc>\d*)(?P<track>\d\d) - (?P<title>[^/]+)' + \
        r'\.[^/]+$'
    return regex.replace('/', re.escape(os.sep))

# --------------------------------------------------------------------------------------------------
def add_artists(builder, entity, parent=None):
    """
    Add artist tags from a tagstore to a TagFileBuilder.
    """
    builder.add_values(entity, 'Artist', parent)
    builder.add_values(entity, 'ArtistSort', parent)
    if args.track_artists:
        if 'Artists' in entity.tags:
            builder.add_values(entity, 'Artists', parent)
        else:
            builder.add_values_as(entity, 'Artist', 'Artists', parent)
        if 'ArtistsSort' in entity.tags:
            builder.add_values(entity, 'ArtistsSort', parent)
        else:
            builder.add_values_as(entity, 'ArtistSort', 'ArtistsSort', parent)

# --------------------------------------------------------------------------------------------------
def add_composers(builder, entity, parent=None):
    """
    Add composer/songwriter tags from a tagstore to a TagFileBuilder.
    """
    builder.add_values(entity, 'Composer', parent)
    builder.add_values(entity, 'ComposerSort', parent)
    builder.add_values(entity, 'Writer', parent)
    builder.add_values(entity, 'WriterSort', parent)
    builder.add_values(entity, 'Arranger', parent)
    builder.add_values(entity, 'ArrangerSort', parent)
    builder.add_values(entity, 'Lyricist', parent)
    builder.add_values(entity, 'LyricistSort', parent)

# --------------------------------------------------------------------------------------------------
def add_performers(builder, entity, parent=None):
    """
    Add performer tags from a tagstore to a TagFileBuilder.
    """
    builder.add_values(entity, 'Conductor', parent)
    builder.add_values(entity, 'ConductorSort', parent)
    builder.add_values(entity, 'Performer', parent)
    builder.add_values(entity, 'PerformerSort', parent)

# --------------------------------------------------------------------------------------------------
def add_dates(builder, entity, require_date, parent=None):
    """
    Add dates from a tagstore to a TagFileBuilder.
    """
    if require_date:
        builder.add_values_req(entity, 'Date')
    else:
        builder.add_values(entity, 'Date')
    # Don't write OriginalDate if it == Date
    if 'OriginalDate' in entity.tags:
        if 'Date' not in entity.tags or entity.tags['OriginalDate'][0] != entity.tags['Date'][0]:
            builder.add_values(entity, 'OriginalDate')

# --------------------------------------------------------------------------------------------------
def add_unsupported(builder, entity, parent=None):
    """
    Add unsupported/unknown tags from a tagstore to a TagFileBuilder.
    """
    if isinstance(entity, Release):
        l = _release_tags
    elif isinstance(entity, Disc):
        l = _disc_tags
    elif isinstance(entity, Track):
        l = _track_tags
    else:
        raise TaggingError('unexpected entity type')

    found = False
    for key in entity.tags.keys():
        if key not in l and key not in _musicbrainz_tags and key not in _replaygain_tags:
            if not found:
                builder.add_blank()
                builder.add_comment('Miscellaneous')
                found = True
            builder.add_values(entity, key, parent)
    if found:
        builder.add_blank()

# --------------------------------------------------------------------------------------------------
def add_musicbrainz(builder, rel):
    """
    Add musicbrainz tag lines from a Release tagstore to a TagFileBuilder.
    """
    builder.add_comment('Musicbrainz info')
    for tag in _musicbrainz_tags:
        builder.add_values(rel, tag)
    for disc in rel.discs:
        for tag in _musicbrainz_tags:
            builder.add_values(disc, tag)
        for track in disc.tracks:
            for tag in _musicbrainz_tags:
                builder.add_values(track, tag, disc)

# --------------------------------------------------------------------------------------------------
def add_replaygain(builder, rel):
    """
    Add replaygain tag lines from a Release tagstore to a TagFileBuilder.
    """
    builder.add_comment('Replaygain info')
    for tag in _replaygain_tags:
        builder.add_values(rel, tag)
    for disc in rel.discs:
        for tag in _replaygain_tags:
            builder.add_values(disc, tag)
        for track in disc.tracks:
            for tag in _replaygain_tags:
                builder.add_values(track, tag, disc)

# --------------------------------------------------------------------------------------------------
def add_structured(builder, rel):
    """
    Add standard tag lines from a Release tagstore to a TagFileBuilder.
    """
    if args.verbose >= 2:
        print('\n<Release entity>', file=sys.stderr)
        print(rel.pprint(), file=sys.stderr)

    builder.add_comment('Album / common track info')
    # The release may have an albumartist even if it's a single-artist release.
    if 'AlbumArtist' in rel.tags:
        builder.add_values(rel, 'AlbumArtist')
        builder.add_values(rel, 'AlbumArtistSort')
    elif rel.is_single_artist:
        builder.add_values_as(rel, 'Artist', 'AlbumArtist')
        builder.add_values_as(rel, 'ArtistSort', 'AlbumArtistSort')
    elif rel.is_various:
        # In this case, get_tags should have added albumartist/sort if missing.
        pass

    # Always want a multi-value album artist output, so prefer any proper AlbumArtists multi-value,
    # but fall back on what we used for AlbumArtist.
    if 'AlbumArtists' in rel.tags:
        builder.add_values(rel, 'AlbumArtists')
        builder.add_values(rel, 'AlbumArtistsSort')
    elif 'AlbumArtist' in rel.tags:
        builder.add_values_as(rel, 'AlbumArtist', 'AlbumArtists')
        builder.add_values_as(rel, 'AlbumArtistSort', 'AlbumArtistsSort')
    elif rel.is_single_artist:
        builder.add_values_as(rel, 'Artist', 'AlbumArtists')
        builder.add_values_as(rel, 'ArtistSort', 'AlbumArtistsSort')
    elif rel.is_various:
        # In this case, get_tags should have added albumartist/sort if missing.
        pass

    add_artists(builder, rel)
    if 'Performer' in rel.tags:
        pass
    elif rel.is_single_artist:
        # Assume this is a popular release with no performer credits.
        builder.add_values_as(rel, 'Artist', 'Performer')
        builder.add_values_as(rel, 'ArtistSort', 'PerformerSort')
    elif not rel.is_various:
        # Assume this is a mixed release with no performer credits, where album artists are the
        # primary performers; prefer multi-value, if available.
        if 'AlbumArtists' in rel.tags:
            builder.add_values_as(rel, 'AlbumArtists', 'Performer')
            builder.add_values_as(rel, 'AlbumArtistsSort', 'PerformerSort')
        else:
            builder.add_values_as(rel, 'AlbumArtist', 'Performer')
            builder.add_values_as(rel, 'AlbumArtistSort', 'PerformerSort')
    if args.classical and not args.artist_block and rel.is_single_artist \
        and 'Composer' not in rel.tags:
        # Assume the artist is the composer, though it could be the primary performer.
        builder.add_values_as(rel, 'Artist', 'Composer')
        builder.add_values_as(rel, 'ArtistSort', 'ComposerSort')

    builder.add_values_req(rel, 'Album')
    if not args.work_block:
        builder.add_values(rel, 'Work')
        builder.add_values(rel, 'Title')
        builder.add_values(rel, 'Part') # shouldn't ever be at this level, though
    add_dates(builder, rel, True)
    builder.add_values_req(rel, 'Genre')
    builder.add_values(rel, 'Version')
    builder.add_values(rel, 'Comment')
    builder.add_values(rel, 'Compilation')

    if args.single_file:
        builder.add_blank()
    else:
        builder.add_comment(
            'The following should be a unique identifier for the release (e.g., UPC or')
        builder.add_comment(
            'catalog number) to allow clients to merge a multi-disc set.')
        if 'LabelId' in rel.tags:
            builder.add_values(rel, 'LabelId')
        elif 'Barcode' in rel.tags:
            builder.add_values_as(rel, 'Barcode', 'LabelId')
        elif 'CatalogNumber' in rel.tags:
            builder.add_values_as(rel, 'CatalogNumber', 'LabelId')
        elif 'ASIN' in rel.tags:
            builder.add_values_as(rel, 'ASIN', 'LabelId')
        else:
            builder.add_value(rel, 'LabelId', '')
        builder.add_blank()

    # Print disc and track artists in an artists block if requested.
    if args.artist_block and not rel.is_single_artist:
        builder.add_comment('Artists')
        for disc in rel.discs:
            # Add disc-level artists.
            add_artists(builder, disc)
            # Add condensed track-level artists.
            add_artists(builder, disc.tracks, disc)
        builder.add_blank()

    # Composer/arranger/lyicist block.
    if args.artist_block or \
        'Composer' in rel.tags or 'Arranger' in rel.tags or 'Lyricist' in rel.tags or \
        'Writer' in rel.tags:
        builder.add_comment('Composers')
    if args.classical and args.artist_block and rel.is_single_artist \
        and 'Composer' not in rel.tags:
        # Assume the artist is the composer, though it could be the primary performer.
        builder.add_values_as(rel, 'Artist', 'Composer')
        builder.add_values_as(rel, 'ArtistSort', 'ComposerSort')
    add_composers(builder, rel)

    # Print disc and track composers in this block if requested.
    if args.artist_block:
        for disc in rel.discs:
            # Add disc-level composers.
            add_composers(builder, disc)
            # Add condensed track-level composers.
            add_composers(builder, disc.tracks, disc)
    builder.add_blank()

    # Performer block.
    if args.artist_block or 'Conductor' in rel.tags or 'Performer' in rel.tags:
        builder.add_comment('Performers')
    add_performers(builder, rel)
    # Print disc and track performers from tracks in this block if requested.
    if args.artist_block:
        for disc in rel.discs:
            # Add disc-level performers.
            add_performers(builder, disc)
            # Add condensed track-level performers.
            add_performers(builder, disc.tracks, disc)
    builder.add_blank()

    # Print works in a work block if requested.
    if args.work_block:
        builder.add_comment('Works')
        builder.add_values(rel, 'Work')
        builder.add_values(rel, 'Title')
        for disc in rel.discs:
            # Add disc-level works.
            builder.add_values(disc, 'Work')
            # Add condensed track-level works.
            builder.add_values(disc.tracks, 'Work', disc)
        builder.add_values(rel, 'Part') # part shouldn't ever be at this level, though
        builder.add_blank()

    # Unknown/unsupported stuff.
    if args.output_unsupported:
        add_unsupported(builder, rel)

    # Print a block of disc info.  If there's only one disc, there shouldn't be any tags in the
    # disc (they should have merged to the release), but we'll print just in case.
    if len(rel.discs) > 1 or len(rel.discs[0].tags) > 0:
        builder.add_comment('Disc info')
        for disc in rel.discs:
            builder.add_value(disc, 'DiscNumber', disc.number)
            builder.add_values(disc, 'DiscSubtitle')
            builder.add_values(disc, 'AlbumArtist')
            builder.add_values(disc, 'AlbumArtistSort')
            builder.add_values(disc, 'AlbumArtists')
            builder.add_values(disc, 'AlbumArtistsSort')
            add_dates(builder, disc, False)
            builder.add_values(disc, 'Genre')
            builder.add_values(disc, 'Version')
            builder.add_values(disc, 'Comment')

            # Print the disc-common values that weren't written in earlier blocks.
            if not args.artist_block:
                add_artists(builder, disc)
                add_composers(builder, disc)
                add_performers(builder, disc)
            if not args.work_block:
                builder.add_values(disc, 'Work')

            builder.add_values(disc, 'Title')
            builder.add_values(disc, 'Part') # shouldn't ever be at this level, though
            builder.add_values(disc, 'CoverNumber')

            # Unknown/unsupported stuff.
            if args.output_unsupported:
                add_unsupported(builder, disc)

        # Blank line before next disc, or start of tracks.
        builder.add_blank()

    for disc in rel.discs:
        # If multi-disc, print a header per disc, otherwise something generic.
        if len(rel.discs) == 1:
            builder.add_comment('Track info')
        else:
            builder.add_comment('Disc ' + disc.number)

        for track in disc.tracks:
            # Print the artists that weren't printed in an artist block.
            if not args.artist_block:
                add_artists(builder, track, disc)

            # Print the works that weren't printed in a work block.
            if not args.work_block:
                builder.add_values(track, 'Work', disc)

            builder.add_values(track, 'Title', disc)
            builder.add_values(track, 'Part', disc)
            builder.add_values(track, 'Version', disc)

            # Print remaining artists that weren't blocked.
            if not args.artist_block:
                add_composers(builder, track, disc)
                add_performers(builder, track, disc)

            builder.add_values(track, 'CoverNumber', disc)
            builder.add_values(track, 'Genre', disc)
            builder.add_values(track, 'Comment', disc)
            add_dates(builder, track, False)

            # Unknown/unsupported stuff.
            if args.output_unsupported:
                add_unsupported(builder, track, disc)

            if args.break_tracks:
                builder.add_blank()

        # Add blank line before next disc.
        builder.add_blank()

# --------------------------------------------------------------------------------------------------
def add_tagset(builder, entity, parent=None):
    """
    Add all tags from a TagStore to a TagFileBuilder.
    """
    for tag in entity.tags.keys():
        builder.add_values(entity, tag, parent)

# --------------------------------------------------------------------------------------------------
def add_unstructured(builder, rel):
    """
    Add tag lines from a Release tagstore to a TagFileBuilder.
    """
    add_tagset(builder, rel)
    for disc in rel.discs:
        add_tagset(builder, disc)
        for track in disc.tracks:
            add_tagset(builder, track, disc)

# --------------------------------------------------------------------------------------------------
def process_files():
    """
    Generate kantag format output for the selected files.
    """
    # Get a Release object containing tags for all the files.
    rel_builder = ReleaseBuilder(args)
    rel_builder.read(args.audio_files)
    rel = rel_builder.release

    # Create a TagFileBuilder object to store the output.  Warnings are disabled because the user
    # will get warnings on reading the source files, and the TagFileBuilder warnings only happen if
    # the tag gets written out.
    builder = TagFileBuilder(warn=False)

    if args.structured:
        if args.standard:
            add_structured(builder, rel)
        if args.musicbrainz:
            builder.add_blank()
            add_musicbrainz(builder, rel)
        if args.replaygain:
            builder.add_blank()
            add_replaygain(builder, rel)
    else:
        add_unstructured(builder, rel)
    builder.add_blank()

    # Write out from the builder.
    if args.output == '-':
        print(str(builder.tags))
    else:
        with io.open(args.output, mode='wt', encoding='utf-8') as f:
            f.write(str(builder.tags))

# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    #main(sys.argv[1:])
    main()
