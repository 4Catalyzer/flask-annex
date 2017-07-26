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


def recursive_glob(rootdir, pattern='*'):
    """Search recursively for files matching a specified pattern.

    Adapted from http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python  # noqa: E501
    """

    matches = []
    for root, _dirnames, filenames in os.walk(rootdir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))

    return matches
