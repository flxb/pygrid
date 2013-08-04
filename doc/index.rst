.. PyGrid documentation master file, created by
   sphinx-quickstart on Thu Aug  1 18:57:33 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :hidden:
   
   function_reference

Tutorial
====================

PyGrid allows to distribute python function calls on a gridengine cluster. This
document contains installation instructions and a tutorial.

.. note::

   You can find all functions and options in the :doc:`function_reference`.

Installation
++++++++++++
When you work on a cluster where you have no global write permissions:

.. code-block:: bash

   git clone http://github.com/flxb/pygrid
   cd pygrid
   python setup.py install --prefix=~/your/local/directory
   echo 'export PYTHONPATH=~/your/local/directory:$PYTHONPATH' >> ~/.bashrc
   source ~/.bashrc

Simple example
++++++++++++++

The simplest example of PyGrid is:

.. literalinclude:: ../examples/simple.py
   :language: python

Here, PyGrid will create a folder ``tmp`` and write all arguments and job
information into that folder. Then it will submit the jobs to the gridengine
and display a status line much like:

.. code-block:: none

   2 Jobs: 0 Finished / 0 Running / 0 Failed / 2 in Queue (press ? for help)   

This will automatically update. When all jobs are finished,
:py:meth:`~pygrid.map` will return the results.

.. warning::

   You have to include the ``pygrid.map`` call in a ``if __name__ ==
   '__main__'`` construct. PyGrid has to import the file with the function
   definition and would otherwise call itself.

.. note::

   Note that input and output values are converted to numpy arrays to make
   loading and saving more efficient (by utilizing ``numpy.save`` instead of
   ``pickle.dump``).

Debugging
+++++++++

Set ``use_cluster=False`` to debug your code. PyGrid will not use the
gridengine and start all jobs in serial, so you can see the debug output.

.. code-block:: none

   $ python examples/simple.py
   Starting job with id 0 (0/2)
   Running example function with args (array(1), array(2), 2)
   Starting job with id 1 (1/2)
   Running example function with args (array(2), array(3), array(4))
   [array(5), array(14)]

Efficient use
+++++++++++++

To run the jobs in a cluster job, PyGrid needs to save and load the input and
output parameters. This is done using numpy, which will fall back to pickle.
Pickle is very slow when saving big data structures, so it is best to avoid
this. All input parameters have to be given in a dictionary. If the dictionary
values can be transformed into a numpy array, numpy will be used to save them.
This means

.. code-block:: python

   # AVOID:
   pygrid.map(function, args={'data': (big_array1, big_array2)})

   # USE INSTEAD:
   pygrid.map(function, args={'data1': big_array1, 'data2': big_array2})

If the output is one numpy array, it will be save efficiently. If it is a dict
of numpy arrays (as for inputs) it will be saved efficiently, too. This means

.. code-block:: python

   # AVOID:
   def example_function(arg1, arg2):
       ...
       return (big_array1, big_array2)

    # USE INSTEAD:
    def example_function(arg1, arg2):
        ...
        return {'res1': big_array1, 'res2': big_array2}

If one input parameter is the same for all jobs, it will only be saved once.

Cluster parameters
++++++++++++++++++

It is possible to provide additional parameters to the gridengine. For example,

.. code-block:: python

   pygrid.map(function, cluster_params=['-l h_vmem=10G', '-l h_rt=00:30:00'])

will request a 30min slot with an upper virtual memory limit of 10Gb. See
*Resource Limits* section of `man queue_conf
<http://linux.die.net/man/5/sge_queue_conf>`_.

Non-interactive use
+++++++++++++++++++

If you do not like the interactive functionality, you can turn it off and
monitor progress and get results yourself.

.. literalinclude:: ../examples/non-interactive.py
   :language: python

Refer to the function reference for :py:meth:`~pygrid.get_progress` and
:py:meth:`~pygrid.get_results` for more information. You can use
:py:meth:`~pygrid.get_args` to get the ``args`` you submitted. If you want to
restart jobs in non-interactive mode, you can use :py:meth:`~pygrid.restart`.

Deleting temporary files
++++++++++++++++++++++++

Temporary files are not deleted automatically. If you want to delete one PyGrid
folder, use :py:meth:`~pygrid.delete_folder`. If you want to clean up and
delete many PyGrid folders under a specific path, you should look at 
:py:meth:`~pygrid.delete_all_folders`.
