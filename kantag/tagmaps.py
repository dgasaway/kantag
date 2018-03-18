# tagmaps.py - kantag metadata mapping defintions.
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

# TMCL='Musician credits list' (2.4)
# IPLS='Involved people list' (2.4)
# Had both TMCL and IPLS in Beastie Boys - Sure Shot ?!!!?
# TDRC replaced TDAT (2.4), TDAT could only do 4 chars.
# TDRC 'when the audio was recorded'
# TDRL 'when the audio was first released'
# Foobar: "The TDRC frame is officially to be used for the recording time, TDRL
#          is for the release time but TDRC is generally used by most programs."
# http://wiki.musicbrainz.org/MusicBrainz_Picard/Tags/Mapping
# http://musicbrainz.org/doc/Picard_Tag_Mapping
# http://musicbrainz.org/doc/MusicBrainzTag
# http://wiki.hydrogenaudio.org/index.php?title=Foobar2000:ID3_Tag_Mapping
# http://wiki.hydrogenaudio.org/index.php?title=Foobar2000:Encouraged_Tag_Standards#ALBUM_ARTIST
# http://wiki.hydrogenaudio.org/index.php?title=Foobar2000:Title_Formatting_Reference#Field_remappings
# http://code.google.com/p/mutagen/source/browse/trunk/mutagen/easyid3.py
# http://www.id3.org/id3v2.4.0-frames
# http://www.id3.org/id3v2.4.0-structure
# http://forums.musicbrainz.org/viewtopic.php?id=2359
# http://www.hydrogenaudio.org/forums/lofiversion/index.php/t85165.html

"""
Set of internal/kantag file tag names.
"""
cannonical_tags = frozenset([
    u'Album',
    u'AlbumArtist',
    u'AlbumArtistNonSort',
    u'AlbumArtistSort',
    u'AlbumArtists',
    u'AlbumArtistsSort',
    u'Arranger',
    u'ArrangerSort',
    u'Artist',
    u'ArtistNonSort',
    u'ArtistSort',
    u'Artists',
    u'ArtistsSort',
    u'ASIN',
    u'Barcode',
    u'CatalogNumber',
    u'Comment',
    u'Compilation',
    u'Composer',
    u'ComposerSort',
    u'Conductor',
    u'ConductorSort',
    u'CoverNumber',
    u'Date',
    u'DiscNumber',
    u'DiscSubtitle',
    u'DJMixer',
    u'Engineer',
    u'Genre',
    u'ISRC',
    u'Label',
    u'LabelId',
    u'Language',
    u'Lyricist',
    u'LyricistSort',
    u'Media',
    u'Mixer',
    u'OriginalDate',
    u'OriginalYear',
    u'Part',
    u'Performer',
    u'PerformerSort',
    u'Producer',
    u'ReleaseCountry',
    u'ReleaseStatus',
    u'ReleaseType',
    u'Script',
    u'Title',
    u'TotalDiscs',
    u'TotalTracks',
    u'TrackNumber',
    u'Version',
    u'Work',
    u'Writer',
    u'WriterSort',
    u'acoustid_id',
    u'musicbrainz_albumartistid',
    u'musicbrainz_albumid',
    u'musicbrainz_albumstatus',
    u'musicbrainz_albumtype',
    u'musicbrainz_artistid',
    u'musicbrainz_discid',
    u'musicbrainz_releasegroupid',
    u'musicbrainz_trackid',
    u'musicbrainz_releasetrackid',
    u'musicbrainz_workid',
    u'replaygain_album_peak',
    u'replaygain_album_gain',
    u'replaygain_track_peak',
    u'replaygain_track_gain'
    ])

