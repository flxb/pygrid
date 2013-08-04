import pygrid
import time


def example_function(arg1, arg2, arg3=2):
    print('Running example function with args ' + str((arg1, arg2, arg3)))
    return arg1 + arg2 * arg3

if __name__ == '__main__':
    args = [{'arg1': 1, 'arg2': 2},
            {'arg1': 2, 'arg2': 3, 'arg3': 4}]

    temp_folder = 'tmp'

    # submit jobs
    results = pygrid.map(example_function, args, temp_folder=temp_folder,
                         use_cluster=True, interactive=False)

    # wait till all jobs are finished
    while True:
        time.sleep(1)
        progress = pygrid.get_progress(temp_folder)
        if len(progress['waiting']) + len(progress['running']) == 0:
            break

    # get results
    results = pygrid.get_results(temp_folder)

    print results  # will print [array(5), array(14)]
