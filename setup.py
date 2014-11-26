from setuptools import setup
from kantag._version import __version__

setup(
    name='kantag',
    version=__version__,
    description='manage audio file metadata using external text files',
    long_description=open('README.txt').read(),
    author='David Gasaway',
    author_email='dave@gasaway.org',
    url='https://code.google.com/p/kantag/',
    download_url='https://code.google.com/p/kantag/downloads/list',
    license='GNU GPL v2',
    packages=['kantag'],
    scripts=['bin/applykan', 'bin/initkan', 'bin/showkan'],
    install_requires=[
        'mutagen >= 1.20',
        'python-musicbrainz2 >= 0.7.2',
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Indended Audience :: End Users/Desktop',
    ],
)
