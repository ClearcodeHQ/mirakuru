import re
import os
from setuptools import setup, find_packages


here = os.path.dirname(__file__)
with open(os.path.join(here, 'mirakuru', '__init__.py')) as v_file:
    package_version = re.compile(
        r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


def read(fname):
    return open(os.path.join(here, fname)).read()

setup(
    name='mirakuru',
    version=package_version,
    description='Process executor for tests.',
    long_description=(
        read('README.rst')
        + '\n\n' +
        read('CHANGES.rst')
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
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing',
    ],
    packages=find_packages(),
    install_requires=[],
    tests_require=['nose', 'mock'],
    test_suite='tests',
    include_package_data=True,
    zip_safe=False,
)
