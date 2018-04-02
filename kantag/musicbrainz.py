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
""" Maps musicbrainz relationship UUIDs to cannonical tags. """
_mbz_reltype_map = {
    # Work 'composer'
    'd59d99ea-23d4-4a80-b066-edca32ee158f' : u'Composer',
    # Work 'librettist'
    '7474ab81-486f-40b5-8685-3a4f8ea624cb' : u'Lyricist',
    # Work 'lyricist'
    '3e48faba-ec01-47fd-8e89-30e81161661c' : u'Lyricist',
    # Work 'translator'
    'da6c5d8a-ce13-474d-9375-61feb29039a5' : u'Lyricist',
    # Work 'arranger'
    'd3fd781c-5894-47e2-8c12-86cc0e2c8d08' : u'Arranger',
    # Work 'instrument arranger'
    '0084e70a-873e-4f7f-b3ff-635b9e863dae' : u'Arranger',
    # Work 'vocal arranger'
    '6a88b92b-8fb5-41b3-aa1f-169ee7e05ed6' : u'Arranger',
    # Work 'orchestrator'
    '0a1771e1-8639-4740-8a43-bdafc050c3da' : u'Arranger',
    # Work 'revised by'
    'eeb9c319-9fde-4313-b76d-29db1576aad8' : u'Arranger',
    # Work 'reconstructed by'
    'cb887d1b-5267-4f3d-badb-5b3fba7349f6' : u'Arranger',
    # Work 'writer'
    'a255bca1-b157-4518-9108-7b147dc3fc68' : u'Writer',
    
    # Recording 'arranger'
    '22661fb8-cdb7-4f67-8385-b2a8be6c9f0d' : u'Arranger',
    # Recording 'instrument arranger'
    '4820daa1-98d6-4f8b-aa4b-6895c5b79b27' : u'Arranger',
    # Recording 'vocal arranger'
    '8a2799e8-a7e2-41ce-a7da-b5f520687216' : u'Arranger',
    # Recording 'orchestrator'
    '38fa7405-f9a5-48cb-827a-8ac601933ba0' : u'Arranger',
    # Recording 'performer'
    '628a9658-f54c-4142-b0c0-95f031b544da' : u'Performer',
    # Recording 'instrument'
    '59054b12-01ac-43ee-a618-285fd397e461' : u'Performer',
    # Recording 'vocal'
    '0fdbe3c6-7700-4a31-ae54-b53f06ae1cfa' : u'Performer',
    # Recording 'performing orchestra'
    '3b6616c5-88ba-4341-b4ee-81ce1e6d7ebb' : u'Performer',
    # Recording 'programming'
    '36c50022-44e0-488d-994b-33f11d20301e' : u'Performer',
    # Recording 'conductor'
    '234670ce-5f22-4fd0-921b-ef1662695c5d' : u'Conductor',
    # Recording 'chorus master'
    '45115945-597e-4cb9-852f-4e6ba583fcc8' : u'Conductor',
    # Recording 'remixer'
    '7950be4d-13a3-48e7-906b-5af562e39544' : u'Arranger',    
    
    # Release 'composer'
    '01ce32b0-d873-4baa-8025-714b45c0c754' : u'Composer',
    # Release 'librettist'
    'dd182715-ca2b-4e4b-80b1-d21742fda0dc' : u'Lyricist',
    # Release 'lyricist'
    'a2af367a-b040-46f8-af21-310f92dfe97b' : u'Lyricist',
    # Release 'translator'
    '4db37fec-eb67-45d3-b4fa-148a68135fbb' : u'Lyricist',
    # Release 'arranger'
    '34d5334e-a4c8-4b65-a5f8-bbcc9c81d13d' : u'Arranger',
    # Release 'instrument arranger'
    '18f159bb-44f0-4aef-b198-a4736ad9b659' : u'Arranger',
    # Release 'vocal arranger'
    'd7d9128d-e676-4d8f-a353-f48a55a98501' : u'Arranger',
    # Release 'orchestrator'
    '04e1f0b6-ef40-4168-ba25-42a87729fe09' : u'Arranger',
    # Release 'writer'
    'ca7a474a-a1cd-4431-9230-56a17f553090' : u'Writer',
    # Release 'performer'
    '888a2320-52e4-4fe8-a8a0-7a4c8dfde167' : u'Performer',
    # Release 'instrument'
    '67555849-61e5-455b-96e3-29733f0115f5' : u'Performer',
    # Release 'vocal'
    'eb10f8a0-0f4c-4dce-aa47-87bcb2bc42f3' : u'Performer',
    # Release 'performing orchestra'
    '23a2e2e7-81ca-4865-8d05-2243848a77bf' : u'Performer',
    # Release 'programming'
    '617063ad-dbb5-4877-9ba0-ba2b9198d5a7' : u'Performer',
    # Release 'conductor'
    '9ae9e4d0-f26b-42fb-ab5c-1149a47cf83b' : u'Conductor',
    # Release 'chorus master'
    'b9129850-73ec-4af5-803c-1c12b97e25d2' : u'Conductor',
    # Release 'remixer'
    'ac6a86db-f757-4815-a07e-744428d2382b' : u'Arranger',    
    }
""" Musicbrainz relationship UUID for work-work 'parts' relationship. """
_mbz_parts_id = 'ca8d3642-ce5f-49f8-91f2-125d72524e6a'
""" Musicbrainz relationsip UUID for recording-work 'performance' relationship. """
_mbz_performance_id = 'a3005666-a872-32c3-ad06-98af558e99b0'

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
    rel_type = relation['type-id']
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
            if rel['type-id'] == _mbz_parts_id:
                if 'direction' in rel and rel['direction'] == 'backward':
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
        return [r['work'] for r in rels if r['type-id'] == _mbz_performance_id]
    else:
        return []
