import fnmatch
import os
import sys

# -----------------------------------------------------------------------------

PY2 = sys.version_info[0] == 2

# -----------------------------------------------------------------------------

if PY2:
    string_types = (str, unicode)  # noqa: F821
else:
    string_types = (str,)

# -----------------------------------------------------------------------------


def recursive_glob(root_dir, pattern='*'):
    """Search recursively for files matching a specified pattern.

    Adapted from http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python  # noqa: E501
    """
    return tuple(
        os.path.join(root, filename)
        for root, _dirnames, filenames in os.walk(root_dir)
        for filename in fnmatch.filter(filenames, pattern),
    )
