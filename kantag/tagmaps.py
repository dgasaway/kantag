# tagmaps.py - kantag metadata mapping defintions.
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

# TMCL='Musician credits list' (2.4)
# IPLS='Involved people list' (2.4)
# Had both TMCL and IPLS in Beastie Boys - Sure Shot ?!!!?
# TDRC replaced TDAT (2.4), TDAT could only do 4 chars.
# TDRC 'when the audio was recorded'
# TDRL 'when the audio was first released'
# Foobar: "The TDRC frame is officially to be used for the recording time, TDRL
#          is for the release time but TDRC is generally used by most programs."
# https://picard-docs.musicbrainz.org/en/appendices/tag_mapping.html
# https://wiki.hydrogenaud.io/index.php?title=Foobar2000:ID3_Tag_Mapping
# https://wiki.hydrogenaud.io/index.php?title=Foobar2000:Metadata_Compatibility_1.1.6_changes
# https://wiki.hydrogenaud.io/index.php?title=Foobar2000:Encouraged_Tag_Standards#ALBUM_ARTIST
# https://wiki.hydrogenaud.io/index.php?title=Foobar2000:Title_Formatting_Reference#Field_remappings
# https://github.com/quodlibet/mutagen/blob/main/mutagen/easyid3.py
# http://www.id3.org/id3v2.4.0-frames
# http://www.id3.org/id3v2.4.0-structure
# http://forums.musicbrainz.org/viewtopic.php?id=2359
# http://www.hydrogenaudio.org/forums/lofiversion/index.php/t85165.html

"""
Set of internal/kantag file tag names.
"""
cannonical_tags = frozenset([
    'Album',
    'AlbumArtist',
    'AlbumArtistNonSort',
    'AlbumArtistSort',
    'AlbumArtists',
    'AlbumArtistsSort',
    'AlbumVersion',
    'Arranger',
    'ArrangerSort',
    'Artist',
    'ArtistNonSort',
    'ArtistSort',
    'Artists',
    'ArtistsSort',
    'ASIN',
    'Barcode',
    'CatalogNumber',
    'Collection',
    'Comment',
    'Compilation',
    'Composer',
    'ComposerSort',
    'Conductor',
    'ConductorSort',
    'CoverNumber',
    'Damaged',
    'Date',
    'DiscNumber',
    'DiscSubtitle',
    'DJMixer',
    'EmbeddedImage',
    'Engineer',
    'Genre',
    'ISRC',
    'Label',
    'LabelId',
    'Language',
    'Lyricist',
    'LyricistSort',
    'Media',
    'Mixer',
    'OriginalDate',
    'OriginalYear',
    'Part',
    'Performer',
    'PerformerSort',
    'Producer',
    'ReleaseCountry',
    'ReleaseStatus',
    'ReleaseType',
    'Script',
    'SortDate',
    'Title',
    'TotalDiscs',
    'TotalTracks',
    'TrackNumber',
    'Version',
    'Work',
    'Writer',
    'WriterSort',
    'acoustid_id',
    'musicbrainz_albumartistid',
    'musicbrainz_albumid',
    'musicbrainz_albumstatus',
    'musicbrainz_albumtype',
    'musicbrainz_artistid',
    'musicbrainz_discid',
    'musicbrainz_releasegroupid',
    'musicbrainz_trackid',
    'musicbrainz_releasetrackid',
    'musicbrainz_workid',
    'replaygain_album_peak',
    'replaygain_album_gain',
    'replaygain_track_peak',
    'replaygain_track_gain'
    ])

