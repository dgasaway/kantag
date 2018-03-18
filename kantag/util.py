# util.py - kantag miscellaneous shared functionality.
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
import collections
import argparse

class ToggleAction(argparse.Action):
    """
    An argparse Action that will convert a y/n arg value into True/False.
    """
    def __call__(self, parser, ns, values, option_string):
        setattr(ns, self.dest, True if values[0] == 'y' else False)

# Basic metadata pair.
TagValue = collections.namedtuple('TagValue', 'tag, value')
