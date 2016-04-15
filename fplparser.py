#!/usr/bin/env python
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from utils.util import parse_task
parse_task(sys.argv[1])
