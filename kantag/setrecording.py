#!/usr/bin/env python3

# setrecording.py - kantag tool for applying a musicbrainz recording id to a file.
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
# see <http://www.gnu.org/licenses>.import os
import os
import mutagen.id3
import mutagen.oggvorbis
import mutagen.oggopus
import mutagen.easymp4
import musicbrainzngs as ngs
from pprint import pprint
from argparse import ArgumentParser
from .util import ToggleAction
from ._version import __version__
from . import exceptions, textencoding, musicbrainz

# --------------------------------------------------------------------------------------------------
def remove_key(dictionary, key):
    """
    Remove items from a dictionary where the key is a case-insensitive match for a specified key.
    """
    for k in [k for k in iter(dictionary) if k.lower() == key.lower()]:
        del(dictionary[k])

# --------------------------------------------------------------------------------------------------
def process_vorbis_file(args):
    """
    Add MusicBrainz IDs to an Ogg file.
    """
    rec = musicbrainz.get_recording_by_id(args.recording_id)
    works = musicbrainz.get_recording_works(rec)
    artists = musicbrainz.get_recording_artists(rec)
        
    afile = mutagen.oggvorbis.OggVorbis(args.audio_file)
    remove_key(afile, 'musicbrainz_trackid')
    afile['musicbrainz_trackid'] = args.recording_id
    
    remove_key(afile, 'musicbrainz_artistid')
    afile['musicbrainz_artistid'] = [artist['id'] for artist in artists]
    
    remove_key(afile, 'musicbrainz_workid')
    if len(works) > 0:
        afile['musicbrainz_workid'] = [work['id'] for work in works]
    
    if args.write_work and len(works) > 0:
        remove_key(afile, 'work')
        for work in works:
            title = work['title']
            if args.ascii_punctuation:
                title = textencoding.asciipunct(title)
            afile['work'] = title
    
    afile.save()
    
# --------------------------------------------------------------------------------------------------
def process_opus_file(args):
    """
    Add MusicBrainz IDs to an Ogg file.
    """
    rec = musicbrainz.get_recording_by_id(args.recording_id)
    works = musicbrainz.get_recording_works(rec)
    artists = musicbrainz.get_recording_artists(rec)
        
    afile = mutagen.oggopus.OggOpus(args.audio_file)
    remove_key(afile, 'musicbrainz_trackid')
    afile['musicbrainz_trackid'] = args.recording_id
    
    remove_key(afile, 'musicbrainz_artistid')
    afile['musicbrainz_artistid'] = [artist['id'] for artist in artists]
    
    remove_key(afile, 'musicbrainz_workid')
    if len(works) > 0:
        afile['musicbrainz_workid'] = [work['id'] for work in works]
    
    if args.write_work and len(works) > 0:
        remove_key(afile, 'work')
        for work in works:
            title = work['title']
            if args.ascii_punctuation:
                title = textencoding.asciipunct(title)
            afile['work'] = title
    
    afile.save()

# --------------------------------------------------------------------------------------------------
def process_mp3_file(args):
    """
    Add MusicBrainz IDs to an MP3 file.
    """
    rec = musicbrainz.get_recording_by_id(args.recording_id)
    works = musicbrainz.get_recording_works(rec)
    artists = musicbrainz.get_recording_artists(rec)
    
    afile = mutagen.id3.ID3(args.audio_file)
    afile.update_to_v24()
    
    name = 'MusicBrainz Track Id'
    afile.delall('TXXX:' + name)
    afile.delall('TXXX:' + name.upper())
    afile.delall('TXXX:' + name.lower())
    afile.add(mutagen.id3.TXXX(encoding=3, desc=name.upper(), text=args.recording_id))
    
    name = 'MusicBrainz Artist Id'
    afile.delall('TXXX:' + name)
    afile.delall('TXXX:' + name.upper())
    afile.delall('TXXX:' + name.lower())
    for artist in artists:
        afile.add(mutagen.id3.TXXX(encoding=3, desc=name.upper(), text=artist['id']))

    name = 'MusicBrainz Work Id'
    afile.delall('TXXX:' + name)
    afile.delall('TXXX:' + name.upper())
    afile.delall('TXXX:' + name.lower())
    for work in works:
        afile.add(mutagen.id3.TXXX(encoding=3, desc=name.upper(), text=work['id']))
    
    if args.write_work and len(works) > 0:
        name = 'Work'
        afile.delall('TXXX:' + name)
        afile.delall('TXXX:' + name.upper())
        afile.delall('TXXX:' + name.lower())
        for work in works:
            title = work['title']
            if args.ascii_punctuation:
                title = textencoding.asciipunct(title)
            afile.add(mutagen.id3.TXXX(encoding=3, desc=name.upper(), text=title))

    afile.save()

