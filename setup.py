#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: Setuptools
@Author: Kermit
@Date: 2022-10-06 12:30:47
@LastEditors: Kermit
@LastEditTime: 2022-12-03 21:02:49
'''

from setuptools import setup, find_packages

setup(
    name='algospace',
    version='v0.1.1',
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
    packages=find_packages(where='.', include=('algospace',)),
    platforms=["all"],
    url='https://github.com/Algo-Space/algospace-pypi',
    install_requires=[
        'requests',
        'gradio'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.7',
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
