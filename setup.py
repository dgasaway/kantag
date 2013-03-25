from distutils.core import setup
from kantag._version import __version__

setup(
    name='kantag',
    version=__version__,
    author='David Gasaway',
    author_email='dave@gasaway.org',
    packages=['kantag'],
    scripts=['bin/applykan', 'bin/initkan', 'bin/showkan'],
    url='http://code.google.com/c/kantag/',
    license='GNU GPL v2',
    description='manage audio file metadata using external text files',
    long_description=open('README.txt').read(),
    install_requires=[
		"mutagen >= 1.20"
        "python-musicbrainz2 >= 0.7.2"
    ],
)
