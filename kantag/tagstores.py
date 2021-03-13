# tagstores.py - kantag heirachical metadata containers and builders.
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
import re
import sys
import os.path
import warnings
import pprint
from .tagset import TagSet
from . import audiofile, util, textencoding
try:
    from . import musicbrainz as mb
except ImportError:
    mb = None

# --------------------------------------------------------------------------------------------------
class TagStore(object):
    """
    Base class that exposes an internal TagSet as a tags property.
    """
    def __init__(self):
        self._tags = TagSet()
        self._children = []

    # ----------------------------------------------------------------------------------------------
    @property
    def tags(self):
        """A TagSet of tag-values that apply to the entity."""
        return self._tags
    @tags.setter
    def tags(self, value):
        self._tags = value

# --------------------------------------------------------------------------------------------------
class Track(TagStore):
    """
    Container for track information and tags.
    """
    def __init__(self, number=None):
        if number is not None:
            self._tags['TrackNumber'] = [number]

    # ----------------------------------------------------------------------------------------------
    @property
    def number(self):
        """Track number."""
        return self._tags['TrackNumber'][0] if 'TrackNumber' in self._tags else None
    @number.setter
    def number(self, value):
        self._tags['TrackNumber'] = [value]

    # ----------------------------------------------------------------------------------------------
    def pprint(self):
        return 'TRACK: ' + (self.number if self.number is not None else 'None') + ':\n' + \
            pprint.PrettyPrinter(indent=2).pformat(self._tags) + '\n'

# --------------------------------------------------------------------------------------------------
class Disc(TagStore):
    """
    Container for disc information, tracks, and tags.
    """
    def __init__(self, number):
        TagStore.__init__(self)
        if number is not None:
            self._tags['DiscNumber'] = [number]
        self._is_single_artist = None
        self._is_various = None

    # ----------------------------------------------------------------------------------------------
    @property
    def number(self):
        """Disc number."""
        return self._tags['DiscNumber'][0] if 'DiscNumber' in self._tags else None
    @number.setter
    def number(self, value):
        self._tags['DiscNumber'] = [value]

    # ----------------------------------------------------------------------------------------------
    @property
    def is_single_artist(self):
        """
        True if the disc has just a single track artist.  Note that a release can have multiple
        track artists without being a Various Artist disc.
        """
        return self._is_single_artist
    @is_single_artist.setter
    def is_single_artist(self, value):
        self._is_single_artist = value

    # ----------------------------------------------------------------------------------------------
    @property
    def is_various(self):
        """True if the disc is Various Artist disc."""
        return self._is_various
    @is_various.setter
    def is_various(self, value):
        self._is_various = value

    # ----------------------------------------------------------------------------------------------
    @property
    def tracks(self):
        """List of Tracks on the disc."""
        return self._children
    @tracks.setter
    def tracks(self, value):
        self._children = value

    # ----------------------------------------------------------------------------------------------
    def replace_all(self, key, replace, replacement):
        """
        Replace a tag values in the disc and all children with a given key/value with a
        replacement value.
        """
        self.tags.replace(key, replace, replacement)
        for track in self.tracks:
            track.tags.replace(key, replace, replacement)

    # ----------------------------------------------------------------------------------------------
    def pprint(self):
        s = 'DISC: ' + (self.number if self.number is not None else 'None') + \
            ' [' + ('Single-artist' if self.is_single_artist else 'Multi-artist') + \
            ('/Various' if self.is_various else '') + ']' + '\n' + \
            pprint.PrettyPrinter(indent=2).pformat(self.tags) + '\n'
        for track in self.tracks:
            s += track.pprint()
        return s

