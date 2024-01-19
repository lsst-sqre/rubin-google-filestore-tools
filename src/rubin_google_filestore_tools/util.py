"""Utility functions for Filtestore tools."""

import datetime

DEFAULT_BACKUP_PREFIX = "bk-"
ENV_PREFIX = "RUBIN_GOOGLE_FILESTORE_TOOLS_"


def backup_name_from_datetime(
    timestamp: datetime.datetime, prefix: str | None = None
) -> str:
    """Make backup name: prefix (default is "bk-") prepended to a
    string representation of the given datestamp rendered into UTC,
    with components zero-padded, and with a lowercase "z" at the end.

    The prefix can be varied; for instance, in order to create
    periodic archival backups not prone to pruning.
    """
    if prefix is None:
        prefix = DEFAULT_BACKUP_PREFIX
    utc = timestamp.astimezone(datetime.UTC)
    return (
        f"{prefix}{utc.year}{utc.month:02d}{utc.day:02d}"
        f"{utc.hour:02d}{utc.minute:02d}{utc.second:02d}z"
    )


def str_bool(inp: str) -> bool:
    """Convert a string into our best guess at its boolean meaning."""
    inp = inp.upper()
    if not inp or inp.startswith(("F", "N")):
        return False
    return True
