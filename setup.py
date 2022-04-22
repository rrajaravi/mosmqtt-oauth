#!/usr/bin/env python3

from setuptools import setup, find_packages
from mosmqtt_oauth import __version__, __maintainer__, __email__, __license__

long_description = '''
Documentation
-------------
Full documentation is available on `Github`_.
.. _`Github`: https://github.com/rrajaravi/mosmqtt-oauth
'''

install_requires = ['redis==3.5.3', 'requests==2.22.0']

setup(
    name='mosmqtt-oauth',
    version=__version__,
    author=__maintainer__,
    author_email=__email__,
    url='https://github.com/rrajaravi/mosmqtt-oauth',
    description='OAuth plugin module for MOSQUITTO MQTT',
    long_description=long_description,
    license=__license__,
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: MIT License",
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