# --------------------------------------------------------------------------------------------------
class Release(TagStore):
    """
    Container for release information, discs, and tags.
    """
    def __init__(self):
        TagStore.__init__(self)
        self._is_single_artist = None
        self._is_various = None

    # ----------------------------------------------------------------------------------------------
    @property
    def is_single_artist(self):
        """
        True if the release has just a single track artist.  Note that a release can have multiple
        track artists without being a Various Artist release.
        """
        return self._is_single_artist
    @is_single_artist.setter
    def is_single_artist(self, value):
        self._is_single_artist = value

    # ----------------------------------------------------------------------------------------------
    @property
    def is_various(self):
        """True if the release is Various Artist release."""
        return self._is_various
    @is_various.setter
    def is_various(self, value):
        self._is_various = value

    # ----------------------------------------------------------------------------------------------
    @property
    def discs(self):
        """List of Discs contained in the release."""
        return self._children
    @discs.setter
    def discs(self, value):
        self._children = value

    # ----------------------------------------------------------------------------------------------
    def replace_all(self, key, replace, replacement):
        """
        Replace a tag values in the release and all children with a given key/value with a
        replacement value.
        """
        self.tags.replace(key, replace, replacement)
        for disc in self.discs:
            disc.replace_all(key, replace, replacement)

    # ----------------------------------------------------------------------------------------------
    def pprint(self):
        s = 'RELEASE [' + ('Single-artist' if self.is_single_artist else 'Multi-artist') + \
            ('/Various' if self.is_various else '') + \
            ('/Multi-disc' if len(self.discs) > 1 else '') + ']' + '\n' + \
            pprint.PrettyPrinter(indent=2).pformat(self.tags) + '\n'
        for disc in self.discs:
            s += disc.pprint() + '\n'
        return s

# --------------------------------------------------------------------------------------------------
class _TagStoreBuilder(object):
    """
    Base class for TagStore build helpers.
    """
    def __init__(self, options, entity=None):
        self._options = options
        self._entity = entity

    # ----------------------------------------------------------------------------------------------
    def apply_musicbrainz_relation(self, relation):
        """
        Apply a musicbrainz Relation to the given TagSet.
        """
        # If the tag already contains this sortname for this particular arist, we'll replace it with
        # the regular name, and vice versa (useful for working with some legacy data).
        entity = self._entity
        entity.tags.append_replace(relation.type, relation.sortname, relation.name)
        entity.tags.append_replace(relation.type + 'Sort', relation.name, relation.sortname)

    # ----------------------------------------------------------------------------------------------
    def apply_musicbrainz_relations(self, relations):
        """
        Apply a list musicbrainz Relation instances to the given TagSet.
        """
        for relation in relations:
            self.apply_musicbrainz_relation(relation)

    # ----------------------------------------------------------------------------------------------
    def _set_artist_statuses(self, common_values, various):
        """
        Set is_single_artist and is_various flags based on the common values produced in an entity
        merge operation.  If it's determined that this is a VA entity, then AlbumArtist and
        AlbumArtistSort tags may get added to the common values.
        """
        entity = self._entity
        if entity.is_single_artist is None:
            entity.is_single_artist = 'Artist' in common_values
        entity.is_various = \
            not entity.is_single_artist and \
            ('AlbumArtist' not in common_values or \
            'Various Artists' in common_values['AlbumArtist'] or \
            'Various' in common_values['AlbumArtist'] or \
            various in common_values['AlbumArtist'])
        if entity.is_various and not 'AlbumArtist' in common_values:
            entity.tags.append('AlbumArtist', various)
            entity.tags.append('AlbumArtistSort', various)

    # ----------------------------------------------------------------------------------------------
    def _merge_children(self, various, keep_common):
        """
        Add tag/value pairs that are common to all children to the entity.
        """
        # First get the common values and add them to the entity tags.
        entity = self._entity
        common_values = TagSet.get_common_values([child.tags for child in entity._children])
        entity.tags.merge_unique(common_values)

        # If the single-artist/various statuses couldn't be determined by a earlier edits, then look
        # look for a common artist tag, and set the property values for convenience.
        self._set_artist_statuses(common_values, various)

        # Remove the common child values from the originating children.
        for child in entity._children:
            child.tags.remove_dict(common_values)