""" Map ID3 frames to kantag name. """
id3_read_map = {
    u'TALB': u'Album',
    u'TXXX:ALBUM ARTIST': u'AlbumArtist',
    u'TXXX:ALBUMARTIST': u'AlbumArtist',
    u'TPE2': u'AlbumArtist',
    u'TXXX:ALBUMARTISTNONSORT': u'AlbumArtistNonSort',
    u'TXXX:ALBUMARTISTSORT': u'AlbumArtistSort',
    u'TSO2': u'AlbumArtistSort',
    u'TXXX:ALBUMARTISTS': u'AlbumArtists',
    u'TXXX:ALBUMARTISTSSORT': u'AlbumArtistsSort',
    u'TXXX:albumartists': u'AlbumArtists',
    u'TXXX:albumartistssort': u'AlbumArtistsSort',
    u'TXXX:AMAZON_ID': u'AmazonId',
    u'TXXX:ARRANGER': u'Arranger',
    u'TXXX:ARRANGERSORT': u'ArrangerSort',
    u'TPE4': u'Arranger',
    u'TPE1': u'Artist',
    u'TXXX:ARTISTSORT': u'ArtistSort',
    u'TXXX:ARTISTNONSORT': u'ArtistNonSort',
    u'TSOP': u'ArtistSort',
    u'TXXX:Artists': u'Artists',
    u'TXXX:COMMENT': u'Comment',
    u'COMM': u'Comment',
    u'TCOM': u'Composer',
    u'TSOC': u'ComposerSort',
    u'TXXX:COMPOSERSORT': u'ComposerSort',
    u'TPE3': u'Conductor',
    u'TXXX:CONDUCTORSORT': u'ConductorSort',
    u'TXXX:COVERNUMBER': u'CoverNumber',
    u'TDRC': u'Date',
    u'TXXX:DATE': u'Date',
    u'TPOS': u'DiscNumber',
    u'TSST': u'DiscSubtitle',
    u'TCON': u'Genre',
    u'TPUB': u'Label',
    u'TXXX:LABELID': u'LabelId',
    u'TXXX:BARCODE': u'Barcode',
    u'TXXX:CATALOGNUMBER': u'CatalogNumber',
    u'TXXX:ASIN': u'LabelId',
    u'TLAN': u'Language',
    u'TEXT': u'Lyricist',
    u'TOLY': u'Lyricist',
    u'TXXX:LYRICISTSORT': u'LyricistSort',
    u'TMED': u'Media',
    u'TDOR': u'OriginalDate',
    u'TXXX:originalyear': u'OriginalDate',
    u'TXXX:PART': u'Part',
    u'TXXX:PERFORMER': u'Performer',
    u'TMCL': u'Performer',
    u'TXXX:PERFORMERSORT': u'PerformerSort',
    u'TXXX:MusicBrainz Album Release Country': u'ReleaseCountry',
    u'TXXX:MusicBrainz Album Status': u'ReleaseStatus',
    u'TXXX:MusicBrainz Album Type': u'ReleaseType',
    u'TXXX:SCRIPT': u'Script',
    u'TIT2': u'Title',
    u'TRCK': u'TrackNumber',
    u'TIT3': u'Version',
    u'TXXX:VERSION': u'Version',
    u'TXXX:version': u'Version',
    u'TXXX:WORK': u'Work',
    u'TXXX:Work': u'Work',
    u'TOAL': u'Work',
    u'TXXX:WRITER': u'Writer',
    u'TXXX:WRITERSORT': u'WriterSort',
    u'TXXX:writer': u'Writer',
    u'TXXX:writersort': u'WriterSort',
    u'TXXX:Writer': u'Writer',
    u'TCMP': u'Compilation',
    u'TIPL': u'Person', # See TIPL map below.
    u'TXXX:MusicBrainz Album Id': u'musicbrainz_albumid',
    u'TXXX:MusicBrainz Album Artist Id': u'musicbrainz_albumartistid',
    u'TXXX:MusicBrainz Artist Id': u'musicbrainz_artistid',
    u'TXXX:MusicBrainz Disc Id': u'musicbrainz_discid',
    u'TXXX:MusicBrainz Release Group Id': u'musicbrainz_releasegroupid',
    u'TXXX:MusicBrainz Release Track Id': u'musicbrainz_releasetrackid',
    u'UFID:http://musicbrainz.org': u'musicbrainz_trackid',
    u'TXXX:MusicBrainz Work Id': u'musicbrainz_workid',
    u'TXXX:MUSICBRAINZ_TRACKID': u'musicbrainz_trackid',
    u'TXXX:replaygain_album_peak': u'replaygain_album_peak',
    u'TXXX:replaygain_album_gain': u'replaygain_album_gain',
    u'TXXX:replaygain_track_peak': u'replaygain_track_peak',
    u'TXXX:replaygain_track_gain': u'replaygain_track_gain',
    u'TXXX:Acoustid Id': u'acoustid_id'
    }

