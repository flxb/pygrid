""" PyGrid allows to distribute python function calls on a gridengine cluster

"""

__version__ = '1.0.0'

from .map import map, restart
from .progress import get_progress
from .file_handling import get_results, get_args, delete_folder
from .file_handling import delete_all_folders
