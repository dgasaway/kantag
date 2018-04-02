# tagfile.py - kantag text metadata file parser and builder.
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
import re
import exceptions
import util
from listdict import ListDict
from tagset import TagSet
from tagstores import Release, Disc, Track
from tagmaps import cannonical_tags

# --------------------------------------------------------------------------------------------------
class TagLine(object):
    """
    Represents a line from a kantag tag file.
    """
    def __init__(self, line=None, line_type=None, applies_to=None, tag=None, value=None, warn=True):
        self._warn = warn

        # Initialize everything before attempting a parse.
        self._source_line = line
        self._line_type = None
        self._applies_to = None
        self._tag = None
        self._value = None
        self._used = False

        # If given a line, parse it.
        if self._source_line is not None:
            self._source_line = self._source_line.strip()
            if len(self._source_line) > 0:
                self._parse(self._source_line)

        # Let the remainder or parameters override what may have been parsed.
        if line_type is not None:
            self.line_type = line_type
        if applies_to is not None:
            self._applies_to = applies_to
        if tag is not None:
            self.tag = tag
        if value is not None:
            self._value = value

    # ----------------------------------------------------------------------------------------------
    @property
    def source_line(self):
        """Raw text source line passed to constructor."""
        return self._source_line

    # ----------------------------------------------------------------------------------------------
    @property
    def line_type(self):
        """Line type '#', 'a', 'd', or 't'."""
        return self._line_type
    @line_type.setter
    def line_type(self, value):
        self._line_type = value.lower()

    # ----------------------------------------------------------------------------------------------
    @property
    def applies_to(self):
        """List of numeric values the line applies to."""
        return self._applies_to
    @applies_to.setter
    def applies_to(self, value):
        self._applies_to = value

    # ----------------------------------------------------------------------------------------------
    @property
    def tag(self):
        """Tag name."""
        return self._tag
    @tag.setter
    def tag(self, value):
        self._tag = value
        if self.warn and value not in cannonical_tags:
            print >> sys.stderr, 'warning: unrecognized tag: ' + value.encode('utf-8')

    # ----------------------------------------------------------------------------------------------
    @property
    def value(self):
        """Tag value."""
        return self._value
    @value.setter
    def value(self, newvalue):
        self._value = newvalue

    # ----------------------------------------------------------------------------------------------
    @property
    def used(self):
        """Whether a tag line is used in the process of writing tags to audio files."""
        return self._used
    @used.setter
    def used(self, value):
        self._used = value

    # ----------------------------------------------------------------------------------------------
    @property
    def warn(self):
        """Whether warnings are enabled."""
        return self._warn
    @warn.setter
    def warn(self, value):
        self._warn = value

    # ----------------------------------------------------------------------------------------------
    def _parse(self, line):
        """
        Parse a kantag line into a TagLine.
        """
        if line.startswith('#'):
            # Comment line.
            pattern = r'^(?P<type>[#])(?P<comment>.*)$'
            match = re.match(pattern, line)
            if not match:
                raise exceptions.TagFileFormatError(
                    'Malformed comment tag: ' + line.encode('utf-8'))

            self.line_type = match.group('type')
            self._value = match.group('comment').strip()
            self._used = True

        elif line.startswith('a'):
            # Album/release line.
            pattern = r'^(?P<type>[aA]) (?P<tagname>[^=]*)=(?P<tagvalue>.+)$'
            match = re.match(pattern, line)
            if not match:
                raise exceptions.TagFileFormatError(
                    'Malformed album tag: ' + line.encode('utf-8'))

            self.line_type = match.group('type')
            self.tag = match.group('tagname')
            self._value = match.group('tagvalue')

        else:
            # Disc or track line.
            pattern = r'^(?P<type>[dtDT]) ' + \
                r'(?P<range>(\d+(-\d+)?)(,(\d+(-\d+)?))*) ' + \
                r'(?P<tagname>[^=]*)=(?P<tagvalue>.+)$'
            match = re.match(pattern, line)
            if not match:
                raise exceptions.TagFileFormatError(
                    'Malformed disc/track tag: ' + line.encode('utf-8'))

            self.line_type = match.group('type')
            self._applies_to = util.expand_ranges(match.group('range'))
            self.tag = match.group('tagname')
            self._value = match.group('tagvalue')

    # ----------------------------------------------------------------------------------------------
    def __unicode__(self):
        """
        Build a unicode kantag line from the current state.
        """
        if self._line_type is None:
            return u''
        elif self._line_type == '#':
            return u'# %s' % (self._value)
        elif self._line_type == 'a':
            return u'a %s=%s' % (self._tag, self._value)
        elif self._line_type == 'd' or self._line_type == 't':
            return u'%s %s %s=%s' % (self._line_type, self._applies_to, self._tag, self._value)
        else:
            raise exceptions.TagFileFormatError('Unexpected line type: ' + self._line_type)

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        """
        Build a UTF-8 encoded kantag line from the current state.
        """
        return unicode(self).encode('utf-8')

    # ----------------------------------------------------------------------------------------------
    def pprint(self):
        s = self._line_type + ': ' + \
            (', '.join(self._applies_to) if self._applies_to is not None else '[n/a]') + '\t' + \
            (self._tag + '=' if self._tag is not None else '') + \
            (self._value if self._value is not None else '[no value]')
        return s

