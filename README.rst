======
kantag
======

Introduction
============

kantag is a set of Python libraries and tools for managing audio file (flac,
ogg vorbis, mp3, and m4a) metadata using external text files called "kantag
files".  The format of the file is identical regardless of audio file type.  
Included is a tool to generate the text file from existing tags, path, and
`MusicBrainz <http://musicbrainz.org>`_ data, ``initkan``; a tool to write the
metadata to the audio file tags, ``applykan``; and a tool to display metadata,
``showkan``.  A typical kantag file would have lines that look like like
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

Using pip
---------

If your system has ``pip`` installed, and you have access to install software in
the system packages, then *kantag* kan be installed as administrator from 
`PyPI <https://pypi.python.org/pypi>`_::

    # pip install kantag

If you do not have access to install system packages, or do not wish to install
in the system location, it can be installed in a user folder::

    $ pip install --user kantag

From Source
-----------

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
