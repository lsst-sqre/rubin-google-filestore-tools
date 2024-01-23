"""Command-line interface for Google Filestore tools."""
import argparse
import os

from .filestore import FilestoreTool
from .util import DEFAULT_BACKUP_PREFIX, ENV_PREFIX, str_bool


def _add_generic_options(
    parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Add options applicable to any filestore tool."""
    parser.add_argument(
        "-p",
        "--project",
        help="Google project containing filestore",
        default=os.environ.get(f"{ENV_PREFIX}PROJECT"),
    )
    parser.add_argument(
        "-z",
        "--zone",
        "--location",
        help="GCP zone containing filestore",
        default=os.environ.get(f"{ENV_PREFIX}ZONE"),
    )
    parser.add_argument(
        "-i",
        "--instance",
        help="Filestore instance name",
        default=os.environ.get(f"{ENV_PREFIX}INSTANCE"),
    )
    parser.add_argument(
        "-s",
        "--share-name",
        help="Filestore share name (Enterprise only)",
        default=os.environ.get(f"{ENV_PREFIX}SHARE_NAME", "share1"),
    )
    parser.add_argument(
        "-d",
        "--debug",
        "--verbose",
        action="store_true",
        default=str_bool(os.environ.get(f"{ENV_PREFIX}DEBUG", "")),
        help="Verbose debugging output",
    )
    return parser


def _add_backup_options(
    parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Add options applicable to backup operations."""
    parser.add_argument(
        "-r",
        "--prefix",
        default=os.environ.get(
            f"{ENV_PREFIX}BACKUP_PREFIX", DEFAULT_BACKUP_PREFIX
        ),
        help="Prefix to add to backup names",
    )
    parser.add_argument(
        "-k",
        "--keep",
        type=int,
        default=int(os.environ.get(f"{ENV_PREFIX}KEEP_BACKUPS", 6)),
        help="Number of backups to keep",
    )
    return parser


def _parse_backup_args() -> argparse.Namespace:
    """Get arguments for a configured backup tool."""
    parser = argparse.ArgumentParser()
    parser = _add_generic_options(parser)
    parser = _add_backup_options(parser)
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    if not args.project:
        raise ValueError("Project is required")
    if not args.zone:
        raise ValueError("Zone is required")
    if not args.instance:
        raise ValueError("Instance is required")


def _backup_tool(args: argparse.Namespace) -> FilestoreTool:
    return FilestoreTool(
        project=args.project,
        location=args.zone,
        instance=args.instance,
        share_name=args.share_name,
        debug=args.debug,
    )


def create_backup() -> None:
    """Create a backup."""
    args = _parse_backup_args()
    _validate_args(args)
    tool = _backup_tool(args)
    tool.backup(prefix=args.prefix)


def purge_backups() -> None:
    """Purge all but 'keep' backups."""
    args = _parse_backup_args()
    _validate_args(args)
    if args.keep < 1:
        raise ValueError("Keep must be at least 1")
    tool = _backup_tool(args)
    tool.purge_backups(prefix=args.prefix, keep=args.keep)