# --------------------------------------------------------------------------------------------------
class TrackBuilder(_TagStoreBuilder):
    """
    Helper for building a Track object from a file.
    """
    def __init__(self, options, track=None):
        _TagStoreBuilder.__init__(self, options, track)
        if self._entity is None:
            self._entity = Track()

    # ----------------------------------------------------------------------------------------------
    @property
    def track(self):
        """The underlying Track object."""
        return self._entity

    # ----------------------------------------------------------------------------------------------
    def read(self, filename):
        """
        Read tags from file.  This will overwrite any existing tags.
        """
        self.track.tags = audiofile.read(filename)

    # ----------------------------------------------------------------------------------------------
    def infer_from_path(self, filename, regex):
        """
        Use file path to add missing artist, album, date, discnumber, tracknumber, title tags.  If
        the regular expression fails to match, the filename less extension is used as the title.
        """
        path = os.path.abspath(filename)
        match = re.search(regex, path)
        tags = self.track.tags
        if match:
            parts = match.groupdict()
            if 'Artist' not in tags and 'artist' in parts and parts['artist'] != '':
                tags['Artist'] = [parts['artist']]
            if 'Album' not in tags and 'album' in parts and parts['album'] != '':
                tags['Album'] = [parts['album']]
            if 'Date' not in tags and 'date' in parts and parts['date'] != '':
                tags['Date'] = [parts['date']]
            if 'DiscNumber' not in tags and 'disc' in parts and parts['disc'] != '':
                tags['DiscNumber'] = [parts['disc']]
            if 'TrackNumber' not in tags and 'track' in parts and parts['track'] != '':
                tags['TrackNumber'] = [parts['track'].zfill(2)]
            # Also want to see if the existing title is a generic value like "Track 5".
            if ('Title' not in tags or tags['Title'][0][0:6] == 'Track ') and \
                'title' in parts and parts['title'] !='':
                tags['Title'] = [parts['title']]
        else:
            if 'Title' not in tags:
                tags['Title'] = [os.path.splitext(os.path.basename(path))[0]]

    # ----------------------------------------------------------------------------------------------
    def split_disc_title(self):
        """
        Parse a musicbrainz-style disc title into title and disc number/subtitle.
        """
        tags = self.track.tags
        if 'Album' in tags:
            for title in tags['Album']:
                parsed = util.parse_album_title(title)
                if parsed.discnum is not None:
                    tags['Album'] = [parsed.title]
                    tags['DiscNumber'] = [parsed.discnum]
                if parsed.subtitle is not None:
                    tags['DiscSubtitle'] = [parsed.subtitle]

    # ----------------------------------------------------------------------------------------------
    def split_title_to_work_and_parts(self, classical):
        """
        Parse a musicbrainz-style title into work and part.
        """
        tags = self.track.tags
        if 'Title' in tags:
            for title in tags['Title']:
                parsed = util.parse_track_title(title)
                if parsed.parts is not None:
                    tags.remove('Title', title)
                    if parsed.work is not None:
                        #tags.append_unique(u'Work', parsed.work)
                        tags['Work'] = [parsed.work]
                    for part in parsed.parts:
                        tags.append_unique('Part', part)
                if 'Work' not in tags and classical:
                    tags.move_values('Title', 'Work')

    # ----------------------------------------------------------------------------------------------
    def remove_instruments(self):
        """
        Remove instrument/role information from Performer tags.
        """
        tags = self.track.tags
        if 'Performer' in tags:
            tags['Performer'] = util.remove_artist_roles(tags['Performer'])

    # ----------------------------------------------------------------------------------------------
    def _apply_release_data(self, mb_release):
        """
        Apply release-level musicbrainz metadata to track tags.
        """
        tags = self.track.tags

        if self._options.verbose >= 3:
            pprint.pprint(mb_release, stream=sys.stderr)

        tags['musicbrainz_albumid'] = [mb_release['id']]
        tags['musicbrainz_releasegroupid'] = [mb_release['release-group']['id']]
        tags['musicbrainz_albumartistid'] = \
            [ac['artist']['id'] for ac in mb_release['artist-credit']]

        #for ac in mb_release['artist-credit']:
        #    tags.append_unique('musicbrainz_albumartistid', ac['artist']['id'])
            
        artists = mb.get_artists(mb_release, self._options.locale)
        tags['AlbumArtists'] = [artist.name for artist in artists]
        tags['AlbumArtistsSort'] = [artist.sortname for artist in artists]
        if len(artists) == 1:
            tags['AlbumArtist'] = [artists[0].name]
            tags['AlbumArtistSort'] = [artists[0].sortname]

        tags['Album'] = [mb_release['title']]
        
        # Use the earliest (US) release date and earliest release group release date.
        date = mb.get_earliest_release(mb_release)
        if date is not None:
            tags['Date'] = [date]
        orig_date = mb.get_earliest_rg_release(mb_release)
        if orig_date is not None:
            if 'Date' in tags:
                if orig_date != tags['Date'][0]:
                    tags['OriginalDate'] = [orig_date]
            else:
                tags['Date'] = [date]
        
        # Barcode, ASIN, CatalogNumber.
        if 'asin' in mb_release:
            tags['ASIN'] = [mb_release['asin']]
        if 'barcode' in mb_release and mb_release['barcode'] != '':
            tags['Barcode'] = [mb_release['barcode']]
        catnum = mb.get_release_catalognumber(mb_release)
        if not catnum is None:
            tags['CatalogNumber'] = [catnum]
        
        # Add the artist relations using sortnames.
        self.apply_musicbrainz_relations(mb.get_artist_relations(mb_release, self._options.locale))
        
    # ----------------------------------------------------------------------------------------------
    def _apply_medium_data(self, mb_medium):
        """
        Apply medium-level musicbrainz metadata to track tags.
        """
        tags = self.track.tags
        if 'title' in mb_medium:
            tags['DiscSubtitle'] = [mb_medium['title']]

    # ----------------------------------------------------------------------------------------------
    def _apply_track_data(self, mb_track):
        """
        Apply track-level musicbrainz metadata to track tags.  Returns whether a track title was
        found.
        """
        tags = self.track.tags

        tags['musicbrainz_releasetrackid'] = [mb_track['id']]
        tags['musicbrainz_artistid'] = [ac['artist']['id'] for ac in mb_track['artist-credit']]

        found_title = ('title' in mb_track)
        if found_title:
            tags['Title'] = [mb_track['title']]

        artists = mb.get_artists(mb_track, self._options.locale)
        tags['Artists'] = [artist.name for artist in artists]
        tags['ArtistsSort'] = [artist.sortname for artist in artists]
        if len(artists) == 1:
            tags['Artist'] = [artists[0].name]
            tags['ArtistSort'] = [artists[0].sortname]
        
        return found_title

    # ----------------------------------------------------------------------------------------------
    def _apply_recording_data(self, mb_recording, apply_title):
        """
        Apply recording-level musicbrainz metadata to the track tags.  'apply_title' indicates
        whether recording title should overwrite an existing title tag.
        """
        tags = self.track.tags

        tags['musicbrainz_trackid'] = [mb_recording['id']]

        tags['RecordingTitle'] = [mb_recording['title']]
        if (not 'Title' in tags or apply_title) and 'title' in mb_recording:
            tags['Title'] = [mb_recording['title']]
        if 'disambiguation' in mb_recording and mb_recording['disambiguation'] != '':
            tags.append_unique('Version', mb_recording['disambiguation'])

        # Add the artist relations using sortnames.
        locale = self._options.locale
        self.apply_musicbrainz_relations(mb.get_artist_relations(mb_recording, locale))

    # ----------------------------------------------------------------------------------------------
    def _apply_work_data(self, mb_work, recurse, apply_title):
        """
        Apply work-level musicbrainz metadata to the track tags.  'apply_title' indicates whether
        the work tile hould be appended to the 'Work' and/or 'Part' tags.  'recuse' indicates
        whether to follow available links to related works, potentially enhancing available
        work/part data.
        """
        tags = self.track.tags

        tags.append_unique('musicbrainz_workid', mb_work['id'])

        if apply_title:
            title = mb_work['title']
            if self._options.parse_title:
                parsed = util.parse_track_title(title)
                if parsed.parts is not None:
                    if parsed.work is not None:
                        tags.append_unique('Work', parsed.work)
                    for part in parsed.parts:
                        tags.append_unique('Part', part)
            else:
                tags.append_unique('Work', title)


        # Add the artist relations using sortnames.
        rels = mb.get_work_artist_relations(mb_work, recurse, self._options.locale)
        self.apply_musicbrainz_relations(rels)

    # ----------------------------------------------------------------------------------------------
    def apply_musicbrainz(self, mbdata):
        """
        Apply musicbrainz metadata to the track tags.  'mbdata' should be a release instance
        returned by the musicbrainz API.  The track needs 'TrackNumber' and 'DiscNumber' tags to
        receive medium, track, recording, and work metadata.
        """
        # Bail out of musicbrainz is not available.
        if mb is None:
            print('warning: musicbrainz package is not available', file=sys.stderr)
        
        # Note: All data is initially loaded into track tags - from existing tags, inferred from
        # path, etc.  On the other hand, musicbrainz data is hierarchical.  Which means, in order
        # to edit existing data with musicbrainz data, we need to either first merge track data to
        # "unflatten" before applying musicbrainz data, or first "flatten" the musicbrainz data to
        # track level.  Earlier revisions used the former approach, but this didn't always work out
        # as desired, and was more difficult to implement.  Now, we use the latter approach, and
        # rely on the built-in "merging" logic rebuild the heirarchy post-edit.  Thus, musicbrainz
        # data is applied to track objects only.

        tags = self.track.tags
        
        self._apply_release_data(mbdata)
        medium_num = (tags['DiscNumber'][0] if 'DiscNumber' in tags else '1')
        mb_medium = mb.get_release_medium(mbdata, medium_num)
        if not mb_medium is None:
            self._apply_medium_data(mb_medium)

            mb_track = None
            if self.track.number is None:
                print('warning: file track number unknown; cannot match to musicbrainz',
                    file=sys.stderr)
            else:
                mb_track = mb.get_medium_track(mb_medium, self.track.number)
            if not mb_track is None:
                # If the track title matches the recording title, then the API will not include a
                # title on the track, so we need to pull it from the recording instead.
                found_title = self._apply_track_data(mb_track)

                mb_recording = mb.get_track_recording(mb_track)
                if not mb_recording is None:
                    self._apply_recording_data(mb_recording, not found_title)

                    # Only apply the work title from the first.
                    apply_title = True
                    for mb_work in mb.get_recording_works(mb_recording):
                        # TODO: Make work recursion an option.
                        self._apply_work_data(mb_work, False, apply_title)
                        apply_title = False

