# listdict.py - kantag dictionary of lists.
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
class ListDict(dict):
    """
    Data container that extends dict with convenience methods for storing a list with each
    dictionary slot.
    """
    # ----------------------------------------------------------------------------------------------
    @staticmethod
    def _list_diff(a, b):
        """
        Return a list of values that are in list a but not in list b, preserving element order.
        """
        return [value for value in a if not value in b]

    # ----------------------------------------------------------------------------------------------
    @staticmethod
    def _list_int(a, b):
        """
        Return a list of values that are in both list and list b, preserving element order.
        """
        return [value for value in a if value in b]

    # ----------------------------------------------------------------------------------------------
    @staticmethod
    def _list_remove(lst, value):
        """
        Remove all occurences of value from the list in-line.
        """
        i = len(lst) - 1
        while i >= 0:
            if lst[i] == value:
                lst.pop(i)
            i -= 1

    # ----------------------------------------------------------------------------------------------
    @staticmethod
    def _list_replace(lst, replace, replacement):
        """
        Replace all values matching values in-line in a list.  Return whether any values were
        replaced.
        """
        replaced = False
        for i, v in enumerate(lst):
            if v == replace:
                lst[i] = replacement
                replaced = True
        return replaced

    # ----------------------------------------------------------------------------------------------
    @staticmethod
    def _list_replace_ci(lst, replace, replacement):
        """
        Replace all values case-insensitive-matching values in-line in a list.  Return whether any
        values were replaced.
        """
        replaced = False
        for i, v in enumerate(lst):
            if v.lower() == replace.lower():
                lst[i] = replacement
                replaced = True
        return replaced

    # ----------------------------------------------------------------------------------------------
    def append(self, key, value):
        """
        Append a value to the list at the key.
        """
        if key in self:
            self[key].append(value)
        else:
            # Create a new sequence at the key.
            self[key] = [value]

    # ----------------------------------------------------------------------------------------------
    def append_unique(self, key, value):
        """
        Append a value to the list at they key, provided the value is not already in the list.
        """
        if key in self:
            l = self[key]
            if value not in l:
                l.append(value)
        else:
            # Create a new sequence at the key.
            self[key] = [value]

    # ----------------------------------------------------------------------------------------------
    def extend(self, key, values):
        """
        Append values to the list at the key.
        """
        for value in values:
            self.append(key, value)

    # ----------------------------------------------------------------------------------------------
    def extend_unique(self, key, values):
        """
        Append values to the list at the key, provided the values are not already in the list.
        """
        for value in values:
            self.append_unique(key, value)

    # ----------------------------------------------------------------------------------------------
    def merge_unique(self, dct):
        """
        Add values from a dictionary that are not already in the object.
        """
        for key, values in dct.iteritems():
            self.extend_unique(key, values)

    # ----------------------------------------------------------------------------------------------
    def replace(self, key, replace, replacement):
        """
        Replace matching values in the list at the key.
        """
        if key in self:
            #self[key] = map((lambda v: replacement if v == replace else v), self[key])
            ListDict._list_replace(self[key], replace, replacement)

    # ----------------------------------------------------------------------------------------------
    def replace_ci(self, key, replace, replacement):
        """
        Replace case-insensitive-matching values in the list at the key.
        """
        if key in self:
            #self[key] = map((lambda v: replacement if v == replace else v), self[key])
            ListDict._list_replace_ci(self[key], replace, replacement)

    # ----------------------------------------------------------------------------------------------
    def remove(self, key, value):
        """
        Remove a value from the list at key; if the list is empty after removing the value, remove
        the key.
        """
        if key in self:
            l = [v for v in self[key] if v != value]
            if len(l) == 0:
                del self[key]
            else:
                self[key] = l

    # ----------------------------------------------------------------------------------------------
    def append_replace(self, key, replace, value):
        """
        Replace matching values in the list at the key with another value.  If neither the replaced
        value nor replacement value is in the list, then append the replacement value.
        """
        # Note we want this code to preserve the order of the items in the list.  That's why we use
        # a replace when possible rather than a simpler remove/append.
        if key in self:
            l = self[key]
            replaced = ListDict._list_replace(l, replace, value)
            # As an optimization, avoid attempting to append if there was a replace.
            if not replaced and value not in l:
                l.append(value)
        else:
            self[key] = [value]

    # ----------------------------------------------------------------------------------------------
    def remove_dict(self, remove):
        """
        Remove all the values from the dictionary that are present in a second dictionary.
        """
        for key, values in remove.iteritems():
            for value in values:
                self.remove(key, value)

    # ----------------------------------------------------------------------------------------------
    def move_values(self, a, b):
        """
        Provided there is a list with key a, replace the list at key b with the list at key a and
        remove key a.
        """
        if a in self:
            self[b] = self[a]
            del self[a]

    # ----------------------------------------------------------------------------------------------
    def contains(self, key, value):
        """
        Return whether the list at the given key contains the given value.
        """
        return key in self and value in self[key]

    # ----------------------------------------------------------------------------------------------
    @staticmethod
    def get_common_values(dicts):
        """
        Return a new ListDict that contains the values common to all the ListDicts passed.
        """
        result = ListDict()

        for key, values in dicts[0].iteritems():
            common_values = values[:]
            for dict2 in dicts[1:]:
                if key in dict2:
                    common_values = ListDict._list_int(common_values, dict2[key])
                else:
                    common_values = []
            if len(common_values) > 0:
                result[key] = common_values

        return result
