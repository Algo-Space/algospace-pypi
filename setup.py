#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-10-06 12:30:47
@LastEditors: Kermit
@LastEditTime: 2022-11-16 22:19:02
'''

from setuptools import setup, find_packages

setup(
    name='vsource',
    version='v2.0.2',
    description=(
        'Algorithm python library linked to vsource platform.'
    ),
    long_description=open('README.rst', encoding='utf8').read(),
    author='DBIIR',
    author_email='chuyuan@vsource.club',
    maintainer='DBIIR',
    maintainer_email='chuyuan@vsource.club',
    license='BSD License',
    packages=find_packages(where='.', include=('vsource',)),
    platforms=["all"],
    url='https://github.com/VSOURCE-Platform/VSOURCE-Library',
    install_requires=[
        'requests',
        'gradio'
    ],
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'vsource = vsource:run',
            'vsc = vsource:run'
        ]
    }
)
