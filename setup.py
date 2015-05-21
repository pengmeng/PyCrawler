import os
try:
    from setuptools import find_packages, setup, Command
except ImportError:
    from distutils.core import find_packages, setup, Command


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

DESCRIPTION = 'A lightweight Python crawler framework'
LONG_DESCRIPTION = read('README.md')

setup(
    name='pycrawler',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/pengmeng/PyCrawler',
    license='MIT License',
    author='mengpeng',
    author_email='mengp3157@gmail.com',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms='any',
    install_requires=['beautifulsoup4>=4.3.2',
                      'bitarray>=0.8.1',
                      'eventlet>=0.17.2',
                      'greenlet>=0.4.5',
                      'pybloom>=1.1',
                      'pymongo>=3.0.1',
                      'redis>=2.10.3',
                      'Unidecode>=0.4.17'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)