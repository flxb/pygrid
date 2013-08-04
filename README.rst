PyGrid
======

PyGrid provides a map-like interface for job submissions to gridengine clusters. Read the installation instructions and the tutorial in the `documentation<http://flxb.github.io/pygrid>`_.

Features
--------

* No dependencies
* Easy to use: no code rewrite necessary
* Robust: Interactive interface allows to resubmit single jobs with different resource requests
* Well documented: `Tutorial<http://flxb.github.io/pygrid>` and `Function reference<http://flxb.github.io/pygrid/function_reference.html>`_

Example use
-----------

.. code-block:: python

   import pygrid


   def example_function(arg1, arg2, arg3=2):
       return arg1 + arg2 * arg3

   if __name__ == '__main__':
       args = [{'arg1': 1, 'arg2': 2},
               {'arg1': 2, 'arg2': 3, 'arg3': 4}]

       results = pygrid.map(example_function, args, temp_folder='tmp',
                            use_cluster=True)

       print results  # will print [array(5), array(14)]
