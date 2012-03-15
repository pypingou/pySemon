#!/usr/bin/env python
import sys
import re

from setuptools import setup
from semon import __version__

description = "Small library to read/convert from XML to INI ontology file."

long_description = """
pySemon tries to help you generate an OWL ontology using INI file as basis.
"""

download_url = "http://github.com/pypingou/pySemon-%s.tar.gz" % __version__

requirements = [
    'rdflib',
    'kitchen',
]

try:
    import argparse
except ImportError:
    requirements.append('argparse')

setup(
    name='pySemon',
    version=__version__,
    description=description,
    author="Pierre-Yves Chibon",
    author_email="pingou@pingoured.fr",
    maintainer="Pierre-Yves Chibon",
    maintainer_email="pingou@pingoured.fr",
    url="http://github.com/pypingou/pySemon",
    license="GPLv3+",
    long_description=long_description,
    download_url=download_url,
    package_dir = {'pySemon': 'semon'},
    packages=['pySemon'],
    install_requires=requirements,
    entry_points="""
    [console_scripts]
    pySemon = pySemon:main
    """
)
