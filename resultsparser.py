#!/usr/bin/env python
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from utils.util import parse_csv_results
parse_csv_results(sys.argv[1])
