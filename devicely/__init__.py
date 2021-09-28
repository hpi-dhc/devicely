"""
Import all readers.
"""
from .empatica import EmpaticaReader
from .everion import EverionReader
from .faros import FarosReader
from .time_stamp import TimeStampReader
from .spacelabs import SpacelabsReader
from .shimmer_plus import ShimmerPlusReader
from .muse import MuseReader

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)

