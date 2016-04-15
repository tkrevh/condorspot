#!/usr/bin/env python
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from utils.util import restore_done_files
restore_done_files(sys.argv[1])