# --------------------------------------------------------------------------------------------------
class TagFile(object):
    """
    Represents a collection of lines from a kantag tag file.
    """
    def __init__(self, warn=True):
        self._lines = []

    # ----------------------------------------------------------------------------------------------
    @property
    def lines(self):
        """List of contained TagLines."""
        return self._lines
    @lines.setter
    def lines(self, value):
        self._lines = value

    # ----------------------------------------------------------------------------------------------
    def apply_map(self, tag_map):
        """
        Apply a tag map to the lines of the file.
        """
        remove = []
        for line in self._lines:
            if line.tag in tag_map:
                new_tag = tag_map[line.tag]
                if new_tag is None:
                    remove.append(line)
                else:
                    line.tag = new_tag
        for line in remove:
            self._lines.remove(line)

    # ----------------------------------------------------------------------------------------------
    def get_matching(self, disc, track):
        """
        Get a TagSet of tags that should be applied to a track with a given disc number and track
        number.  If a line is used in the process, the 'used' attribue is set to True.
        """
        # Note: This approach of looping through the lines in one pass has the advantage of
        # preserving the order of the values for a given tag name as they appear in the file.
        disctrack = (track if disc is None else disc + track)
        result = TagSet()
        for line in self._lines:
            if line.line_type == 'a' or \
                line.line_type == 'd' and disc in line.applies_to or \
                line.line_type == 't' and disctrack in line.applies_to:
                    # Record the tag pair.
                    result.append(line.tag, line.value)
                    # Flag the line as used.
                    line.used = True

        return result

    # ----------------------------------------------------------------------------------------------
    def __unicode__(self):
        """
        Build unicode kantag lines from the current state.
        """
        return ('\n').join([unicode(l) for l in self._lines])

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        """
        Build UTF-8 encoded kantag lines from the current state.
        """
        return unicode(self).encode('utf-8')

    # ----------------------------------------------------------------------------------------------
    def pprint(self, print_comments=False):
        s = ''
        for line in [l for l in self._lines if print_comments or l.line_type != '#']:
            s += line.pprint() + '\n'
        return s

