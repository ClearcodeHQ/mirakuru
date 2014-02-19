from setuptools import setup, find_packages

setup(name='summon_process',
      version='0.1.3',
      description='Process coordinator for tests',
      long_description=file('README.rst').read(),
      url='https://github.com/mlen/summon_process',
      author='Mateusz Lenik',
      author_email='mlen@mlen.pl',
      license='LGPL',
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*",
          "tests"]),
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose', 'mock'])
