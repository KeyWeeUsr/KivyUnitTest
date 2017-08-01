#!/usr/bin/env python

from distutils.core import setup

version = '0.1.5'

setup(
    name='kivyunittest',
    version=version,
    description='Unittesting for Kivy framework',
    author='Peter Badida',
    author_email='keyweeusr@gmail.com',
    url='https://github.com/KeyWeeUsr/KivyUnitTest',
    download_url=(
        'https://github.com/KeyWeeUsr/KivyUnitTest/tarball/'
        '{}'.format(version)
    ),
    packages=['kivyunittest'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Testing',
    ],
    keywords=['unittest', 'testing', 'debug', 'kivy'],
    license="License :: OSI Approved :: MIT License",
)
