#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://astrocoffee.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='astrocoffee',
    version='0.0.2',
    description='Web application for organizing astro-ph coffee discussion.',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Anowar J. Shajib',
    author_email='ajshajib@gmail.com',
    url='https://github.com/ajshajib/astrocoffee',
    packages=[
        'astrocoffee',
    ],
    package_dir={'astrocoffee': 'astrocoffee'},
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    license='MIT',
    zip_safe=False,
    keywords='astrocoffee',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        #'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.6',
        #'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)