# --------------------------------------------------------------------------------------------------
class TagFileBuilder(object):
    """
    Helper for building a TagFile.
    """
    def __init__(self, tag_file=None, reader=None, warn=True):
        self._warn = warn
        self._file = tag_file
        if self._file is None:
            self._file = TagFile(warn=warn)
        if reader is not None:
            self._file.lines = \
                [TagLine(line, warn=warn) for line in reader.readlines() if len(line.strip()) > 0]

    # ----------------------------------------------------------------------------------------------
    @property
    def tags(self):
        """The underlying TagFile object."""
        return self._file

    # ----------------------------------------------------------------------------------------------
    @property
    def warn(self):
        """Whether warnings are enabled."""
        return self._warn
    @warn.setter
    def warn(self, value):
        self._warn = value

    # ----------------------------------------------------------------------------------------------
    def _get_value_entity_dict(self, entities, key):
        """
        Builds a dictionary keyed by the values of 'key' in all 'entities', where the value at each
        key is a list of entities with that value.  Result is a ListDict instance.
        """
        values = ListDict()
        for entity in entities:
            if key in entity.tags:
                for value in entity.tags[key]:
                    values.append_unique(value, entity)
        return values
    
    # ----------------------------------------------------------------------------------------------
    def _get_number_str(self, entities, parent=None):
        """
        Builds a number identifier for a TagStore entity or list of TagStore entities.  If a
        'entities' is a list, all items should be of the same type.
        """
        if not isinstance(entities, list):
            entities = [entities]
        
        nums = []
        for entity in entities:
            if isinstance(entity, Release):
                pass
            elif isinstance(entity, Disc):
                nums.append('%s' % entity.number)
            elif isinstance(entity, Track):
                if parent is not None and parent.number is not None:
                    nums.append('%s%s' % (parent.number, entity.number.zfill(2)))
                else:
                    nums.append('%s' % entity.number.zfill(2))
            else:
                raise exceptions.TaggingError('Unexpected entity type: ' + str(type(entity)))

        # Condense consecutive numbers into ranges.  Note that values are strings with leading
        # zeros.
        return util.condense_ranges(nums)

    # ----------------------------------------------------------------------------------------------
    def _add_value(self, entity, num, tag, value):
        """
        Add a TagLine built from a TagStore entity, a number identifier, a tag, and a value.
        """
        if isinstance(entity, Release):
            l = TagLine(None, 'a', num, tag, value, self.warn)
        elif isinstance(entity, Disc):
            l = TagLine(None, 'd', num, tag, value, self.warn)
        elif isinstance(entity, Track):
            l = TagLine(None, 't', num, tag, value, self.warn)
        else:
            raise exceptions.TaggingError('Unexpected entity type: ' + str(type(entity)))
        self._file.lines.append(l)

    # ----------------------------------------------------------------------------------------------
    def add_value(self, entity, tag, value, parent=None):
        """
        Add a TagLine built from a TagStore entity or list of TagStore entities, a tag, and a value.
        If 'entity' is a list, all items should be of the same type.
        """
        num = self._get_number_str(entity, parent)
        self._add_value(entity[0] if isinstance(entity, list) else entity, num, tag, value)

    # ----------------------------------------------------------------------------------------------
    def add_values(self, entity, key, parent=None):
        """
        Add TagLines built from tag values for a given key stored in a TagStore entity or list of
        TagStore entities.  If 'entity' is a list, all items should be of the same type.
        """
        if isinstance(entity, list):
            # First, build a dictionary that has the entities for each value.
            ved = self._get_value_entity_dict(entity, key);
            # Then sort them by the condensed number list.
            sorted_values = sorted(ved, key=lambda value: self._get_number_str(ved[value], parent))
            # Now output them in order.
            for value in sorted_values:
                self.add_value(ved[value], key, value, parent)
        elif key in entity.tags:
            for value in entity.tags[key]:
                self.add_value(entity, key, value, parent)

    # ----------------------------------------------------------------------------------------------
    def add_values_as(self, entity, key, as_tag, parent=None):
        """
        Add a TagLine built from a TagStore entity and its stored tag values for the key, but as an
        alternate tag name.
        """
        if key in entity.tags:
            for value in entity.tags[key]:
                self.add_value(entity, as_tag, value, parent)

    # ----------------------------------------------------------------------------------------------
    def add_values_req(self, entity, key, parent=None):
        """
        Add a TagLine built from a TagStore entity and its stored tag values for the key; a line is
        added even if no tags are present for the key.
        """
        if key in entity.tags:
            for value in entity.tags[key]:
                self.add_value(entity, key, value, parent)
        else:
            self.add_value(entity, key, '', parent)

    # ----------------------------------------------------------------------------------------------
    def add_values_as_req(self, entity, key, as_tag, parent=None):
        """
        Add a TagLine built from a TagStore entity and its stored tag values for the key, but as an
        alternate tag name; a line is added even if no tags are present for the key.
        """
        if key in entity.tags:
            for value in entity.tags[key]:
                self.add_value(entity, as_tag, value, parent)
        else:
            self.add_value(entity, as_tag, '', parent)

    # ----------------------------------------------------------------------------------------------
    def add_comment(self, comment):
        """
        Add a comment TagLine.
        """
        self._file.lines.append(TagLine(line_type='#', value=comment, warn=self.warn))

    # ----------------------------------------------------------------------------------------------
    def add_blank(self):
        """
        Add an empty TagLine, but only if the file is non-empty and the previous line is not blank.
        """
        cnt = len(self._file.lines)
        #print 'last: ' + self._file.lines[cnt-1].line_type
        if cnt > 0 and not self._file.lines[cnt-1].line_type is None:
            self._file.lines.append(TagLine(warn=self.warn))
