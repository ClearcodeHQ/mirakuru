# Copyright (C) 2014 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of mirakuru.

# mirakuru is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# mirakuru is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with mirakuru.  If not, see <http://www.gnu.org/licenses/>.
"""Mirakuru installation module."""

import os
from setuptools import setup, find_packages


here = os.path.dirname(__file__)


requirements = [
    # psutil is used to find processes leaked during termination.
    # It's installable but not importable on pypy3.
    'psutil>=4.0.0',
]

tests_require = (
    'pytest==3.6.2',  # tests framework used
    'pytest-cov==2.5.1',  # coverage reports to verify tests quality
    'mock==2.0.0',  # tests mocking tool
    'python-daemon==2.1.2',  # used in test for easy creation of daemons
)
extras_require = {
    'docs': ['sphinx'],
    'tests': tests_require,
}


def read(fname):
    """
    Read filename.

    :param str fname: name of a file to read
    """
    return open(os.path.join(here, fname)).read()


setup(
    name='mirakuru',
    version='1.0.0',
    description='Process executor for tests.',
    long_description=(
        read('README.rst') + '\n\n' + read('CHANGES.rst')
    ),
    keywords='process executor tests summon_process',
    url='https://github.com/ClearcodeHQ/mirakuru',
    author='Clearcode - The A Room',
    author_email='thearoom@clearcode.cc',
    license='LGPL',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Testing',
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=requirements,
    tests_require=tests_require,
    test_suite='tests',
    include_package_data=True,
    zip_safe=False,
    extras_require=extras_require,
)
