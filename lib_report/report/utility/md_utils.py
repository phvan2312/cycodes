#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Andrew <hieu@cinnamon.is>"
import time
import os
import logging

# Get the logger specified in the file
logging.basicConfig(level=logging.INFO, format='TIMER: %(message)s')
logger = logging.getLogger(__name__)


def elapse_time(f):
    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = f(*args, **kwargs)
        logger.info(
            '[%s.%s] - Elapsed time: %fs' % (f.__module__, f.__name__, (time.time() - start)))
        return return_value

    return wrapper


def tree(input_dir, print_files=False, padding=' ', fcount=0):
    """
    Display tree folder of model
    :param input_dir:
    :param padding:
    :param print_files:
    :return:
    """
    suffix = ''
    ignore_dicts = ['__pycache__', '.idea']
    ignore_files = ['.DS_Store']
    if print_files:
        files = os.listdir(input_dir)
    else:
        files = [x for x in os.listdir(input_dir) if os.path.isdir(input_dir + os.sep + x)]

    new_files = []
    for file in files:
        if file not in ignore_dicts and file not in ignore_files:
            new_files.append(file)

    if fcount == 0:
        prefix = '└──'
    else:
        prefix = '├──'

    dict_name = os.path.basename(os.path.abspath(input_dir))
    if dict_name not in ignore_dicts:
        print(padding[:-1] + prefix + dict_name + suffix)
        padding = padding + '   '
        count = 0
        for file in new_files:
            count += 1
            print(padding + '│ ')
            path = input_dir + os.path.sep + file
            if os.path.isdir(path):
                if count == len(files):
                    tree(path, print_files, padding + ' ', 0)
                else:
                    tree(path, print_files, padding + '│', len(files))
            else:
                print(padding + '├──' + file)
