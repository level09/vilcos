import os
import sys
from importlib import resources

def get_root_path(package_name: str = 'vilcos') -> str:
    """Returns the path to the package root."""
    try:
        with resources.files(package_name) as path:
            return str(path)
    except (ImportError, TypeError):
        # Fallback for development mode
        return os.path.abspath(os.path.dirname(sys.modules[package_name].__file__))
