# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : setup.py
# @Function : TODO

#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='vsource',
    version='v1.1.2',
    description=(
        'Algorithm python library linked to vsource platform.'
    ),
    long_description=open('README.rst', encoding='utf8').read(),
    author='Ecohnoch',
    author_email='chuyuan@vsource.club',
    maintainer='Ecohnoch',
    maintainer_email='chuyuan@vsource.club',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/VSOURCE-Platform/VSOURCE-Library',
    install_requires=[
        'requests'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    include_package_data=True
)