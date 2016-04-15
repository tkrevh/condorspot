#!/usr/bin/env python
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from utils.imgutil import generate_task_img
generate_task_img(sys.argv[1], sys.argv[2])