""" Map ID3 frames to kantag name. """
id3_read_map = {
    'TALB': 'Album',
    'TXXX:ALBUM ARTIST': 'AlbumArtist',
    'TXXX:ALBUMARTIST': 'AlbumArtist',
    'TPE2': 'AlbumArtist',
    'TXXX:ALBUMARTISTNONSORT': 'AlbumArtistNonSort',
    'TXXX:ALBUMARTISTSORT': 'AlbumArtistSort',
    'TSO2': 'AlbumArtistSort',
    'TXXX:ALBUMARTISTS': 'AlbumArtists',
    'TXXX:ALBUMARTISTSSORT': 'AlbumArtistsSort',
    'TXXX:ALBUMVERSION': 'AlbumVersion',
    'TXXX:AMAZON_ID': 'AmazonId',
    'TXXX:ARRANGER': 'Arranger',
    'TXXX:ARRANGERSORT': 'ArrangerSort',
    'TPE4': 'Arranger',
    'TPE1': 'Artist',
    'TXXX:ARTISTSORT': 'ArtistSort',
    'TXXX:ARTISTNONSORT': 'ArtistNonSort',
    'TSOP': 'ArtistSort',
    'TXXX:ARTISTS': 'Artists',
    'TXXX:COLLECTION': 'Collection',
    'TXXX:COMMENT': 'Comment',
    'COMM': 'Comment',
    'TCOM': 'Composer',
    'TSOC': 'ComposerSort',
    'TXXX:COMPOSERSORT': 'ComposerSort',
    'TPE3': 'Conductor',
    'TXXX:CONDUCTORSORT': 'ConductorSort',
    'TXXX:COVERNUMBER': 'CoverNumber',
    'TDRC': 'Date',
    'TXXX:DATE': 'Date',
    'TPOS': 'DiscNumber',
    'TSST': 'DiscSubtitle',
    'TSRC': 'ISRC',
    'TCON': 'Genre',
    'TPUB': 'Label',
    'TXXX:LABELID': 'LabelId',
    'TXXX:BARCODE': 'Barcode',
    'TXXX:CATALOGNUMBER': 'CatalogNumber',
    'TXXX:ASIN': 'LabelId',
    'TLAN': 'Language',
    'TEXT': 'Lyricist',
    'TOLY': 'Lyricist',
    'TXXX:LYRICISTSORT': 'LyricistSort',
    'TMED': 'Media',
    'TDOR': 'OriginalDate',
    'TXXX:ORIGINALYEAR': 'OriginalDate',
    'TXXX:PART': 'Part',
    'TXXX:PERFORMER': 'Performer',
    'TMCL': 'Performer',
    'TXXX:PERFORMERSORT': 'PerformerSort',
    'TXXX:MUSICBRAINZ ALBUM RELEASE COUNTRY': 'ReleaseCountry',
    'TXXX:MUSICBRAINZ ALBUM STATUS': 'ReleaseStatus',
    'TXXX:MUSICBRAINZ ALBUM TYPE': 'ReleaseType',
    'TXXX:SCRIPT': 'Script',
    'TXXX:SORTDATE': 'SortDate',
    'TIT2': 'Title',
    'TRCK': 'TrackNumber',
    'TIT3': 'Version',
    'TXXX:VERSION': 'Version',
    'TXXX:WORK': 'Work',
    'TOAL': 'Work',
    'TXXX:WRITER': 'Writer',
    'TXXX:WRITERSORT': 'WriterSort',
    'TCMP': 'Compilation',
    'TIPL': 'Person', # See TIPL map below.
    'TXXX:MUSICBRAINZ ALBUM ID': 'musicbrainz_albumid',
    'TXXX:MUSICBRAINZ ALBUM ARTIST ID': 'musicbrainz_albumartistid',
    'TXXX:MUSICBRAINZ ARTIST ID': 'musicbrainz_artistid',
    'TXXX:MUSICBRAINZ DISC ID': 'musicbrainz_discid',
    'TXXX:MUSICBRAINZ RELEASE GROUP ID': 'musicbrainz_releasegroupid',
    'TXXX:MUSICBRAINZ RELEASE TRACK ID': 'musicbrainz_releasetrackid',
    'UFID:HTTP://MUSICBRAINZ.ORG': 'musicbrainz_trackid',
    'TXXX:MUSICBRAINZ WORK ID': 'musicbrainz_workid',
    'TXXX:MUSICBRAINZ TRACK ID': 'musicbrainz_trackid',
    'TXXX:MUSICBRAINZ_TRACKID': 'musicbrainz_trackid',
    'TXXX:REPLAYGAIN_ALBUM_PEAK': 'replaygain_album_peak',
    'TXXX:REPLAYGAIN_ALBUM_GAIN': 'replaygain_album_gain',
    'TXXX:REPLAYGAIN_TRACK_PEAK': 'replaygain_track_peak',
    'TXXX:REPLAYGAIN_TRACK_GAIN': 'replaygain_track_gain',
    'TXXX:ACOUSTID ID': 'acoustid_id',
    'APIC': 'EmbeddedImage'
    }

""" Map non-ID3 tags from, e.g., Picard to cannonical names. """
# Note that the destination value should be something in cannonical_tags.
general_read_map = {
    'remixer': 'Arranger',
    'djmixer': 'Arranger',
    'disctotal': 'TotalDiscs',
    'tracktotal': 'TotalTracks',
    'metadata_block_picture': 'EmbeddedImage',
    'r128_track_gain' : 'replaygain_track_gain',
    'r128_album_gain' : 'replaygain_album_gain'
    }

""" Map TIPL involvements to kantag name. """
tipl_map = {
    'dj-mix': 'DJMixer',
    'mix': 'Mixer'
    }

