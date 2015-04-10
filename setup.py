import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = '0.0.1'

setup(
    name='pycrawler',
    version=version,
    packages=find_packages(),
    url='https://github.com/pengmeng/PyCrawler',
    license='MIT License',
    author='mengpeng',
    author_email='mengp3157@gmail.com',
    description='A lightweight Python crawler framework',
    long_description=read('README.md'),
    platforms='any',
    install_requires=['beautifulsoup4>=4.3.2',
                      'bitarray>=0.8.1',
                      'eventlet>=0.17.2',
                      'greenlet>=0.4.5',
                      'pybloom>=1.1',
                      'pymongo>=2.8',
                      'redis>=2.10.3'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