# --------------------------------------------------------------------------------------------------
def process_m4a_file(args):
    """
    Add MusicBrainz IDs to an Ogg file.
    """
    rec = musicbrainz.get_recording_by_id(args.recording_id)
    works = musicbrainz.get_recording_works(rec)
    artists = musicbrainz.get_recording_artists(rec)

    # At time of writing this code, EasyMP4 appeared to have a bug that made it impossible to
    # completely remove a particular tag from the file.  Even though it would no longer show in the
    # dictionary, it would still be present in the file after save.  So, the code uses MP4 instead.
    prefix = '----:com.apple.iTunes:'
    afile = mutagen.mp4.MP4(args.audio_file)

    remove_key(afile, prefix + 'musicbrainz_trackid')
    name = prefix + 'MusicBrainz Track Id'
    remove_key(afile, name)
    afile[name] = mutagen.mp4.MP4FreeForm(
        bytes(args.recording_id, 'UTF-8'), 
        mutagen.mp4.AtomDataType.UTF8)

    remove_key(afile, prefix + 'musicbrainz_artistid')
    name = prefix + 'MusicBrainz Artist Id'
    remove_key(afile, name)
    for artist in artists:
        afile[name] = mutagen.mp4.MP4FreeForm(
            bytes(artist['id'], 'UTF-8'), 
            mutagen.mp4.AtomDataType.UTF8)

    remove_key(afile, prefix + 'musicbrainz_workid')
    name = prefix + 'MusicBrainz Work Id'
    remove_key(afile, name)
    for work in works:
        afile[name] = mutagen.mp4.MP4FreeForm(
            bytes(work['id'], 'UTF-8'), 
            mutagen.mp4.AtomDataType.UTF8)

    if args.write_work and len(works) > 0:
        name = prefix + 'work'
        remove_key(afile, name)
        for work in works:
            title = work['title']
            if args.ascii_punctuation:
                title = textencoding.asciipunct(title)
            afile[name] = mutagen.mp4.MP4FreeForm(
            bytes(title, 'UTF-8'), 
            mutagen.mp4.AtomDataType.UTF8)
    
    afile.save()
    
# --------------------------------------------------------------------------------------------------
def process_file(args):
    """
    Search the MP3 file for a UFID tag and copy to MusicBrainz Trac Id, if found.
    """
    ext = os.path.splitext(args.audio_file)[1].lower()
    if ext == '.ogg':
        return process_vorbis_file(args)
    elif ext == '.opus':
        return process_opus_file(args)
    elif ext == '.mp3':
        return process_mp3_file(args)
    elif ext == '.m4a':
        return process_m4a_file(args)
    else:
        raise exceptions.FileTypeError('invalid file extension: ' + ext)

# --------------------------------------------------------------------------------------------------
def main():
    """
    Parse command line argument and initiate main operation.
    """
    parser = ArgumentParser(
        description='Fetches information about a recording from the MusicBrainz API and applies ' +
        'it to an audio file.')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-v', '--verbose',
        help='verbose output (can be specified up to three times)',
        action='count', default=0)
    parser.add_argument('-A', '--ascii-punctuation',
        help='replace non-ascii punctuation in titles with ascii equivalents [default=y]',
        action=ToggleAction, choices=['y', 'n'], default=True)
    parser.add_argument('recording_id',
        help='MusicBrainz identifier for the recording',
        action='store')
    parser.add_argument('audio_file',
        help='audio file (Ogg Vorbis, Ogg Opus, MP3, M4A)',
        action='store')
    parser.add_argument('-w', '--write_work',
        help='write Work tags [default=y]',
        action=ToggleAction, dest='write_work', choices=['y', 'n'], default=True)
    args = parser.parse_args()

    if args.verbose >= 2:
        print('<Arguments>')
        print(pprint.PrettyPrinter(indent=2).pformat(vars(args)) + '\n')

    # Check for some files to build tags for.
    if not os.path.exists(args.audio_file):
        parser.error('audio file not found: ' + args.audio_file)

    # Write the output.
    process_file(args)

# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    #main(sys.argv[1:])
    main()
