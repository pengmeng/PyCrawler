from setuptools import setup, find_packages

version = '0.1'

setup(
    name='pycrawler',
    version=version,
    packages=find_packages(),
    url='https://github.com/pengmeng/PyCrawler',
    license='MIT License',
    author='mengpeng',
    author_email='mengp3157@gmail.com',
    description='A lightweight Python crawler framework',
    install_requires=['beautifulsoup4>=4.3.2',
                      'bitarray>=0.8.1',
                      'eventlet>=0.17.2',
                      'greenlet>=0.4.5',
                      'pybloom>=1.1',
                      'pymongo>=2.8',
                      'redis>=2.10.3']
)
