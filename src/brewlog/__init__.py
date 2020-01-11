from .app import make_app  # noqa: F401

from ._version import get_version
__version__ = get_version()
del get_version
