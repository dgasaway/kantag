# musicbrainz.py - kantag musicbrainz operations.
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
import time
import re
import collections
import musicbrainz2.webservice as ws

# Globals
_mbz_reltype_map = {
    'Arranger'           : u'Arranger',
    'Composer'           : u'Composer',
    'Conductor'          : u'Conductor',
    'ChorusMaster'       : u'Conductor',
    'Instrument'         : u'Performer',
    'Instrumentator'     : u'Arranger',
    'Lyricist'           : u'Lyricist',
    'Librettist'         : u'Lyricist',
    'Orchestrator'       : u'Arranger',
    'Performer'          : u'Performer',
    'PerformingOrchestra': u'Performer',
    'Programmer'         : u'Performer',
    'Remixer'            : u'Arranger',
    'Vocal'              : u'Performer',
    'Writer'             : u'Writer'
    }

NameRole = collections.namedtuple('NameRole', 'name, role')
WorkParts = collections.namedtuple('WorkParts', 'work, parts')
AlbumTitle = collections.namedtuple('AlbumTitle', 'title, discnum, subtitle')
Relation = collections.namedtuple('Relation', 'type, name, sortname')

# --------------------------------------------------------------------------------------------------
def get_release_by_id(releaseid):
    """
    Call the musicbrainz API and return the Release object matching the releaseid.
    """
    # Run the query (pause required by the API).
    time.sleep(1.2)
    q = ws.Query()
    includes = ws.ReleaseIncludes(
        artist=True, artistRelations=True, releaseEvents=True, tracks=True)
    return q.getReleaseById(releaseid, includes)

# --------------------------------------------------------------------------------------------------
def get_track_by_id(trackid):
    """
    Call the musicbrainz API and return the Track object matching the trackid.
    """
    # Run the query (pause required by the API).
    time.sleep(1.2)
    q = ws.Query()
    return q.getTrackById(trackid, ws.TrackIncludes(artist=True, artistRelations=True))

# --------------------------------------------------------------------------------------------------
def parse_artist_role(artist):
    """
    Parse a musicbrainz-style performer name/role string into parts.  The result is a NamedRole
    named tuple.
    """
    match = re.match(r'^(?P<name>[^(]*) \((?P<role>.*)\)$', artist)
    if match:
        return NameRole(match.group('name'), match.group('role'))
    else:
        return NameRole(artist, None)

# --------------------------------------------------------------------------------------------------
def parse_track_title(full_title):
    """
    Parse a musicbrainz-style track title into work and parts.  The result is a WorkParts named
    tuple.
    """
    work = None
    match = re.match(r'^(?P<work>[^:]+): (?P<parts>.+)$', full_title)
    if match:
        work = match.group('work')
        s = match.group('parts')
    else:
        s = full_title

    parts = None
    if s.find(' / ') > -1:
        parts = s.split(' / ')
    elif work is not None:
        parts = [s]

    return WorkParts(work, parts)

# --------------------------------------------------------------------------------------------------
def parse_album_title(full_title):
    """
    Parse a musicbrainz-style release title into a tuple containing the release title, the disc
    number, and the disc subtitle.  The result is an AlbumTitle named tuple.
    """
    match = re.match(r'(?P<title>.+) \(disc (?P<disc>\d+)(: (?P<subtitle>.*))?\)', full_title)
    if match:
        return AlbumTitle(match.group('title'), match.group('disc'), match.group('subtitle'))
    else:
        return AlbumTitle(full_title, None, None)

# --------------------------------------------------------------------------------------------------
def remove_artist_roles(artists):
    """
    Return a list of artists with the musicbrainz-style artist roles removed.  The argument should
    be a list of strings.
    """
    return [parse_artist_role(artist).name for artist in artists]

# --------------------------------------------------------------------------------------------------
def map_relation(relation):
    """
    Map a musicbrainz artist relation to a tag name.  The result is a Relation named tuple.
    """
    # Pull the relation type from the URL returned.
    rel_type = relation.type.partition("#")[2]

    # Map relation type to tagname and store in the result.
    try:
        mapped = _mbz_reltype_map[rel_type]
        return Relation(mapped, relation.target.name, relation.target.sortName)
    except KeyError:
        return None

# --------------------------------------------------------------------------------------------------
def map_relations(relations):
    """
    Map a musicbrainz artist relations to a tag names.  The result is a list of Relation named
    tuples. A relation type that has no map will not be in the list.
    """
    names = [map_relation(rel) for rel in relations]
    return [name for name in names if not name is None]

# --------------------------------------------------------------------------------------------------
def get_track_artist_relations(track):
    """
    Extract the artist relations from the given musicbrainz Track object.  The result is a list of
    Relation named tuples.  'artist' is also set from the track artist.  A relation type that has
    no map will be excluded.
    """

    # Map the relations to tag/name tuples.
    result = map_relations(track.getRelations())

    # Add the track artist as a bonus.
    result.append(Relation(u'artist', track.artist.name, track.artist.sortName))

    return result

# --------------------------------------------------------------------------------------------------
def get_release_artist_relations(release):
    """
    Extracts the artist relations from the given musicbrainz Relase object.  The result is a list of
    Relation named tuples.  'artist' is set if the release is a single-artist release, otherwise
    'albumartist' is set.  A relation type that has no map will be excluded.
    """

    # Map the relations to tag/name tuples.
    result = map_relations(release.getRelations())

    # Add the release artist as a bonus.
    if release.isSingleArtistRelease():
        result.append(Relation(u'artist', release.artist.name, release.artist.sortName))
    else:
        result.append(Relation(u'albumartist', release.artist.name, release.artist.sortName))

    return result

# --------------------------------------------------------------------------------------------------
def get_earliest_release(release):
    """
    Extracts the earliest US release date or earliest release date if no US date is available, from
    the given musicbrainz Release object.
    """
    earliest = None
    earliest_US = None
    for event in release.releaseEvents:
        if not event.date is None:
            if earliest is None or event.date < earliest:
                earliest = event.date
            if event.country == 'US' and (earliest_US is None or event.date < earliest_US):
                earliest_US = event.date

    return earliest if earliest_US is None else earliest_US

