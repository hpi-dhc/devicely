"""
Helper functions
"""

import os

def file_empty_or_not_existing(path):
    return not os.path.isfile(path) or os.stat(path).st_size == 0