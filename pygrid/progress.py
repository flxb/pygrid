""" Implements functions that get and display progress info for pygrid """

# Copyright (c) 2013 Felix Brockherde
# License: BSD

import os
import subprocess
import time
import termios
import fcntl
import sys

from .file_handling import _get_job_map, _get_info, _get_qids, delete_folder
from .run import _submit_jobs


def get_progress(temp_folder):
    """ Returns progress information

    Parameters
    ----------
    temp_folder : string
        The temprary folder that was given when the job was submitted first.

    Returns
    -------
    output : dict
        A dict where the values are the indices of the jobs and the keys are:

        - waiting
        - running
        - failed
        - finished
        
    """
    jobs = {}
    jobs['all'] = range(_get_info(temp_folder)['njobs'])

    qids = _get_qids(temp_folder)

    # get job maps
    job_maps = {}
    for qid in qids:
        job_maps[qid] = _get_job_map(temp_folder, qid)

    # get jobs running and waiting
    output = subprocess.Popen(
        ['qstat', '-g', 'd'],
        stdout=subprocess.PIPE).communicate()[0].split(os.linesep)
    first = output[0]
    status_marker = first.find('state')
    jobs['running'] = []
    jobs['waiting'] = []
    for line in output[2:]:
        if line == '':
            break
        qid = line.split()[0]
        if qid in qids:
            task_id = int(line.split()[-1])
            id = job_maps[qid][task_id - 1]
            status = line[status_marker:status_marker + 2]
            if status == 'r ':
                jobs['running'].append(id)
            elif status == 'qw':
                jobs['waiting'].append(id)
            else:
                # consider all these jobs (dr, t, ...) as done
                pass

    # get jobs for which result files are found
    files = os.listdir(temp_folder)
    jobs['finished'] = [int(f.split('_')[1]) for f in files if
                        f.startswith('result_')]

    # compute which jobs have failed
    jobs['failed'] = [id for id in jobs['all'] if
                      id not in jobs['finished'] and
                      id not in jobs['running'] and id not in jobs['waiting']]

    return jobs


def _disp_progress(temp_folder):

    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    t = 0
    extra_lines = None
    extra_lines_length = []
    status_line_length = 0
    abort = False
    confirm = None
    cluster_params = ''
    print('')
    try:
        while abort is False:
            try:
                c = repr(sys.stdin.read(1))[1:-1]
                t = 0
                if confirm is not None and c != 'y':
                    # action was aborted
                    confirm = None
                    extra_lines = None
                elif confirm is not None and c == 'y':
                    # action was confirmed
                    if confirm == 'a':
                        qids = _get_qids(temp_folder)
                        for qid in qids:
                            p = subprocess.Popen(['qdel', qid],
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
                            p.communicate()
                        abort = True
                    elif confirm == 'c':
                        abort = True
                    elif confirm == 'r':
                        jobs = get_progress(temp_folder)
                        params = cluster_params.split(';')
                        res = _submit_jobs(temp_folder, jobs['failed'], params)
                        if res is False:
                            extra_lines = ['Could not submit job. Are your ' +
                                           ' `cluster_params` valid?']
                        else:
                            extra_lines = None
                    elif confirm == 'R':
                        # get all jobs
                        jobs = get_progress(temp_folder)

                        # kill old jobs
                        qids = _get_qids(temp_folder)
                        for qid in qids:
                            p = subprocess.Popen(['qdel', qid],
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
                            p.communicate()

                        # start new jobs
                        params = cluster_params.split(';')
                        res = _submit_jobs(temp_folder, jobs['all'], params)
                        if res is True:
                            extra_lines = ['Could not submit job. Are your ' +
                                           ' `cluster_params` valid?']
                        else:
                            extra_lines = None
                    elif confirm == 'q':
                        qids = _get_qids(temp_folder)
                        for qid in qids:
                            p = subprocess.Popen(['qdel', qid],
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
                            p.communicate()
                        delete_folder(temp_folder)
                        abort = True
                    confirm = None
                else:
                    # action key was pressed
                    if c == '?':
                        extra_lines = [
                            'Press these keys to control the jobs:',
                            'a: abort remaining jobs and continue',
                            'q: abort jobs, delete files and continue',
                            'c: keep jobs running and continue',
                            'r: restart failed',
                            'R: restart all',
                            'Ctrl-C: keep jobs running and come back later']
                    elif c == 'a':
                        extra_lines = ['Press y to abort, any other key to ' +
                                       'cancel.']
                        confirm = 'a'
                    elif c == 'c':
                        extra_lines = ['Press y to continue, any other key ' +
                                       'to cancel.']
                        confirm = 'c'
                    elif c == 'r' or c == 'R':
                        q = ('Enter cluster_params (separated by `;`) and ' +
                             'press Enter: ')
                        print(q)
                        cluster_params = ';'.join(_get_info(
                            temp_folder)['cluster_params'])
                        sys.stdout.write(cluster_params)
                        while True:
                            set_break = False
                            try:
                                c2 = sys.stdin.read(1)
                                if ord(c2) == 127:
                                    sys.stdout.write('\033[D \033[D')
                                    cluster_params = cluster_params[:-1]
                                elif ord(c2) == 10:
                                    set_break = True
                                    sys.stdout.write('\n')
                                    break
                                else:
                                    c2 = repr(c2)[1:-1]
                                    sys.stdout.write(c2)
                                    cluster_params += c2
                            except IOError:
                                pass
                            if set_break:
                                break
                        extra_lines_length.append(len(q))
                        extra_lines_length.append(len(cluster_params))
                        alltext = ' ALL' if c == 'R' else ''
                        extra_lines = ['Press y to restart' + alltext + ', ' +
                                       'any other key to cancel.']
                        confirm = c
                    elif c == 'q':
                        extra_lines = ['Press y to quit, any other key to ' +
                                       'cancel.']
                        confirm = 'q'
                    else:
                        extra_lines = None
            except IOError:
                if time.time() - t >= 1:
                    t = time.time()
                    # delete old lines
                    for l in extra_lines_length[::-1]:
                        print('\033[A' + ' ' * l + '\033[A')
                    print('\033[A' + ' ' * status_line_length + '\033[A')

                    # write progress line
                    jobs = get_progress(temp_folder)
                    if set(jobs['all']) == set(set(jobs['finished'])):
                        abort = True
                    l = ('%d Jobs: %d Finished / %d Running / %d Failed / %d'
                         ' in Queue (press ? for help)' % (
                             len(jobs['all']),
                             len(jobs['finished']), len(jobs['running']),
                             len(jobs['failed']), len(jobs['waiting'])))
                    print(l)
                    status_line_length = len(l)
                    extra_lines_length = []

                    # write extra lines if necessary
                    if extra_lines is not None:
                        for line in extra_lines:
                            print(line)
                            extra_lines_length.append(len(line))

    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
