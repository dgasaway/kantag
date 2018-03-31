# musicbrainz.py - kantag musicbrainz operations.
# Copyright (C) 2018 David Gasaway
# https://bitbucket.org/dgasaway/kantag/

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
import time
import re
import collections
import warnings
import musicbrainzngs as ngs
from kantag._version import __version__

# Globals
_mbz_reltype_map = {
    'arranger'            : u'Arranger',
    'composer'            : u'Composer',
    'conductor'           : u'Conductor',
    'chorus master'       : u'Conductor',
    'instrument'          : u'Performer',
    'instrument arranger' : u'Arranger',
    'lyricist'            : u'Lyricist',
    'librettist'          : u'Lyricist',
    'orchestrator'        : u'Arranger',
    'performer'           : u'Performer',
    'performing orchestra': u'Performer',
    'programming'         : u'Performer',
    'revised by'          : u'Arranger',
    'reconstructed by'    : u'Arranger',
    'remixer'             : u'Arranger',
    'translator'          : u'Lyricist',
    'vocal'               : u'Performer',
    'vocal arranger'      : u'Arranger',
    'writer'              : u'Writer'
    }

""" Representation of an artist relation. """
Relation = collections.namedtuple('Relation', 'type, name, sortname')
""" An artist name-sortname pair. """
ArtistName = collections.namedtuple('ArtistName', 'name, sortname')

""" API response format. """
_format = 'json'

# Initialize the user agent.
ngs.set_useragent('kantag', __version__, 'https://bitbucket.org/dgasaway/kantag/')

# --------------------------------------------------------------------------------------------------
def _set_api_format(api_format):
    """
    Set the API format (xml or json).  FOR DEBUG USE ONLY.
    """
    global _format
    _format = api_format
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        ngs.set_format(api_format)

# --------------------------------------------------------------------------------------------------
def get_release_by_id(releaseid):
    """
    Call the musicbrainz API and return the Release object matching the releaseid.
    """
    incs = ['artists', 'artist-credits', 'artist-rels', 'recordings', 'recording-level-rels',
            'work-rels', 'work-level-rels', 'release-groups', 'labels', 'aliases']
    result = ngs.get_release_by_id(releaseid, includes=incs)
    print >> sys.stderr, "api format: " + _format
    if _format == 'json':
        return result
    else:
        return result['release']

# --------------------------------------------------------------------------------------------------
def get_recording_by_id(recordingid):
    """
    Call the musicbrainz API and return recording information, including artist and work ARs.
    """
    incs = ['artist-rels', 'work-rels', 'aliases']
    result = ngs.get_recording_by_id(recordingid, includes=incs)
    if _format == 'json':
        return result
    else:
        return result['recording']

# --------------------------------------------------------------------------------------------------
def get_work_by_id(workid, include_work_rels=False):
    """
    Call the musicbrainz API and return work information, including artist ARs.
    """
    incs = ['artist-rels', 'work-rels', 'aliases']
    result = ngs.get_work_by_id(workid, includes=incs)
    if _format == 'json':
        return result
    else:
        return result['work']

# --------------------------------------------------------------------------------------------------
def get_artist_primary_alias(artist, locale='en'):
    """
    Extract the primary locale alias from an artist returned by the musicbrainz API.  The result is
    an ArtistName named tuple with 'Artist' as the type.  If no primary locale alias is found, a
    tuple containing the original artist is returned.
    """
    key = 'aliases' if _format == 'json' else 'alias-list'
    primary_val = True if _format == 'json' else 'primary'
    alias_name_key = 'name' if _format == 'json' else 'alias'
    
    if key in artist:
        for alias in artist[key]:
            if 'primary' in alias and alias['primary'] == primary_val:
                if 'locale' in alias and alias['locale'] == locale:
                    return ArtistName(alias[alias_name_key], alias['sort-name'])
    return ArtistName(artist['name'], artist['sort-name'])

# --------------------------------------------------------------------------------------------------
def map_relation(relation, locale='en'):
    """
    Map a musicbrainz artist relation to a tag name.  The result is a Relation named tuple.
    """
    rel_type = relation['type']
    if rel_type in _mbz_reltype_map:
        artist = get_artist_primary_alias(relation['artist'], locale)
        return Relation(_mbz_reltype_map[rel_type], artist.name, artist.sortname)
    else:
        return None

# --------------------------------------------------------------------------------------------------
def map_relations(relations, locale='en'):
    """
    Map a musicbrainz artist relations to a tag names.  The result is a list of Relation named
    tuples. A relation type that has no map will not be in the list.
    """
    names = [map_relation(rel, locale) for rel in relations]
    return [name for name in names if not name is None]

# --------------------------------------------------------------------------------------------------
def get_artists(entity, locale='en'):
    """
    Extract the artists from an entity (e.g., release) returned by the musicbrainz API.  The result
    is a list of Relation named tupes with 'Artist' as the type.
    """
    result = []
    if 'artist-credit' in entity:
        for ac in entity['artist-credit']:
            if type(ac) == type(dict()) and 'artist' in ac:
                artist = get_artist_primary_alias(ac['artist'], locale)
                result.append(Relation(u'Artist', artist.name, artist.sortname))
    elif 'artist-credit-phrase' in entity:
        result.append(Relation(u'Artist', entity['artist-credit-phrase'], ''))

    return result

