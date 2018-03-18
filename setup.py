from setuptools import setup
import os
import io
from kantag._version import __version__

# Read the long description from the README.
basedir = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(basedir, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='kantag',
    version=__version__,
    description='manage audio file metadata using external text files',
    long_description=long_description,
    author='David Gasaway',
    author_email='dave@gasaway.org',
    url='https://bitbucket.org/dgasaway/kantag',
    download_url='https://bitbucket.org/dgasaway/kantag/downloads/',
    license='GNU GPL v2',
    packages=['kantag'],
    scripts=['bin/applykan', 'bin/initkan', 'bin/showkan'],
    python_requires='~=2.7',
    install_requires=[
        'mutagen >= 1.20',
        'python-musicbrainz2 >= 0.7.2',
    ],
    keywords='audio music metadata tags',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
    ],
)
