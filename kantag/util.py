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

# --------------------------------------------------------------------------------------------------
def expand_ranges(range_str):
    """
    Expand a range string into a list of individual values, e.g., '01-03,05' -> ['01', '02, '03',
    '05'].  Each number in the string should have the same number of digits.
    """
    if not re.match(r'^(\d+(-\d+)?)(,(\d+(-\d+)?))*$', range_str):
        raise exceptions.TagFileFormatError('Malformed track number range string: ' + range_str)

    result = []
    for item in range_str.split(','):
        match = re.match(r'(?P<start>\d+)-(?P<end>\d+)', item)
        if match:
            # Store the length of the start value so we can pad all values to
            # this length.
            item_len = len(match.group('start'))

            # Loop through the range, and add add each item to the list.
            start = int(match.group('start'))
            end = int(match.group('end'))
            for i in range(start, end+1):
                result.append(str(i).zfill(item_len))
        else:
            result.append(item)

    return result

# --------------------------------------------------------------------------------------------------
def condense_ranges(nums):
    """
    Given a list of numeric strings, sort and condense consecutive ranges into a range string,
    e.g., ['01', '02', '03', '05'] -> '01-03,05'.
    """
    # 'base' is the index storing the low value of a range.
    base = 0
    ranges = []
    nums = sorted([num for num in nums if not num is None])
    for idx in range(len(nums)):
        # If last index, or there is a gap before the next value, then output a range.
        if (idx == len(nums) - 1) or (int(nums[idx + 1]) - int(nums[idx]) > 1):
            ranges.append(('' if idx == base else str(nums[base]) + '-') + str(nums[idx]))
            # Next value will start the next range.
            base = idx + 1

    return ','.join(ranges)

