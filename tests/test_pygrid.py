""" Some basic tests for pygrid """

# Copyright (c) 2013 Felix Brockherde
# License: BSD

import time
import os


def example_function(arg1, arg2=10):
    if arg2 == 0:
        raise Exception('Let one job fail.')
    time.sleep(3 * arg1)
    return arg1, arg2


def run_simple(use_cluster):
    import pygrid
    if not use_cluster:
        temp = 'temp1'
    else:
        temp = 'temp2'
    args = [{'arg1': 1, 'arg2': 5}, {'arg1': 2}, {'arg1': 1, 'arg2': 0}]
    pygrid.delete_folder(temp)
    res = pygrid.map(function=example_function, args=args, temp_folder=temp,
                     use_cluster=use_cluster,
                     cluster_params=['-l h_rt=00:00:30', '-l vf=1.0G',
                                     '-l h_vmem=1.0G'])
    assert(res[0][0] == args[0]['arg1'] and res[0][1] == args[0]['arg2'] and
           res[1][0] == args[1]['arg1'] and res[1][1] == 10 and res[2] is None)

    # test restart
    res = pygrid.map(function=example_function, args=args, temp_folder=temp,
                     use_cluster=use_cluster)
    assert(res[0][0] == args[0]['arg1'] and res[0][1] == args[0]['arg2'] and
           res[1][0] == args[1]['arg1'] and res[1][1] == 10 and res[2] is None)


def test_simple_serial():
    run_simple(use_cluster=False)


def test_simple_parallel():
    run_simple(use_cluster=True)


def test_delete_all():
    import pygrid
    pygrid.delete_all_folders(os.getcwd())
