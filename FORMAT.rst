==================
kantag File Format
==================

File format
===========

Overall, if the file contains any non-ASCII characters, it should be UTF-8 encoded without BOM. Each line is parsed according to the rules below.

Line format
===========

The first character of a line indicates the line type:

+------+------------------------------------------------+
| Char | Description                                    |
+======+================================================+
| #    | A comment line that will be ignored.           |
+------+------------------------------------------------+
| a    | A tag that will be applied to all files.       |
+------+------------------------------------------------+
| d    | A tag that will be applied to selected discs.  |
+------+------------------------------------------------+
| t    | A tag that will be applied to selected tracks. |
+------+------------------------------------------------+

Blank lines are also allowed and ignored.

For disc and track types, next is a space followed by a list of disc/track numbers to which the tag applies. The list is comma separated and may contain ranges indicated by a hyphen. Some examples: 

+---------------+---------------------------------------------+
| Selector      | Description                                 |
+===============+=============================================+
| t 10          | Applies to track 10.                        |
+---------------+---------------------------------------------+
| d 2           | Applies to all tracks on disc 2.            |
+---------------+---------------------------------------------+
| d 1-3         | Applies to all tracks on discs 1, 2, and 3. |
+---------------+---------------------------------------------+
| t 01,05-07,10 | Applies to tracks 1, 5, 6, 7, and 10.       |
+---------------+---------------------------------------------+

The numbers may need to be zero padded as in the above track example if the audio filename has the disc or track number zero padded. This can also depend on the setting the ``--path-regex`` option passed to ``applykan``. With default settings, track numbers should be padded to two digits in the *kantag* file and in filenames. In addition, when working with a multi-disc release, track numbers should be prepended with the disc number, as in these examples:

+---------------+-------------------------------------------------------------+
| Selector      | Description                                                 |
+===============+=============================================================+
| t 101-103     | Applies to tracks 1 to 3 of disc 1.                         |
+---------------+-------------------------------------------------------------+
| t 105,201-202 | Applies to track 5 of disc 1, and tracks 1 and 2 of disc 2. |
+---------------+-------------------------------------------------------------+

Next comes a space and the tag name/value pair separated by an equal sign. Anything before the first equal sign will be used as the tag name, anything after and to the end of the line is the value. Putting it all together, you have something like this::

    t 07 Composer=Jaromír Weinberger

There is no support for multi-line values. Instead, use multiple instances of the tag::

    t 07 Comment=Work premièred in 1927.
    t 07 Comment=Known in English as "Švanda the Bagpiper" or "Schwanda the Bagpiper".