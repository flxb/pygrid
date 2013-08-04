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
        cluster_params=None, interactive=False, nest=False):
    """ Submits jobs to gridengine and returns results

    Parameters
    ----------
    function :  callable
        The function that gets run with different input parameters.
    args : list
        A list of dictionaries where each dictionary in the list is for one
        function call. The dictionary keys must match the function parameters.

        If the function has default parameters, the values do not have to be
        provided in args. PyGrid will check if any parameter values are the
        same for all function calls and save them only once.

        If an argument value is a numpy array, saving and loading is efficient
        (with numpy.savez and numpy.load).

        If the function returns a numpy array or a dict of numpy arrays,
        saving and loading of return values is efficient, too.
    temp_folder : string, optional
        A path to a folder where PyGrid will save the temporary files. PyGrid
        will ask before overwriting or reusing a folder. The folder is not
        deleted by default. Default is ``'temp_pygrid'``.
    use_cluster : bool, optional
        If set to false, the run will be simulated to make debugging easier.
        That means that all computations are done in serial in the current
        session. Default is True.
    cluster_params : list, optional
        A list of strings with additional parameters to use when submitting the
        job. E.g. ``['-l h_vmem=10G']`` to set a limit of 10Gb per job. Default
        is None.
    interactive : bool, optional
        When set to False, there will be no progress information printed and
        ``None`` will be returned without waiting for results. Default is True.
    nest : bool, optional
        Allows to nest PyGrid jobs when set to True. Otherwise an exception is
        thrown when pygrid.map gets called inside a PyGrid job. Default is
        False.

    Returns
    -------
    results : list
        A list with the results for each job. Each item in the list corresponds
        to the item in the ``args`` list from input. If the job failed or was
        not finished, the value will be None.

    Examples
    --------
    See examples directory.
    """

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

            if interactive:
                _disp_progress(temp_folder)
            else:
                return None
        else:
            _simulate_jobs(temp_folder, range(len(args)))

    return get_results(temp_folder)


def restart(temp_folder, cluster_params=None):
    """ Restarts all failed jobs.
    
    Parameters
    ----------
    temp_folder : string
        The temporary folder that was given when the job was submitted first.
    cluster_params : list, optional
        A list of strings with new parameters to use when submitting the
        job. E.g. ``['-l h_vmem=10G']`` to set a limit of 10Gb per job. Default
        is None.
    """
    jobs = get_progress(temp_folder)
    if cluster_params is None:
        params = _get_info(temp_folder)['cluster_params']
    res = _submit_jobs(temp_folder, jobs['failed'], params)
    if res is not True:
        raise Exception('Could not submit job: ' + res)
