""" Implements functions that run jobs for pygrid """

# Copyright (c) 2013 Felix Brockherde
# License: BSD

import os
import inspect
import subprocess

from .file_handling import _write_job_map


def _submit_jobs(temp_folder, ids, cluster_params):
    # find file that does not exist yet
    file_no = 1
    while os.path.exists(os.path.join(temp_folder, 'submit_' + str(file_no) +
                                      '.sh')):
        file_no += 1

    # write sh file
    with open(os.path.join(temp_folder, 'submit_' + str(file_no) + '.sh'),
              'w') as f:
        f.write('#!/bin/bash\n')
        f.write('#$ -cwd\n')
        f.write('#$ -t 1-' + str(len(ids)) + '\n')
        f.write('#$ -e log_error_$TASK_ID\n')
        f.write('#$ -o log_output_$TASK_ID\n')
        f.write('#$ -S /bin/bash\n')
        for p in cluster_params:
            f.write('#$ ' + p + '\n')
        f.write('\n')
        f.write('export PYGRID=1\n')  # set PYGRID to avoid accidental nesting
        f.write('')
        current_dir = os.path.split(os.path.abspath(inspect.stack()[0][1]))[0]
        f.write('python ' + os.path.join(current_dir, 'execute_job.py') +
                ' ${JOB_ID} ${SGE_TASK_ID}\n')

    # submit the jobs
    output = subprocess.Popen(
        ['qsub', 'submit_' + str(file_no) + '.sh'],
        stderr=subprocess.PIPE, stdout=subprocess.PIPE,
        cwd=temp_folder).communicate()[0]

    # save the qid
    # output should be Your job-array 1234.1-...
    try:
        ref, qid_string = output.split(' job-array ')
    except ValueError:
        return output
    if ref != 'Your' or '.' not in qid_string:
        return output
    qid = qid_string.split('.')[0]
    with open(os.path.join(temp_folder, 'qids'), 'a') as f:
        f.write(qid + ' ')

    _write_job_map(temp_folder, qid, ids)
    return True


def _simulate_jobs(temp_folder, ids):
    qid = '000'  # dummy id
    _write_job_map(temp_folder, qid, ids)

    for i, id in enumerate(ids):
        print('Starting job with id ' + str(id) + ' (' + str(i) + '/' +
              str(len(ids)) + ')')
        current_dir = os.path.split(os.path.abspath(inspect.stack()[0][1]))[0]
        subprocess.call(['python', os.path.join(
            current_dir, 'execute_job.py'), qid, str(i + 1)], cwd=temp_folder)
