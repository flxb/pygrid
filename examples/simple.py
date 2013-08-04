import pygrid


def example_function(arg1, arg2, arg3=2):
    print('Running example function with args ' + str((arg1, arg2, arg3)))
    return arg1 + arg2 * arg3

if __name__ == '__main__':
    args = [{'arg1': 1, 'arg2': 2},
            {'arg1': 2, 'arg2': 3, 'arg3': 4}]

    results = pygrid.map(example_function, args, temp_folder='tmp',
                         use_cluster=True)

    print results  # will print [array(5), array(14)]
