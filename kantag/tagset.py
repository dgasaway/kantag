# tagset.py - kantag metadata storage primitive.
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
from listdict import ListDict

class TagSet(ListDict):
    """
    Represents a set of tag/value sets that could be applied to an audio file.  Each item in the
    ListDict is keyed by a tag name, and contains a list of values for that name.
    """

    # --------------------------------------------------------------------------------------------------
    def __init__(self, tags=None):
        """
        Initializes an instance from a list of TagValue named tuples.
        """
        if tags is not None:
            for tagvalue in tags:
                self.append_unique(tagvalue.tag, tagvalue.value)
