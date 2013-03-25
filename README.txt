======
kantag
======

kantag is a set of Python libraries and tools for managing audio file (flac,
ogg vorbis, and mp3) metadata using external text files called "kantag
files".  The format of the file is identical regardless of audio file type.  
Included is a tool to generate the text file from existing tags, path, and
`Musicbrainz <http://musicbrainz.org>` data (``initkan``); a tool to write
the metadata to the audio file tags (``applykan``); and a tool to display
metadata (``showkan``).  A typical kantag file would have lines that look
like this::

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

