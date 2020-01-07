#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 eelium <eelium@eez008>
#
# Distributed under terms of the MIT license.
import random
"""
parameters 
"""
# the ground size
margin_left = margin_right = margin_bottom = 50
margin_top = 100
L = 50  # unit value in pixel; as scalar
# the window size
world_height = 11 * L + margin_top + margin_bottom
world_width = 16 * L + margin_left + margin_right


# robot numbers
num_agents = 6
num_areas = 6
# agent speed
agent_speed = 40
# TODO: parameterize this magic number
TIME_RATE = 2
FRAME_PER_SECOND = 20.0
# collision allows the angle
th_close_angle = 30

# good position letter (forward,backward)
GOOD_FIND_LETTER_UP_LEFT = [
    ('G', 'A'), ('B', 'H'), ('I', 'C'), ('D', 'J'), ('K', 'E')]
GOOD_FIND_LETTER_UP_RIGHT = [
    ('B', 'H'), ('I', 'C'), ('D', 'J'), ('K', 'E'), ('F', 'L')]
GOOD_FIND_LETTER_DOWN_LEFT = [
    ('M', 'G'), ('H', 'N'), ('O', 'I'), ('J', 'P'), ('Q', 'K')]
GOOD_FIND_LETTER_DOWN_RIGHT = [
    ('H', 'N'), ('O', 'I'), ('J', 'P'), ('Q', 'K'), ('L', 'R')]

# letter distance
ROW_LETTER = ['AB', 'BC', 'CD', 'DE', 'EF', 'GH', 'HI',
              'IJ', 'JK', 'KL', 'RQ', 'QP', 'PO', 'ON', 'NM']
COLUMN_LETTER = [
    'MG', 'GA', 'BH', 'HN', 'OI', 'IC', 'DJ', 'JP', 'QK', 'KE', 'FL', 'LR']

# goods numbers
goodstotal = 10

GOOD_NUM = [11, 8, 39, 28, 53, 1, 69, 42, 79, 6]  # test1
# GOOD_NUM = [74, 50, 62, 15, 49, 34, 14, 72, 31, 37]
# GOOD_NUM = [68, 79, 56, 47, 48, 75, 23, 50, 76, 16]
# GOOD_NUM = [59, 6, 74, 2, 67, 49, 53, 28, 25, 79]
# GOOD_NUM = [14, 65, 41, 75, 22, 36, 54, 74, 9, 48]
