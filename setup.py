"""
Setup installation file for the pouty package.
"""

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pouty',
    version='0.1.3',
    description='pouty',
    long_description=long_description,
    url='https://github.com/jdmonaco/pouty',
    author='Joseph Monaco',
    author_email='self@joemona.co',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='shell console terminal output print log logfile debug color',
    packages=['pouty'],
)
