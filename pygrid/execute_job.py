""" This file gets called by the sh file for pygrid jobs """

# Copyright (c) 2013 Felix Brockherde
# License: BSD

import sys
import os

from file_handling import _get_info, _get_common_args,  _get_job_args
from file_handling import _save_data

if __name__ == '__main__':
    assert(len(sys.argv) == 3)

    # find out which id to run
    with open('submit_map_' + sys.argv[1]) as f:
        id = [int(id) for id in f.read().split()][int(sys.argv[2]) - 1]

    # load args
    common_args = _get_common_args('')
    args = _get_job_args('', id, common_args)

    # load info
    info = _get_info('')

    # change dir to function dir
    oldcwd = os.getcwd()
    os.chdir(info['path'])

    # import function file
    sys.path.append(info['path'])
    module = __import__(info['module'])

    # execute job function
    result = getattr(module, info['function_name'])(**args)

    # change directory back
    os.chdir(oldcwd)

    # write results to file
    _save_data('result_' + str(id), result)
