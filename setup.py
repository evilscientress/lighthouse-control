#!/usr/bin/env python3
from setuptools import setup

setup(
    name='lighthouse-control',
    version='0.0.1',
    description='A cross platform python library to control and interact with Valve® V2 Lighthouses.',
    author='Jenny Danzmayr',
    author_email='mail@evilscientress.de',
    url='https://github.com/evilscientress/lighthouse-control',
    packages=['lighthouse-control'],
    license='Apache License 2.0',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'bleak>=0.10.0',
    ],
)