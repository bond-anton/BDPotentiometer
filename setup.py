"""
Setup script
"""
from codecs import open as codecs_open
from os import path
import re

from setuptools import setup


here = path.abspath(path.dirname(__file__))
PACKAGE_NAME = 'BDPotentiometer'
version_file = path.join(here, PACKAGE_NAME, '_version.py')
with codecs_open(version_file, 'rt') as f:
    version_file_line = f.read()
VERSION_RE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VERSION_RE, version_file_line, re.M)
if mo:
    version_string = mo.group(1)
else:
    raise RuntimeError(f'Unable to find version string in {version_file}.')

readme_file = path.join(here, 'README.md')
with codecs_open(readme_file, encoding='utf-8') as f:
    long_description = f.read()


setup(
    name=PACKAGE_NAME,
    version=version_string,

    description='BD Digital Potentiometer',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/bond-anton/BDPotentiometer',

    author='Anton Bondarenko',
    author_email='bond.anton@gmail.com',

    license='Apache Software License',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],

    keywords=['Potentiometer', 'Digital Potentiometer', 'gpio', 'gpiozero', 'SPI', 'Raspberry'],
    packages=['BDPotentiometer'],

)