""" Map non-ID3 tags from, e.g., Picard to cannonical names. """
# Note that the destination value should be something in cannonical_tags.
general_read_map = {
    u'remixer': u'Arranger',
    u'djmixer': u'Arranger',
    u'disctotal': u'TotalDiscs',
    u'tracktotal': u'TotalTracks'
    }

""" Map TIPL involvements to kantag name. """
tipl_map = {
    u'dj-mix': u'DJMixer',
    u'mix': u'Mixer'
    }

""" Map kantag name to ID3 frame. """
id3_write_map = {
    u'Album': u'TALB',
    u'AlbumArtist': u'TXXX:ALBUM ARTIST',
    u'Artist': u'TPE1',
    u'ArtistSort': u'TSOP',
    # Having more than one COMM with the same content descriptor (third descriptor, after
    #     language) can cause problems with, for example, foobar2000. "There may be more
    #     than one comment frame in each tag, but only one with the same language and
    #     content descriptor."
    # 'Comment': 'COMM::eng', # having more than one with the same content
    u'Comment': u'TXXX:COMMENT',
    u'Composer': u'TCOM',
    u'Conductor': u'TPE3',
    u'Date': u'TDRC',
    u'DiscNumber': u'TPOS',
    u'DiscSubtitle': u'TSST',
    u'Genre': u'TCON',
    u'Language': u'TLAN',
    u'Lyricist': u'TEXT',
    u'OriginalDate': u'TDOR',
    u'Title': u'TIT2',
    u'TrackNumber': u'TRCK',
    u'musicbrainz_albumid': u'TXXX:MusicBrainz Album Id',
    u'musicbrainz_albumartistid': u'TXXX:MusicBrainz Album Artist Id',
    u'musicbrainz_artistid': u'TXXX:MusicBrainz Artist Id',
    u'musicbrainz_releasegroupid': u'TXXX:MusicBrainz Release Group Id',
    u'musicbrainz_releasetrackid': u'TXXX:MusicBrainz Release Track Id',
    u'musicbrainz_trackid': u'UFID:http://musicbrainz.org',
    u'musicbrainz_workid': u'TXXX: MusicBrainz Work Id',
    u'replaygain_album_peak': u'TXXX:replaygain_album_peak',
    u'replaygain_album_gain': u'TXXX:replaygain_album_gain',
    u'replaygain_track_peak': u'TXXX:replaygain_track_peak',
    u'replaygain_track_gain': u'TXXX:replaygain_track_gain'
    # Anything not explicitly listed maps to TXXX:<WHATEVER>
    }

""" Additional freeform items for writing to MP4/M4A. """
mp4_map = {
    # Note: 'albumartistsort' is supported by EasyMP4, but with default settings foobar2000 will
    #       map 'soaa' as ALBUMARTISTSORTORDER.
    b'albumartistsort': 'albumartistsort',
    b'albumartists': 'albumartists',
    b'albumartistssort': 'albumartistssort',
    b'arranger': 'arranger',
    b'arrangersort': 'arrangersort',
    b'composer': 'composer',
    # Note: 'composersort' is supported by EasyMP4, but with default settings foobar2000 will map
    #       'soco' as COMPOSERSORTORDER.
    b'composersort': 'composersort',
    b'conductor': 'conductor',
    b'conductorsort': 'conductorsort',
    b'covernumber': 'covernumber',
    b'discsubtitle': 'discsubtitle',
    b'labelid': 'labelid',
    b'lyricist': 'lyricist',
    b'lyricistsort': 'lyricistsort',
    b'originaldate': 'originaldate',
    b'part': 'part',
    b'performer': 'performer',
    b'performersort': 'performersort',
    b'version': 'version',
    b'work': 'work',
    b'writer': 'writer',
    b'writersort': 'writersort',
    b'replaygain_album_peak': 'replaygain_album_peak',
    b'replaygain_album_gain': 'replaygain_album_gain',
    b'replaygain_track_peak': 'replaygain_track_peak',
    b'replaygain_track_gain': 'replaygain_track_gain'
}

