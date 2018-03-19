Introduction
============

*kantag* is a set of Python libraries and tools for managing audio file (flac,
ogg vorbis, mp3, and m4a) metadata using external text files called "kantag
files".  The format of the file is identical regardless of audio file type.  
Included is a tool to generate the text file from existing tags, path, and
`MusicBrainz <https://musicbrainz.org>`_ data, ``initkan``; a tool to write the
metadata to the audio file tags, ``applykan``; and a tool to display metadata,
``showkan``.  A typical *kantag* file would have lines that look like like
this::

    # Album / common track info
    a AlbumArtist=Rush
    a AlbumArtistSort=Rush
    a Album=2112
    a Date=1976-03-12

    a Composer=Geddy Lee
    a ComposerSort=Lee, Geddy
    t 01-05 Composer=Alex Lifeson
    t 01-05 ComposerSort=Lifeson, Alex
    t 01-03,06 Lyricist=Neil Peart
    t 01-03,06 LyricistSort=Peart, Neil

    t 01 Title=2112
    t 01 Part=1. Overture
    t 01 Part=2. The Temples of Syrinx
    t 01 Part=3. Discovery
    t 01 Part=4. Presentation
    t 01 Part=5. Oracle: The Dream
    t 01 Part=6. Soliloquy
    t 01 Part=7. Grand Finale


Typical Usage
=============

In a typical *kantag* workflow, the user will have an album of audio files,
whether ripped from a CD, purchased from an online store, downloaded from
Bandcamp, or another source.  In most cases, the files will already contain
metadata tags.  `MusicBrainz Picard <https://picard.musicbrainz.org/>`_ is a
recommended choice for setting the initial metadata, especially for files ripped
from physical media.  The tool ``initkan`` will produce a baseline file for
a set of audio files::

    $ initkan -v -b=y -M=y *.ogg > tags.kan

The output would typically be retained as a file in the same folder as the audio
files, as in the above example.  Then, the file can be edited by any available
text editor, to meet the user's personal tastes.  Note, there are additional 
tags recognized by by the *kantag* tools that are not necessary output by 
``initkan``.  To write the tags back to the audio files, use ``applykan``::

    $ applykan -v tags.kan *.ogg

Installation
============

.. warning::

    Some Linux distributions discourage installation of system-level python
    packages using ``pip`` or ``setup.py install``, due to collisions with the
    system package manager.  In those cases, dependencies should be installed
    through the package manager, if possible, or choose a user folder
    installation method.

Installing with pip
-------------------

If your system has ``pip`` installed, and you have access to install software in
the system packages, then *kantag* kan be installed as administrator from 
`PyPI <https://pypi.python.org/pypi>`_::

    # pip install kantag

If you do not have access to install system packages, or do not wish to install
in the system location, it can be installed in a user folder::

    $ pip install --user kantag

Installing from source
----------------------

Either download a release tarball from the
`Downloads <https://bitbucket.org/dgasaway/kantag/downloads/>`_ page, and
unpack::

    $ tar zxvf kantag-1.1.0.tar.gz

Or get the latest source from the Mercurial repository::

    $ hg clone https://bitbucket.org/dgasaway/kantag

If you have access to install software in the system packages, then it can be
installed as administrator::

    # python setup.py install

If you do not have access to install system packages, or do not wish to install
in the system location, it can be installed in a user folder::

    $ python setup.py install --user


File Format
===========

Overall, if the *kantag* file contains any non-ASCII characters, it should be
UTF-8 encoded without BOM. Each line is parsed according to the rules below.
Blank lines are allowed and ignored.


Line format
-----------

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

For disc and track types, next is a space followed by a list of disc/track
numbers to which the tag applies. The list is comma separated and may
contain ranges indicated by a hyphen. Some examples: 

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

The numbers may need to be zero padded as in the above track example if the
audio filename has the disc or track number zero padded. This can also depend
on the setting the ``--path-regex`` option passed to ``applykan``. With default
settings, track numbers should be padded to two digits in the *kantag* file and
in filenames. In addition, when working with a multi-disc release, track numbers
should be prepended with the disc number, as in these examples:

+---------------+-------------------------------------------------------------+
| Selector      | Description                                                 |
+===============+=============================================================+
| t 101-103     | Applies to tracks 1 to 3 of disc 1.                         |
+---------------+-------------------------------------------------------------+
| t 105,201-202 | Applies to track 5 of disc 1, and tracks 1 and 2 of disc 2. |
+---------------+-------------------------------------------------------------+

Next comes a space and the tag name/value pair separated by an equal sign.
Anything before the first equal sign will be used as the tag name, anything
after and to the end of the line is the value. Putting it all together, you
have something like this::

    t 07 Composer=Jaromír Weinberger

There is no support for multi-line values. Instead, use multiple instances of
the tag::

    t 07 Comment=Work premièred in 1927.
    t 07 Comment=Known in English as "Švanda the Bagpiper" or "Schwanda the Bagpiper".
