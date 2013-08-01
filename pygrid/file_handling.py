""" Implements most file handling functions for pygrid """

# Copyright (c) 2013 Felix Brockherde
# License: BSD

import shutil
import os
from os.path import join as pjoin
from os.path import exists as pexists
import cPickle as pickle
import time
try:
    import numpy
except:
    numpy = None


def _save_data(filename, data):
    if numpy:
        with open(filename, 'w') as f:
            if type(data) == dict:
                numpy.savez(f, **data)
            else:
                numpy.save(f, data)
    else:
        with open(filename, 'w') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def _load_data(filename):
    if numpy:
        data = numpy.load(filename)
        if hasattr(data, 'files'):
            return dict(data)
        else:
            return data
    else:
        with open(filename) as f:
            return pickle.load(f)


def _create_folder(temp_folder):
    os.makedirs(temp_folder)


def delete_folder(temp_folder):
    if os.path.exists(temp_folder):
        if os.path.isdir(temp_folder):
            shutil.rmtree(temp_folder)
        else:
            raise ValueError('`' + temp_folder + '` is not a folder.')


def _write_info(temp_folder, function_name, path, module, cluster_params,
                njobs):
    with open(pjoin(temp_folder, 'info'), 'w') as f:
        pickle.dump({'function_name': function_name,
                     'path': path,
                     'module': module,
                     'cluster_params': cluster_params,
                     'timestamp': time.time(),
                     'njobs': njobs}, f, pickle.HIGHEST_PROTOCOL)


def _get_info(temp_folder):
    with open(pjoin(temp_folder, 'info')) as f:
        return pickle.load(f)


def _write_files(temp_folder, args):
    # find args that are common for every job
    common_args = {}
    for key in args[0]:
        if all(key in arg and id(args[0][key]) == id(arg[key]) for
                arg in args):
            common_args[key] = args[0][key]
            for arg in args:
                del arg[key]

    # write common args
    if len(common_args) > 0:
        _save_data(pjoin(temp_folder, 'common_args'), common_args)

    # write individual args
    for i, arg in enumerate(args):
        if len(arg) > 0:
            _save_data(pjoin(temp_folder, 'args_' + str(i)), arg)

    # touch is_pygrid file
    open(pjoin(temp_folder, 'is_pygrid'), 'w').close()


def get_results(temp_folder):
    if not os.path.exists(temp_folder):
        return None

    info = _get_info(temp_folder)
    results = []
    for i in range(info['njobs']):
        try:
            results.append(_load_data(pjoin(temp_folder, 'result_' + str(i))))
        except IOError:
            results.append(None)
    return results


def _get_job_args(temp_folder, id, common_args):
        if pexists(pjoin(temp_folder, 'args_' + str(id))):
            return dict(_load_data(pjoin(temp_folder, 'args_' + str(id))),
                        **common_args)
        else:
            return common_args


def _get_common_args(temp_folder):
    if pexists(pjoin(temp_folder, 'common_args')):
        return _load_data(pjoin(temp_folder, 'common_args'))
    else:
        return {}


def get_args(temp_folder):
    info = _get_info(temp_folder)
    common_args = _get_common_args(temp_folder)
    args = []
    for i in range(info['njobs']):
        args.append(_get_job_args(temp_folder, i, common_args))
    return args


def _write_job_map(temp_folder, qid, ids):
    # write file that maps the cluster job tasks to jobs from the args list
    with open(os.path.join(temp_folder, 'submit_map_' + qid), 'w') as f:
        f.write(' '.join([str(id) for id in ids]))


def _get_job_map(temp_folder, qid):
    # write file that maps the cluster job tasks to jobs from the args list
    with open(os.path.join(temp_folder, 'submit_map_' + qid)) as f:
        return [int(id) for id in f.read().split()]


def _get_qids(temp_folder):
    with open(os.path.join(temp_folder, 'qids')) as f:
        return f.read().split()


def delete_all_folders(root):
    folders = []
    print('Searching for pygrid folders...')
    for folder, dirs, files in os.walk(root):
        if 'is_pygrid' in files:
            info = _get_info(folder)
            folders.append((folder, info['timestamp']))
    folders.sort(key=lambda (folder, timestamp): timestamp)

    delete = []
    for folder, timestamp in folders:
        a = raw_input('Delete folder ' + folder + ' (Created ' +
                      time.strftime('%d %b %Y', time.localtime(timestamp)) +
                      ')? y/[n] ')
        if len(a) > 0 and a[0].lower() == 'y':
            delete.append(folder)

    for folder in delete:
        print('Deleting ' + folder + ' ...')
        delete_folder(folder)
