"""Pandas 1/2 compatibility."""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

_pd_version = importlib_metadata.version('pandas')
_pd_major = int(_pd_version.split('.')[0])
_have_pd_2 = _pd_major >= 2
# Pandas 1.5 renamed the `line_terminator` parameter of the `to_csv` method to
# `lineterminator` for consistency, and then Pandas 2 removed the old name.
_to_csv_line_terminator = 'lineterminator' if _have_pd_2 else 'line_terminator'
