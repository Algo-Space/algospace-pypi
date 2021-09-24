# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : __init__.py.py
# @Function : TODO

from vsource.loginInstance import login
from vsource.algorithms.face_recognition import face_recognition
from vsource.algorithms.face_detection import face_detection
from vsource.algorithms.face_attribute import face_attribute
from vsource.algorithms.speaker_recognition import speaker_recognition
from vsource.algorithms.face_generation import face_generation
from vsource.algorithms.random_number import random_number
from vsource.algorithms.remove_bg import remove_bg

from vsource.algorithms.new_algorithm import new_algorithm
from vsource.algorithms.cod_cpd import cod_cpd
from vsource.algorithms.salient_object_detection import salient_object_detection
from vsource.algorithms.landmark_detection import landmark_detection
from vsource.algorithms.binary_segmentation import binary_segmentation
from vsource.algorithms.face_attribute_x import face_attribute_x
from vsource.algorithms.text_generation import text_generation
from vsource.algorithms.github_avatar_generation import github_avatar_generation

from vsource.scripts.algorithm_scripts.algorithms import parse_algorithm
from vsource.scripts.enroll_service import enroll

__version__ = 'v1.1.3'
__author__  = 'Ecohnoch'
__email__   = 'chuyuan@vsource.club'