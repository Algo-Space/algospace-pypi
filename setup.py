#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: Setuptools
@Author: Kermit
@Date: 2022-10-06 12:30:47
@LastEditors: Kermit
@LastEditTime: 2022-12-12 14:46:48
'''

from setuptools import setup, find_packages
from os import path

name = 'algospace'
with open(path.join(name, 'version.txt'), 'r') as f:
    version = f.read().strip()

setup(
    name=name,
    version=version,
    description=(
        'AlgoSpace: A platform for displaying algorithm achievements'
    ),
    long_description=open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    author='DBIIR',
    author_email='ckeming@outlook.com',
    maintainer='DBIIR',
    maintainer_email='ckeming@outlook.com',
    license='BSD License',
    packages=find_packages(where='.', include=(name,)),
    platforms=["all"],
    url='https://github.com/Algo-Space/algospace-pypi',
    project_urls={
        'Documentation': 'https://vsource.club/publish',
        'Homepage': 'https://vsource.club',
    },
    install_requires=[
        'setuptools>=3.0',
        'requests',
        'gradio>=3.0'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'algospace = algospace:run',
            'asc = algospace:run'
        ]
    }
)