""" vcomment/ID3 map used by foobar2000; for development reference only. """
_foobar_id3_map = {
    'album': 'TALB',
    'albumartist': 'TXXX:ALBUM ARTIST',
    'artist': 'TPE1',
    'artistsortorder': 'TSOP', # This causes problems for mixed vcomment/mp3 fb2k library
    'discnumber': 'TPOS',
    'band': 'TPE2',
    'comment': 'COMM',
    'composer': 'TCOM',
    'conductor': 'TPE3',
    'date': 'TDRC', # also, TXXX:DATE
    'discnumber': 'TPOS',
    'genre': 'TCON',
    'tracknumber': 'TRCK',
    'remixed by': 'TPE4',
    'lyricist': 'TEXT',
    'subtitle': 'TIT3',
    'replaygain_album_peak': 'TXXX:replaygain_album_peak',
    'replaygain_album_gain': 'TXXX:replaygain_album_gain',
    'replaygain_track_peak': 'TXXX:replaygain_track_peak',
    'replaygain_track_gain': 'TXXX:replaygain_track_gain',
    # Anything not explicitly listed maps to TXXX:<WHATEVER>
    }

""" Tag remaps used by foobar2000; for development reference only. """
_foobar_field_remap = (
    ['album artist', ['album artist', 'artist', 'composer', 'performer', 'albumartist']],
    ['album', ['album', 'venue']],
    ['artist', ['artist', 'album artist', 'composer', 'performer']],
    ['discnumber', ['discnumber', 'disc']],
    ['title', ['title', 'filename']]
    )

# NOTE: comment, discnumber, and discsubtitle are not set by stock Picard.
""" vcomment/ID3 map used by Musicbrainz Picard; for development reference only. """
_picard_id3_map = {
    'album': 'TALB',
    'albumartist': 'TPE2',
    'albumartistsort': 'TXXX:ALBUMARTISTSORT',
    'arranger': 'TIPL:arranger',
    'artist': 'TPE1',
    'artistsort': 'TSOP',
    'asin': 'TXXX:ASIN',
    'barcode': 'TXXX:BARCODE',
    'catalognumber': 'TXXX:CATALOGNUMBER',
    'composer': 'TCOM',
    'comment': 'COMM:description',
    'compilation': 'TCMP',
    'conductor': 'TPE3',
    'date': 'TDRC',
    'discnumber': 'TPOS',
    'discsubtitle': 'TSST',
    'djmixer': 'TIPL:DJ-mix',
    'engineer': 'TIPL:engineer',
    'label': 'TPUB',
    'language': 'TLAN',
    'lyricist': 'TEXT',
    'mixer': 'TIPL:mix',
    'originaldate': 'TDOR',
    'performer': 'TMCL:instrument',
    'producer': 'TIPL:producer',
    'remixer': 'TPE4',
    'subtitle': 'TIT3',
    'title': 'TIT2',
    'tracknumber': 'TRCK',
    'writer': 'TXXX:writer',
    'musicbrainz_trackid': 'UFID:http://musicbrainz.org',
    'musicbrainz_albumid': 'TXXX:MusicBrainz Album Id',
    'musicbrainz_artistid': 'TXXX:MusicBrainz Artist Id',
    'musicbrainz_albumartistid': 'TXXX:MusicBrainz Album Artist Id',
    'musicbrainz_workid': 'TXXX:MusicBrainz Work Id'
    }

""" vcomment/ID3 map used by mutagen; for development reference only. """
_mutagen_easyid3_map = {
    'genre': 'TCON',
    'date': 'TDRC',
    'performer:role': 'TMCL:role',
    'album': 'TALB',
    'composer': 'TCOM',
    'lyricist': 'TEXT',
    'title': 'TIT2',
    'version': 'TIT3',
    'artist': 'TPE1',
    'performer': 'TPE2',
    'conductor': 'TPE3',
    'arranger': 'TPE4',
    'discnumber': 'TPOS',
    'tracknumber': 'TRCK',
    'composersort': 'TSOC', # iTunes extension
    'artistsort': 'TSOP',
    'discsubtitle': 'TSST',
    'albumartistsort': 'TXXX:ALBUMARTISTSORT', # also TSO2, iTunes extension
    'barcode': 'TXXX:BARCODE',
    'musicbrainz_trackid': 'UFID:http://musicbrainz.org',
    'musicbrainz_albumid': 'TXXX:MusicBrainz Album Id',
    'musicbrainz_artistid': 'TXXX:MusicBrainz Artist Id',
    'musicbrainz_albumartistid': 'TXXX:MusicBrainz Album Artist Id',
    'musicbrainz_discid': 'TXXX:MusicBrainz Disc Id'
    }
