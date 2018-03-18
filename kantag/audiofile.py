# audiofile.py - kantag audio file metadata read and write operations.
# Copyright (C) 2013 David Gasaway
# http://code.google.com/p/kantag/

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
import mutagen.id3
import mutagen.oggvorbis
import mutagen.flac
import mutagen.easymp4
import tagmaps, exceptions
from util import TagValue
from tagset import TagSet

# --------------------------------------------------------------------------------------------------
def _map_tag(tag, warn):
    """
    Get the cannonical name for a tag.
    """
    work = tag.lower()
    if work in tagmaps.general_read_map:
        work = tagmaps.general_read_map[work].lower()
    l = [t for t in tagmaps.cannonical_tags if t.lower() == work]
    if len(l) == 0:
        if warn:
            print >> sys.stderr, 'warning: unrecognized tag: ' + tag
        return tag
    else:
        return l[0]

# --------------------------------------------------------------------------------------------------
def _break_text_frame(frame, tag):
    """
    Break a mutagen text frame into a list of TagValue named tuples.
    """
    result = []
    if isinstance(frame.text, list):
        for value in frame.text:
            if isinstance(value, mutagen.id3.ID3TimeStamp):
                result.append(TagValue(tag, value.text))
            else:
                result.append(TagValue(tag, value))
    else:
        result.append(TagValue(tag, value))

    return result

# --------------------------------------------------------------------------------------------------
def _break_tipl_frame(frame, warn):
    """
    Break a mutagen TIPL ID3 frame into a list of TagValue named tuples.
    """
    # TIPL has a list of people/involvements.
    result = []
    for involvement, artist in frame.people:
        # A couple of TIPL involvements need a map to get to the cannonical tag, the rest we hope
        # are in the cannonical list.
        tag = involvement.lower()
        if tag in tagmaps.tipl_map:
            tag = tagmaps.tipl_map[tag]
        else:
            tag = _map_tag(tag, warn)
        result.append(TagValue(tag, artist))

    return result

# --------------------------------------------------------------------------------------------------
def _break_tmcl_frame(frame, tag):
    """
    Break a mutagen TMCL ID3 frame into a list of TagValue named tuples.
    """
    # TMCL has a list of people/instruments.
    result = []
    for instrument, artist in frame.people:
        # kantag format can't currently directly support instruments, so we'll map this to a
        # musicbrainz/vcomment credit where the data is: "Performer=Artist Name (instrument)".
        if instrument is not None and instrument != '':
            artist = artist + ' (' + instrument + ')'
        result.append(TagValue(tag, artist))

    return result

# --------------------------------------------------------------------------------------------------
def _break_ufid_frame(frame, tag):
    """
    Break a mutagen UFID ID3 frame into a list of TagValue named tuples.
    """
    return [TagValue(tag, frame.data)]

# --------------------------------------------------------------------------------------------------
def _break_frame(frame, ftype, warn):
    """
    Break a mutagen ID3 frame into a list of TagValue named tuples.
    """
    # COMM can have different attributes like COMM:description:eng and so on, but we'll drop all
    # that since it can't be reproduced in a tag file.
    if ftype.startswith('COMM:'):
        ftype = 'COMM'

    if ftype in tagmaps.id3_read_map:
        tag = tagmaps.id3_read_map[ftype]

        # Examine the type of frame to pull out the values correctly, and flatten where necessary.
        if isinstance(frame, mutagen.id3.TextFrame):
            return _break_text_frame(frame, tag)
        elif isinstance(frame, mutagen.id3.TIPL):
            return _break_tipl_frame(frame, warn)
        elif isinstance(frame, mutagen.id3.TMCL):
            return _break_tmcl_frame(frame, tag)
        elif isinstance(frame, mutagen.id3.UFID):
            return _break_ufid_frame(frame, tag)
        else:
            raise exceptions.TaggingError('unexpected frame object encountered: ' + type(frame))
    else:
        if warn:
            print >> sys.stderr, 'warning: unknown ID3 frame type: ' + ftype
        return [TagValue(ftype, repr(frame))]

# --------------------------------------------------------------------------------------------------
def _build_frame(tag, values):
    """
    Build an mutagen ID3 frame from a tag name and associated values.
    """
    if tag in tagmaps.id3_write_map:
        frame = tagmaps.id3_write_map[tag]
    elif tag == 'TCMP':
        return mutagen.id3.TCMP(encoding=3, text=values)
    else:
        frame = 'TXXX:' + tag.upper()

    if frame == 'TALB':
        return mutagen.id3.TALB(encoding=3, text=values)
    elif frame == 'TPE1':
        return mutagen.id3.TPE1(encoding=3, text=values)
    elif frame == 'TCOM':
        return mutagen.id3.TCOM(encoding=3, text=values)
    elif frame == 'TPE3':
        return mutagen.id3.TPE3(encoding=3, text=values)
    elif frame == 'TDRC':
        return mutagen.id3.TDRC(encoding=3, text=values)
    elif frame == 'TPOS':
        return mutagen.id3.TPOS(encoding=3, text=values)
    elif frame == 'TSST':
        return mutagen.id3.TSST(encoding=3, text=values)
    elif frame == 'TCON':
        return mutagen.id3.TCON(encoding=3, text=values)
    elif frame == 'TEXT':
        return mutagen.id3.TEXT(encoding=3, text=values)
    elif frame == 'TIT2':
        return mutagen.id3.TIT2(encoding=3, text=values)
    elif frame == 'TRCK':
        return mutagen.id3.TRCK(encoding=3, text=values)
    elif frame == 'TSOP':
        return mutagen.id3.TSOP(encoding=3, text=values)
    elif frame == 'TIT3':
        return mutagen.id3.TIT3(encoding=3, text=values)
    elif frame == 'TSOC':
        return mutagen.id3.TSOC(encoding=3, text=values)
    elif frame == 'TDOR':
        return mutagen.id3.TDOR(encoding=3, text=values)
    elif frame.startswith('TXXX:'):
        desc = frame.partition(':')[2]
        return mutagen.id3.TXXX(encoding=3, desc=desc, text=values)
    elif frame.startswith('UFID:'):
        owner = frame.partition(':')[2]
        if len(values) > 1:
            raise exceptions.TaggingError('UFID owner not unique: ' + frame)
        return mutagen.id3.UFID(encoding=3, owner=owner, data=values[0])
    elif frame.startswith('COMM:'):
        split = frame.split(':', 3)
        return mutagen.id3.COMM(encoding=3, desc=split[1], lang=split[2], text=values)
    else:
        raise exceptions.TaggingError('unexpected mapped frame encountered: ' + frame)

    return None

