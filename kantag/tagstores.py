# tagstores.py - kantag heirachical metadata containers and builders.
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
import re
import sys
import os.path
import pprint
from tagset import TagSet
import audiofile, musicbrainz

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
            self._tags[u'TrackNumber'] = [number]

    # ----------------------------------------------------------------------------------------------
    @property
    def number(self):
        """Track number."""
        return self._tags[u'TrackNumber'][0] if u'TrackNumber' in self._tags else None
    @number.setter
    def number(self, value):
        self._tags[u'TrackNumber'] = [value]

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
            self._tags[u'DiscNumber'] = [number]
        self._is_single_artist = None
        self._is_various = None

    # ----------------------------------------------------------------------------------------------
    @property
    def number(self):
        """Disc number."""
        return self._tags[u'DiscNumber'][0] if u'DiscNumber' in self._tags else None
    @number.setter
    def number(self, value):
        self._tags[u'DiscNumber'] = [value]

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
    def __init__(self, entity=None):
        self._entity = entity

    # ----------------------------------------------------------------------------------------------
    def apply_musicbrainz_relation(self, rel):
        """
        Apply a musicbrainz Relation to the given TagSet.
        """
        # If the tag already contains this sortname for this particular arist, we'll replace it with
        # the regular name, and vice versa (useful for working with some legacy data).
        entity = self._entity
        entity.tags.append_replace(rel.type, rel.sortname, rel.name)
        entity.tags.append_replace(rel.type + u'Sort', rel.name, rel.sortname)

    # ----------------------------------------------------------------------------------------------
    def _set_artist_statuses(self, common_values, various):
        """
        Set is_single_artist and is_various flags based on the common values produced in an entity
        merge operation.  If it's determined that this is a VA entity, then AlbumArtist and
        AlbumArtistSort tags may get added to the common values.
        """
        entity = self._entity
        if entity.is_single_artist is None:
            entity.is_single_artist = u'Artist' in common_values
        entity.is_various = \
            not entity.is_single_artist and \
            (u'AlbumArtist' not in common_values or \
            u'Various Artists' in common_values[u'AlbumArtist'] or \
            u'Various' in common_values[u'AlbumArtist'] or \
            various in common_values[u'AlbumArtist'])
        if entity.is_various and not u'AlbumArtist' in common_values:
            entity.tags.append(u'AlbumArtist', various)
            entity.tags.append(u'AlbumArtistSort', various)

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
    def __init__(self, track=None):
        _TagStoreBuilder.__init__(self, track)
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
            if u'Artist' not in tags and 'artist' in parts and parts['artist'] != '':
                tags[u'Artist'] = [parts['artist']]
            if u'Album' not in tags and 'album' in parts and parts['album'] != '':
                tags[u'Album'] = [parts['album']]
            if u'Date' not in tags and 'date' in parts and parts['date'] != '':
                tags[u'Date'] = [parts['date']]
            if u'DiscNumber' not in tags and 'disc' in parts and parts['disc'] != '':
                tags[u'DiscNumber'] = [parts['disc']]
            if u'TrackNumber' not in tags and 'track' in parts and parts['track'] != '':
                tags[u'TrackNumber'] = [parts['track'].zfill(2)]
            # Also want to see if the existing title is a generic value like "Track 5".
            if (u'Title' not in tags or tags[u'Title'][0][0:6] == 'Track ') and \
                'title' in parts and parts['title'] !='':
                tags[u'Title'] = [parts['title']]
        else:
            if u'Title' not in tags:
                tags[u'Title'] = [os.path.splitext(os.path.basename(path))[0]]

    # ----------------------------------------------------------------------------------------------
    def split_disc_title(self):
        """
        Parse a musicbrainz-style disc title into title and disc number/subtitle.
        """
        tags = self.track.tags
        if u'Album' in tags:
            for title in tags[u'Album']:
                parsed = musicbrainz.parse_album_title(title)
                if parsed.discnum is not None:
                    tags[u'Album'] = [parsed.title]
                    tags[u'DiscNumber'] = [parsed.discnum]
                if parsed.subtitle is not None:
                    tags[u'DiscSubtitle'] = [parsed.subtitle]

    # ----------------------------------------------------------------------------------------------
    def split_title_to_work_and_parts(self, classical):
        """
        Parse a musicbrainz-style title into work and part.
        """
        tags = self.track.tags
        if u'Title' in tags:
            for title in tags[u'Title']:
                parsed = musicbrainz.parse_track_title(title)
                if parsed.parts is not None:
                    tags.remove(u'Title', title)
                    if parsed.work is not None:
                        tags.append_unique(u'Work', parsed.work)
                    for part in parsed.parts:
                        tags.append_unique(u'Part', part)
                if u'Work' not in tags and classical:
                    tags.move_values(u'Title', u'Work')

    # ----------------------------------------------------------------------------------------------
    def remove_instruments(self):
        """
        Remove instrument/role information from Performer tags.
        """
        tags = self.track.tags
        if u'Performer' in tags:
            tags[u'Performer'] = musicbrainz.remove_artist_roles(tags[u'Performer'])

    # ----------------------------------------------------------------------------------------------
    def apply_musicbrainz(self):
        """
        Call the musicbrainz service and apply results to the Track. The track tags must contain a
        'musicbrainz_trackid' value.
        """
        tags = self.track.tags
        if u'musicbrainz_trackid' in tags:
            for mbid in tags['musicbrainz_trackid']:
                mbtrack = musicbrainz.get_track_by_id(mbid)
                for rel in musicbrainz.get_track_artist_relations(mbtrack):
                    self.apply_musicbrainz_relation(rel)