# --------------------------------------------------------------------------------------------------
class DiscBuilder(_TagStoreBuilder):
    """
    Helper for building a Disc from files.
    """
    def __init__(self, options, disc=None):
        _TagStoreBuilder.__init__(self, options, disc)
        if self._entity is None:
            self._entity = Disc()

    # ----------------------------------------------------------------------------------------------
    @property
    def disc(self):
        """The underlying Disc object."""
        return self._entity

    # ----------------------------------------------------------------------------------------------
    def merge_tracks(self, various, keep_common):
        """
        Add tag/value pairs that are common to all tracks to the disc.
        """
        self._merge_children(various, keep_common)

# --------------------------------------------------------------------------------------------------
class ReleaseBuilder(_TagStoreBuilder):
    """
    Helper for building a Release heirarchy from files.
    """
    def __init__(self, options, release=None):
        _TagStoreBuilder.__init__(self, options, release)
        self._musicbrainz_data = None
        if self._entity is None:
            self._entity = Release()

    # ----------------------------------------------------------------------------------------------
    @property
    def release(self):
        """The underlying Release object."""
        return self._entity

    # ----------------------------------------------------------------------------------------------
    @property
    def musicbrainz_data(self):
        """MusicBrainz API data about the release."""
        return self._musicbrainz_data
    @musicbrainz_data.setter
    def musicbrainz_data(self, value):
        self._musicbrainz_data = value

    # ----------------------------------------------------------------------------------------------
    def merge_discs(self):
        """
        Add tag/value pairs that are common to all discs to the release.
        """
        self._merge_children(self._options.various, self._options.keep_common)

    # ----------------------------------------------------------------------------------------------
    def _get_track(self, filename):
        """
        Get the tags for file sourced from the existing tags in the file, the filename and path (if
        the existing tags have gaps and can be inferred from filename/path).  Also does some release
        and track title parsing based on musicbrainz-originated titles.
        """
        builder = TrackBuilder(self._options)
        builder.read(filename)

        # Fill in gaps using filename/path.
        if self._options.infer_from_path:
            builder.infer_from_path(filename, self._options.path_regex)

        # Remove roles from artist names.
        if self._options.remove_instruments:
            builder.remove_instruments()

        # Parse the album title in case it is a musicbrainz-style multi-disc title.
        if self._options.parse_disc:
            builder.split_disc_title()

        # Temporarily make sure everything is 'Various Artists' so we don't have issues with unique
        # appends or replaces with mismatched values.
        tags = builder.track.tags
        tags.replace('AlbumArtist', 'Various', 'Various Artists')
        tags.replace('AlbumArtist', self._options.various, 'Various Artists')
        tags.replace('AlbumArtistSort', 'Various', 'Various Artists')
        tags.replace('AlbumArtistSort', self._options.various, 'Various Artists')
        tags.replace('AlbumArtists', 'Various', 'Various Artists')
        tags.replace('AlbumArtists', self._options.various, 'Various Artists')
        tags.replace('AlbumArtistsSort', 'Various', 'Various Artists')
        tags.replace('AlbumArtistsSort', self._options.various, 'Various Artists')

        # Note: Some old musicbrainz metadata will have a different albumid for each disc in a
        # multi-disc release.  This is an artifact of the days when musicbrainz represented each
        # disc as a different release.  However, the API will return the same full release metadata
        # for either mbid.
        if self._options.call_musicbrainz and self.musicbrainz_data is None:
            release_id = self._options.release_mbid
            if release_id is None and 'musicbrainz_albumid' in tags:
                release_id = tags['musicbrainz_albumid'][0]
            if release_id is None:
                print('warning: no release id available for musicbrainz lookup', file=sys.stderr)
            else:
                self.musicbrainz_data = mb.get_release_by_id(release_id)

        if not self.musicbrainz_data is None:
            builder.apply_musicbrainz(self.musicbrainz_data)

        # Parse track title into work/part.
        if self._options.parse_title:
            builder.split_title_to_work_and_parts(self._options.classical)

        # All track data is now loaded.  Apply optional removing of non-ASCII punctuation.
        if self._options.ascii_punctuation:
            # For titles.
            tags.apply_to_all('Album', textencoding.asciipunct)
            tags.apply_to_all('DiscSubtitle', textencoding.asciipunct)
            tags.apply_to_all('Title', textencoding.asciipunct)
            tags.apply_to_all('RecordingTitle', textencoding.asciipunct)
            tags.apply_to_all('Work', textencoding.asciipunct)
            tags.apply_to_all('Part', textencoding.asciipunct)
            tags.apply_to_all('Version', textencoding.asciipunct)
            # And for myriad artist tags.
            tags.apply_to_all('AlbumArtist', textencoding.asciipunct)
            tags.apply_to_all('AlbumArtistSort', textencoding.asciipunct)
            tags.apply_to_all('AlbumArtists', textencoding.asciipunct)
            tags.apply_to_all('AlbumArtistsSort', textencoding.asciipunct)
            tags.apply_to_all('Artist', textencoding.asciipunct)
            tags.apply_to_all('ArtistSort', textencoding.asciipunct)
            tags.apply_to_all('Composer', textencoding.asciipunct)
            tags.apply_to_all('ComposerSort', textencoding.asciipunct)
            tags.apply_to_all('Lyricist', textencoding.asciipunct)
            tags.apply_to_all('LyricistSort', textencoding.asciipunct)
            tags.apply_to_all('Writer', textencoding.asciipunct)
            tags.apply_to_all('WriterSort', textencoding.asciipunct)
            tags.apply_to_all('Arranger', textencoding.asciipunct)
            tags.apply_to_all('ArrangerSort', textencoding.asciipunct)
            tags.apply_to_all('Performer', textencoding.asciipunct)
            tags.apply_to_all('PerformerSort', textencoding.asciipunct)
            tags.apply_to_all('Conductor', textencoding.asciipunct)
            tags.apply_to_all('ConductorSort', textencoding.asciipunct)

        return builder.track

    # ----------------------------------------------------------------------------------------------
    def _get_disc(self, track):
        """
        Build and/or return a Disc matching the given Track.  If a new Disc is needed, it is added
        to the release.  The Track is added to the Disc.
        """
        release = self.release

        # Check if this is the first encounter with a certain disc number.
        discnum = (track.tags['DiscNumber'][0] if 'DiscNumber' in track.tags else None)
        if not discnum in [d.number for d in release.discs]:
            # Initialize a new disc object.
            disc = Disc(discnum)
            release.discs.append(disc)
        else:
            disc = [d for d in release.discs if d.number == discnum][0]

        return disc

    # ----------------------------------------------------------------------------------------------
    def read(self, filenames):
        """
        Return a Release object containing the tags from the given files in a heirarchy.  Tag
        sources include existing tags, path information, and musicbrainz API calls.  Many edits are
        applied to conform the data as closely as possible to certain standards.
        """
        release = self.release

        for filename in filenames:
            if self._options.verbose >= 1:
                print(filename, file=sys.stderr)

            # Fetch the tags that are stored in the file/path.
            track = self._get_track(filename)

            # Get a new or existing Disc matching the track.
            disc = self._get_disc(track)
            disc.tracks.append(track)

        for disc in release.discs:
            # Merge values that are common to all tracks in a disc into the disc tags.
            dbuilder = DiscBuilder(self._options, disc)
            dbuilder.merge_tracks(self._options.various, self._options.keep_common)

        # Merge values that are common to all discs in the release into the release tags.
        self.merge_discs()

        # Set the final "Various Artists"/"Various" values.
        release.replace_all('AlbumArtist', 'Various Artists', self._options.various)
        release.replace_all('AlbumArtistSort', 'Various Artists', self._options.various)
        release.replace_all('AlbumArtists', 'Various Artists', self._options.various)
        release.replace_all('AlbumArtistsSort', 'Various Artists', self._options.various)

        return release