# --------------------------------------------------------------------------------------------------
def _read_ogg(path, warn):
    """
    Read the existing tags from an ogg file, and return a list of TagValue named tuples.
    """
    afile = mutagen.oggvorbis.OggVorbis(path)
    return [TagValue(_map_tag(v[0], warn), v[1]) for v in afile.tags]

# --------------------------------------------------------------------------------------------------
def _read_flac(path, warn):
    """
    Read the existing tags from a flac file, and return a list of TagValue named tuples.
    """
    afile = mutagen.flac.FLAC(path)
    return [TagValue(_map_tag(v[0], warn), v[1]) for v in afile.tags]

# --------------------------------------------------------------------------------------------------
def _read_mp3(path, warn):
    """
    Read the existing tags from an mp3 file, and return a list of TagValue named tuples.
    """
    result = []
    afile = mutagen.id3.ID3(path)
    afile.update_to_v24()
    for ftype, frame in afile.iteritems():
        result.extend(_break_frame(frame, ftype, warn))

    return result

# --------------------------------------------------------------------------------------------------
def _read_m4a(path, warn):
    """
    Read the existing tags from an m4a file, and return a list of TagValue named tuples.
    """
    # Register additional keys not supported by EasyMP4 by default.
    for name, key in tagmaps.mp4_map.items():
        mutagen.easymp4.EasyMP4Tags.RegisterFreeformKey(key, name)

    result = []
    afile = mutagen.easymp4.EasyMP4(path)
    for key, values in afile.iteritems():
        result.extend([TagValue(_map_tag(key, warn), v) for v in values])
    return result

# --------------------------------------------------------------------------------------------------
def read_raw(path, warn=True):
    """
    Read the existing tags from an audio file, and return a list of TagValue named tuples.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == '.ogg':
        return _read_ogg(path, warn)
    elif ext == '.flac':
        return _read_flac(path, warn)
    elif ext == '.mp3':
        return _read_mp3(path, warn)
    elif ext == '.m4a':
        return _read_m4a(path, warn)
    else:
        raise exceptions.FileTypeError('invalid file extension: ' + ext)

# --------------------------------------------------------------------------------------------------
def read(path, warn=True):
    """
    Read the existing tags from an audio file, and return a TagSet.
    """
    return TagSet(read_raw(path, warn))

# --------------------------------------------------------------------------------------------------
def _write_ogg(path, tagset):
    """
    Write tags from a TagSet to an ogg file.
    """
    afile = mutagen.oggvorbis.OggVorbis(path)
    afile.clear()
    for tag, values in tagset.iteritems():
        afile[tag.lower()] = values
    afile.save()

# --------------------------------------------------------------------------------------------------
def _write_flac(path, tagset):
    """
    Write tags from a TagSet to a flac file.
    """
    afile = mutagen.flac.FLAC(path)
    afile.clear()
    for tag, values in tagset.iteritems():
        afile[tag.lower()] = values
    afile.save()

# --------------------------------------------------------------------------------------------------
def _write_mp3(path, tagset):
    """
    Write tags from a TagSet to an mp3 file.
    """
    try:
        afile = mutagen.id3.ID3(path)
    except mutagen.id3.ID3NoHeaderError:
        afile = mutagen.id3.ID3()

    afile.clear()
    for tag, values in tagset.iteritems():
        frame = _build_frame(tag, values)
        if frame is not None:
            afile.add(frame)

    # Assume compilation and write a TCMP frame if an albumartist is present.
    #if u'AlbumArtist' in tags:
    #    file.add(_build_frame('TCMP', '1'))

    afile.save(path)

# --------------------------------------------------------------------------------------------------
def _write_m4a(path, tagset):
    """
    Write tags from a TagSet to an m4a file.
    """
    # Register additional keys not supported by EasyMP4 by default.
    for name, key in tagmaps.mp4_map.items():
        mutagen.easymp4.EasyMP4Tags.RegisterFreeformKey(key, name)

    afile = mutagen.easymp4.EasyMP4(path)
    afile.delete()  # Needed to remove tags not mapped by EasyMP4.
    afile.clear()
    for tag, values in tagset.iteritems():
        afile[tag.lower()] = values
    afile.save()

# --------------------------------------------------------------------------------------------------
def write(path, tagset):
    """
    Write tags from a TagSet to an audio file.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == '.ogg':
        _write_ogg(path, tagset)
    elif ext == '.flac':
        _write_flac(path, tagset)
    elif ext == '.mp3':
        _write_mp3(path, tagset)
    elif ext == '.m4a':
        _write_m4a(path, tagset)
    else:
        raise exceptions.FileTypeError('invalid file extension: ' + ext)