# --------------------------------------------------------------------------------------------------
class DiscBuilder(_TagStoreBuilder):
    """
    Helper for building a Disc from files.
    """
    def __init__(self, disc=None):
        _TagStoreBuilder.__init__(self, disc)
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

    # ----------------------------------------------------------------------------------------------
    def apply_musicbrainz(self):
        """
        Call the musicbrainz service and apply results to the Disc. The disc tags must contain a
        'musicbrainz_albumid' value.
        """

        # TODO: At some time in the future, this should be moved to the release level.
        # Musicbrainz album IDs are now tied to the release, not the disc.  So the existing code
        # will end up feching the same release metadata for each disc, and those will all get
        # merged to the release level.  Although it seems you could immediately move this operation
        # to the release level and get the same result, the problem is the pre-NGS IDs stored in
        # existing files.  Pre-NGS, each disc will have a different album ID, which will *not*
        # merge up to release level, so when querying for 'musicbrainz_albumid' at the release
        # level, you'll get nothing.

        tags = self.disc.tags
        if u'musicbrainz_albumid' in tags:
            for mbid in tags[u'musicbrainz_albumid']:
                # Call the web service.
                release = musicbrainz.get_release_by_id(mbid)
                self.disc.is_single_artist = release.isSingleArtistRelease()

                # Parse the album title in case it is a musicbrainz-style multi-disc title.
                parsed = musicbrainz.parse_album_title(release.title)
                if parsed.discnum is not None:
                    tags[u'Album'] = [parsed.title]
                    tags[u'DiscNumber'] = [parsed.discnum]
                if parsed.subtitle is not None:
                    tags[u'DiscSubtitle'] = [parsed.subtitle]

                # Get the date of the earliest release date (US preferred).
                date = musicbrainz.get_earliest_release(release)
                if date is not None:
                    if u'Date' not in tags:
                        tags[u'Date'] = [date]
                    elif date != tags[u'Date'][0] and u'OriginalDate' not in tags:
                        tags[u'OriginalDate'] = [date]

                # Add the artist relations using sortnames.
                for rel in musicbrainz.get_release_artist_relations(release):
                    self.apply_musicbrainz_relation(rel)

# --------------------------------------------------------------------------------------------------
class ReleaseBuilder(_TagStoreBuilder):
    """
    Helper for building a Release heirarchy from files.
    """
    def __init__(self, options, release=None):
        _TagStoreBuilder.__init__(self, release)
        self._options = options
        if self._entity is None:
            self._entity = Release()

    # ----------------------------------------------------------------------------------------------
    @property
    def release(self):
        """The underlying Release object."""
        return self._entity

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
        builder = TrackBuilder()
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

        # Parse track title into work/part.
        if self._options.parse_title:
            builder.split_title_to_work_and_parts(self._options.classical)

        # Temporarily make sure everything is 'Various Artists' so we don't have issues with unique
        # appends or replaces with mismatched values.
        tags = builder.track.tags
        tags.replace(u'AlbumArtist', u'Various', u'Various Artists')
        tags.replace(u'AlbumArtist', self._options.various, u'Various Artists')
        tags.replace(u'AlbumArtistSort', u'Various', u'Various Artists')
        tags.replace(u'AlbumArtistSort', self._options.various, u'Various Artists')
        tags.replace(u'AlbumArtists', u'Various', u'Various Artists')
        tags.replace(u'AlbumArtists', self._options.various, u'Various Artists')
        tags.replace(u'AlbumArtistsSort', u'Various', u'Various Artists')
        tags.replace(u'AlbumArtistsSort', self._options.various, u'Various Artists')

        # Add artist relations from musicbrainz to the track tags.
        if self._options.call_musicbrainz:
            builder.apply_musicbrainz()

        return builder.track

    # ----------------------------------------------------------------------------------------------
    def _get_disc(self, track):
        """
        Build and/or return a Disc matching the given Track.  If a new Disc is needed, it is added
        to the release.  The Track is added to the Disc.
        """
        release = self.release

        # Check if this is the first encounter with a certain disc number.
        discnum = (track.tags[u'DiscNumber'][0] if u'DiscNumber' in track.tags else None)
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
                print >> sys.stderr, filename

            # Fetch the tags that are stored in the file/path.
            track = self._get_track(filename)

            # Get a new or existing Disc matching the track.
            disc = self._get_disc(track)
            disc.tracks.append(track)

        for disc in release.discs:
            # Merge values that are common to all tracks in a disc into the disc tags.
            dbuilder = DiscBuilder(disc)
            dbuilder.merge_tracks(self._options.various, self._options.keep_common)

            # Populate the disc tags with musicbrainz data.  Note we want to do that after merging
            # the track common values, rather than on initialization of the disc.  If populated at
            # init, names/sortnames in the source file would be in track tags, not get corrected by
            # the track AR processing (they're not track ARs), and then get merged after-the-fact
            # into the disc tags (which were already corrected by release AR processing).
            if self._options.call_musicbrainz:
                dbuilder.apply_musicbrainz()

        # Merge values that are common to all discs in the release into the release tags.
        self.merge_discs()

        # Set the final "Various Artists"/"Various" values.
        release.replace_all(u'AlbumArtist', u'Various Artists', self._options.various)
        release.replace_all(u'AlbumArtistSort', u'Various Artists', self._options.various)
        release.replace_all(u'AlbumArtists', u'Various Artists', self._options.various)
        release.replace_all(u'AlbumArtistsSort', u'Various Artists', self._options.various)

        return release
