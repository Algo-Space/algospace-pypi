# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : __init__.py.py
# @Function : TODO

from vsource.loginInstance import login
from vsource.algorithms.face_recognition import face_recognition
from vsource.algorithms.face_detection import face_detection
from vsource.algorithms.face_attribute import face_attribute
from vsource.algorithms.speaker_recognition import speaker_recognition

from vsource.algorithms.new_algorithm import new_algorithm

from vsource.scripts.algorithm_scripts.algorithms import parse_algorithm
from vsource.scripts.enroll_service import enroll

__version__ = 'v1.0.5'
__author__  = 'Ecohnoch'
__email__   = '542305306@qq.com'