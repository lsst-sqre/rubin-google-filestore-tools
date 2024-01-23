"""Test the CLI."""

import argparse
import os
import subprocess

import rubin_google_filestore_tools
import rubin_google_filestore_tools.cli
import rubin_google_filestore_tools.util

_SHORTENVS = (
    "PROJECT",
    "ZONE",
    "INSTANCE",
    "SHARE_NAME",
    "DEBUG",
    "BACKUP_PREFIX",
    "KEEP_BACKUPS",
)
ENVVARS = [
    f"{rubin_google_filestore_tools.util.ENV_PREFIX}{x}" for x in _SHORTENVS
]


def test_backup_cli() -> None:
    cp = subprocess.run("create_backup", check=False)
    assert cp.returncode == 1  # It won't have the arguments
    cp = subprocess.run("purge_backups", check=False)
    assert cp.returncode == 1


def test_env_args() -> None:
    envvals = {
        "RUBIN_GOOGLE_FILESTORE_TOOLS_PROJECT": "myproject-4381",
        "RUBIN_GOOGLE_FILESTORE_TOOLS_ZONE": "us-central1-a",
        "RUBIN_GOOGLE_FILESTORE_TOOLS_INSTANCE": "myinstance",
        "RUBIN_GOOGLE_FILESTORE_TOOLS_SHARE_NAME": "fake_share",
        "RUBIN_GOOGLE_FILESTORE_TOOLS_KEEP_BACKUPS": "4",
        "RUBIN_GOOGLE_FILESTORE_TOOLS_BACKUP_PREFIX": "w-bk-",
        "RUBIN_GOOGLE_FILESTORE_TOOLS_DEBUG": "true",
    }
    for k in envvals:
        os.environ[k] = envvals[k]
    parser = argparse.ArgumentParser()
    rubin_google_filestore_tools.cli._add_generic_options(parser)
    rubin_google_filestore_tools.cli._add_backup_options(parser)
    args = parser.parse_args([])
    assert args.project == envvals["RUBIN_GOOGLE_FILESTORE_TOOLS_PROJECT"]
    assert args.zone == envvals["RUBIN_GOOGLE_FILESTORE_TOOLS_ZONE"]
    assert args.instance == envvals["RUBIN_GOOGLE_FILESTORE_TOOLS_INSTANCE"]
    assert (
        args.share_name == envvals["RUBIN_GOOGLE_FILESTORE_TOOLS_SHARE_NAME"]
    )
    assert args.keep == int(
        envvals["RUBIN_GOOGLE_FILESTORE_TOOLS_KEEP_BACKUPS"]
    )
    assert args.debug
    # Reset environment
    for k in envvals:
        del os.environ[k]
