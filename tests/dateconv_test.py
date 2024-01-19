"""Test date-to-backup-name conversion."""

import datetime
import zoneinfo

import rubin_google_filestore_tools.filestore
import rubin_google_filestore_tools.util

TEST_DATE = datetime.datetime(
    year=2024,
    month=1,
    day=15,
    hour=13,
    minute=33,
    second=40,
    tzinfo=zoneinfo.ZoneInfo("MST"),
)


def test_date_to_backup() -> None:
    name = rubin_google_filestore_tools.util.backup_name_from_datetime(
        TEST_DATE
    )
    assert name == "bk-20240115203340z"


def test_date_to_backup_with_prefix() -> None:
    name = rubin_google_filestore_tools.util.backup_name_from_datetime(
        TEST_DATE,
        prefix="archive-",
    )
    assert name == "archive-20240115203340z"