""" Map kantag name to ID3 frame. """
id3_write_map = {
    'Album': 'TALB',
    'AlbumArtist': 'TPE2',
    'Artist': 'TPE1',
    'ArtistSort': 'TSOP',
    # Having more than one COMM with the same content descriptor (third descriptor, after
    #     language) can cause problems with, for example, foobar2000. "There may be more
    #     than one comment frame in each tag, but only one with the same language and
    #     content descriptor."
    # 'Comment': 'COMM::eng', # having more than one with the same content
    'Comment': 'TXXX:COMMENT',
    'Compilation': 'TCMP',
    'Composer': 'TCOM',
    'ComposerSort': 'TSOC',
    'Conductor': 'TPE3',
    'Date': 'TDRC',
    'DiscNumber': 'TPOS',
    'DiscSubtitle': 'TSST',
    'Genre': 'TCON',
    'ISRC': 'TSRC',
    'Language': 'TLAN',
    'Lyricist': 'TEXT',
    'OriginalDate': 'TDOR',
    'Title': 'TIT2',
    'TrackNumber': 'TRCK',
    'musicbrainz_albumid': 'TXXX:MusicBrainz Album Id',
    'musicbrainz_albumartistid': 'TXXX:MusicBrainz Album Artist Id',
    'musicbrainz_artistid': 'TXXX:MusicBrainz Artist Id',
    'musicbrainz_discid': 'TXXX:MusicBrainz Disc Id',
    'musicbrainz_releasegroupid': 'TXXX:MusicBrainz Release Group Id',
    'musicbrainz_releasetrackid': 'TXXX:MusicBrainz Release Track Id',
    'musicbrainz_trackid': ['UFID:http://musicbrainz.org', 'TXXX:MusicBrainz Track Id'],
    'musicbrainz_workid': 'TXXX:MusicBrainz Work Id',
    'replaygain_album_peak': 'TXXX:replaygain_album_peak',
    'replaygain_album_gain': 'TXXX:replaygain_album_gain',
    'replaygain_track_peak': 'TXXX:replaygain_track_peak',
    'replaygain_track_gain': 'TXXX:replaygain_track_gain',
    'acoustid_id': 'TXXX:ACOUSTID ID'
    # Anything not explicitly listed maps to TXXX:<WHATEVER>
    }

""" Additional freeform items for writing to MP4/M4A. """
mp4_map = {
    # Note: 'albumartistsort' is supported by EasyMP4, but with default settings foobar2000 will
    #       map 'soaa' as ALBUMARTISTSORTORDER.
    'albumartistsort': 'albumartistsort',
    'albumartists': 'albumartists',
    'albumartistssort': 'albumartistssort',
    'arranger': 'arranger',
    'arrangersort': 'arrangersort',
    'composer': 'composer',
    # Note: 'composersort' is supported by EasyMP4, but with default settings foobar2000 will map
    #       'soco' as COMPOSERSORTORDER.
    'composersort': 'composersort',
    'conductor': 'conductor',
    'conductorsort': 'conductorsort',
    'covernumber': 'covernumber',
    'discsubtitle': 'discsubtitle',
    'labelid': 'labelid',
    'lyricist': 'lyricist',
    'lyricistsort': 'lyricistsort',
    'originaldate': 'originaldate',
    'part': 'part',
    'performer': 'performer',
    'performersort': 'performersort',
    'sortdate': 'sortdate',
    'version': 'version',
    'work': 'work',
    'writer': 'writer',
    'writersort': 'writersort',
    'MusicBrainz Disc Id': 'musicbrainz_disc_id',
    'MusicBrainz Release Group Id': 'musicbrainz_releasegroupid',
    'MusicBrainz Release Track Id': 'musicbrainz_releasetrackid',
    'MusicBrainz Track Id' : 'musicbrainz_trackid',
    'MusicBrainz Work Id': 'musicbrainz_workid',
    'replaygain_album_peak': 'replaygain_album_peak',
    'replaygain_album_gain': 'replaygain_album_gain',
    'replaygain_track_peak': 'replaygain_track_peak',
    'replaygain_track_gain': 'replaygain_track_gain',
    'Acoustid Id': 'acoustid_id'
}

""" Additional cannonical to Vorbis map. """
vorbis_write_map = { }

""" Additional cannonical to FLAC map. """
flac_write_map = { }

""" Additional cannonical to Opus map. """
opus_write_map = {
    'replaygain_track_gain' : 'R128_TRACK_GAIN',
    'replaygain_album_gain' : 'R128_ALBUM_GAIN'
}
