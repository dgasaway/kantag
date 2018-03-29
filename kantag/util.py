# util.py - kantag miscellaneous shared functionality.
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
import collections
import argparse
import re


class ToggleAction(argparse.Action):
    """
    An argparse Action that will convert a y/n arg value into True/False.
    """
    def __call__(self, parser, ns, values, option_string):
        setattr(ns, self.dest, True if values[0] == 'y' else False)

""" Basic metadata pair. """
TagValue = collections.namedtuple('TagValue', 'tag, value')
""" Artist name and performance role. """
NameRole = collections.namedtuple('NameRole', 'name, role')
""" Work title and list of part titles. """
WorkParts = collections.namedtuple('WorkParts', 'work, parts')
""" Constituent parts of an old-style MusicBrainz release title. """
AlbumTitle = collections.namedtuple('AlbumTitle', 'title, discnum, subtitle')

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
def remove_artist_roles(artists):
    """
    Return a list of artists with the musicbrainz-style artist roles removed.  The argument should
    be a list of strings.
    """
    return [parse_artist_role(artist).name for artist in artists]

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