# --------------------------------------------------------------------------------------------------
def get_artist_relations(entity, locale='en'):
    """
    Extract the artist relations from an entity (e.g., recording or release) returned by the
    musicbrainz API.  The result is a list of Relation named tuples.  A relation type that has no
    map will be excluded, and duplicates of the same type and artist are removed.
    """
    key = 'relations' if _format == 'json' else 'artist-relation-list'
    if key in entity:
        # Map the relations to tag/name tuples.
        return list(set(map_relations(entity[key], locale))) 
    else:
        return []

# --------------------------------------------------------------------------------------------------
def get_work_partof_works(work):
    """
    Extract the works of which the a work returned by the musicbrainz API is a part.  The result is
    a list of work objects.  Only examines subworks in the loaded metadata, and does not query the
    API.
    """
    key = 'relations' if _format == 'json' else 'work-relation-list'
    result = []
    if key in work:
        for rel in work[key]:
            if rel['type'] == 'parts' and 'direction' in rel and rel['direction'] == 'backward':
                result.append(rel['work'])
    return result

# --------------------------------------------------------------------------------------------------
def _get_work_artist_relations(work, recurse=False, locale='en'):
    """
    Extract the artist relationships from a work returned by the musicbrainz API, optionally
    recursively following 'part of' relationships making further API calls, as necessary.
    """
    result = get_artist_relations(work, locale)
    if not recurse:
        return result

    # Recurse through part-of relation parents and add to list.
    parents = get_work_partof_works(work)
    for parent in parents:
        work = get_work_by_id(parent['id'], True)
        result = result + _get_work_artist_relations(work, True, locale)
    
    return result

# --------------------------------------------------------------------------------------------------
def get_work_artist_relations(work, recurse=False, locale='en'):
    """
    Extract the artist relationships from a work returned by the musicbrainz API, optionally
    recursively following 'part of' relationships making further API calls, as necessary.  The
    passed API work data must contain the work-artist relations; to recurse, it must also contain
    one level of work-work relations.  The result is a list of Relation named tuples.  A relation
    type that has no map will be excluded, and duplicates of the same type and artist are removed.
    """
    return list(set(_get_work_artist_relations(work, recurse, locale)))

# --------------------------------------------------------------------------------------------------
def get_earliest_release(release):
    """
    Extract the earliest US release date or earliest release date if no US date is available, from
    a release returned by the musicbrainz API.  The result is a date as a string or None if no date
    was found.  Only looks at release events on the specific release.
    """
    earliest = None
    earliest_US = None
    key = 'release-events' if _format == 'json' else 'release-event-list'
    if key in release:
        for event in release[key]:
            if 'date' in event:
                if earliest is None or event['date'] < earliest:
                    earliest = event['date']
                is_US = ('iso-3166-1-code-list' in event and 'US' in event['iso-3166-1-code-list'])
                if is_US and (earliest_US is None or event['date'] < earliest_US):
                    earliest_US = event['date']

    return earliest if earliest_US is None else earliest_US

# --------------------------------------------------------------------------------------------------
def get_earliest_rg_release(release):
    """
    Extract the earliest release date for the release group associated with a release returned by
    the musicbrainz API.  The result is a date as a string or None if no date was found.
    """
    if 'release_group' in release and 'first-release-date' in release['release_group']:
        return release['release_group']['first-release-date']
    else:
        return None

# --------------------------------------------------------------------------------------------------
def get_release_catalognumber(release):
    """
    Extract a label catalog number from a release returned by the musicbrainz API.  The result is a
    catalog number as a string or None if no catalog number was found.
    """
    key = 'label-info' if _format == 'json' else 'label-info-list'
    if key in release:
        for label in release[key]:
            if 'catalog-number' in label:
                return label['catalog-number']
    return None

# --------------------------------------------------------------------------------------------------
def get_release_medium(release, number):
    """
    Extract a medium by number from a release returned by the musicbrainz API.  The result is a
    musicbrainz API medium object.
    """
    key = 'media' if _format == 'json' else 'medium-list'
    if key in release:
        for medium in release[key]:
            if int(medium['position']) == int(number):
                return medium
    return None

# --------------------------------------------------------------------------------------------------
def get_medium_track(medium, number):
    """
    Extract a track by number from a medium returned by the musicbrainz API.  The result is a
    musicbrainz API track object.
    """
    key = 'tracks' if _format == 'json' else 'track-list'
    if 'tracks' in medium:
        for track in medium['tracks']:
            if int(track['position']) == int(number):
                return track
    return None

# --------------------------------------------------------------------------------------------------
def get_track_recording(track):
    """
    Extract a recording from a track returned by the musicbrainz API.  The result is a musicbrainz
    API recording object.
    """
    if 'recording' in track:
        return track['recording']
    else:
        return None

# --------------------------------------------------------------------------------------------------
def get_recording_works(recording):
    """
    Extract the works associated with a recording returned by the musicbrainz API.  The result is a
    list of musicbrainz API work objects.
    """
    result = []
    key = 'relations' if _format == 'json' else 'work-relation-list'
    if key in recording:
        rels = recording[key]
        return [r['work'] for r in rels if r['type'] == 'performance']
    else:
        return []
