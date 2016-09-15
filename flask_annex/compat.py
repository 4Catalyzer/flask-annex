import sys

# -----------------------------------------------------------------------------

PY2 = sys.version_info[0] == 2

# -----------------------------------------------------------------------------

if PY2:
    string_types = (str, unicode)  # flake8: noqa
else:
    string_types = (str,)


# From six.
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})
