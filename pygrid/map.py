""" Implements map function for pygrid """

# Copyright (c) 2013 Felix Brockherde
# License: BSD

import os
import inspect

from .file_handling import get_results, _write_files, _write_info, _get_info
from .file_handling import delete_folder, _create_folder
from .progress import get_progress, _disp_progress
from .run import _submit_jobs, _simulate_jobs


def map(function, args, temp_folder='temp_pygrid', use_cluster=True,
        cluster_params=None, nest=False):
    # test if pygrid map is called inside a pygrid map instance
    if not nest and os.environ.get('PYGRID') == 1:
        raise Exception('PyGrid called itself inside a PyGrid instance. ' +
                        'Read the tutorial on how to avoid this.')

    # input tests
    if not hasattr(function, '__call__'):
        raise ValueError('`function` has to be callable.')
    if not os.path.exists(os.path.abspath(inspect.stack()[1][1])):
        raise Exception('Can not find the file from which `map` was called.')
    if not type(args) == list and all(type(arg) == dict for arg in args):
        raise ValueError('`args` has to be a list of dicts.')
    if cluster_params is None:
        cluster_params = []
    elif type(cluster_params) == str:
        cluster_params = [cluster_params]
    elif not hasattr(cluster_params, '__iter__'):
        # TODO: do more testing here
        raise ValueError('`cluster_params` must be a list of parameters')

    # handle existing temp_folder
    if os.path.exists(temp_folder):
        a = raw_input('Path `' + os.path.abspath(temp_folder) +
                      '` exists. Delete? y/[n]: ')
        if len(a) > 0 and a[0].lower() == 'y':
            delete_folder(temp_folder)
            write = True
        elif os.path.exists(os.path.join(temp_folder, 'is_pygrid')):
            print('Path is pygrid folder, continuing.')
            write = False
        else:
            raise ValueError('Can not continue with temp_folder `' +
                             temp_folder + '`.')
    else:
        write = True

    if write:
        _create_folder(temp_folder)
        _write_files(temp_folder, args)
        function_name = function.__name__
        module = function.__module__
        call_file = os.path.abspath(inspect.stack()[1][1])
        if module == '__main__':
            module = os.path.splitext(os.path.split(call_file)[1])[0]
        path = os.path.split(call_file)[0]
        _write_info(temp_folder, function_name, path, module, cluster_params,
                    len(args))

        if use_cluster:
            res = _submit_jobs(temp_folder, range(len(args)), cluster_params)
            if res is not True:
                raise Exception('Could not submit job: ' + res)

            _disp_progress(temp_folder)
        else:
            _simulate_jobs(temp_folder, range(len(args)))

    return get_results(temp_folder)


def restart(temp_folder, cluster_params=None):
    jobs = get_progress(temp_folder)
    if cluster_params is None:
        params = _get_info(temp_folder)['cluster_params']
    res = _submit_jobs(temp_folder, jobs['failed'], params)
    if res is not True:
        raise Exception('Could not submit job: ' + res)
