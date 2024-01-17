"""Create, list, and purge Google backups."""

import datetime
import logging

from google.cloud import filestore_v1

from .util import DEFAULT_BACKUP_PREFIX, backup_name_from_datetime


class BackupTool:
    """Create, list, and purge Google Filestore backups.  Each instance of
    the BackupTool class corresponds to a single file share.
    """

    def __init__(
        self,
        project: str,
        location: str,
        instance: str,
        share_name: str = "share1",
        debug: bool = False,  # noqa: FBT001 FBT002
    ) -> None:
        self.project = project
        self.location = location
        self.instance = instance
        self._logger = logging.getLogger(__name__)
        level = logging.INFO
        if debug:
            level = logging.DEBUG
        logging.basicConfig(level=level)
        self._logger.setLevel(level)

        # Location must be a zone, e.g. "us-central1-b"; backups only
        #  require a region, but we'll handle the chopping.
        components = location.split("-")
        if len(components) != 3:
            raise ValueError("Location must be a zone, e.g. 'us-central1-b1")
        self._zone = f"{components[0]}-{components[1]}"
        self.share_name = share_name
        # Unless we're using Enterprise Filestores (we don't as of
        #  January 2024), this is always "share1".

        # Default credentials should be fine--we will use WorkloadIdentity
        self._client = filestore_v1.CloudFilestoreManagerAsyncClient()
        self._instance_parent = f"projects/{project}/locations/{location}"
        self._backup_parent = f"projects/{project}/locations/{self._zone}"
        self._name = f"{self.instance}/{self.share_name}"
        self._logger.debug(f"BackupTool initialized for {self._name}")

    def backup(self, prefix: str | None = None) -> None:
        """Create a backup."""
        now = datetime.datetime.now(tz=datetime.UTC)
        backup_id = backup_name_from_datetime(now, prefix=prefix)
        request = filestore_v1.types.CreateBackupRequest(
            parent=self._backup_parent,
            backup=filestore_v1.types.Backup(
                description=(f"Backup for {self._name} at {now!s}"),
                source_instance=self.instance,
                source_file_share=self.share_name,
            ),
            backup_id=backup_id,
        )
        # Fire and forget; weirdly, the AsyncClient has a sync method,
        #  but the thing that is returned is an AsyncResponse.  Forget
        #  it, Jake, it's Googletown.
        self._logger.info(f"Backup requested for {self._name}")
        self._client.create_backup(request=request)

    async def list_backups(self, prefix: str | None = None) -> list[str]:
        """List backups in Ready state for this file share."""
        if prefix is None:
            prefix = DEFAULT_BACKUP_PREFIX
        backup_list: list[str] = []
        request = filestore_v1.ListBackupsRequest(parent=self._backup_parent)
        page_result = self._client.list_instances(request=request)
        async for backup in page_result:
            # Pull out instance and backup ID
            instance_id = backup.instance.split("/")[-1]
            backup_id = backup.name.split("/")[-1]
            # Only match the right ones for this file share
            if (
                backup.source_file_share == self.share_name
                and instance_id == self.instance
                and backup_id.startswith(prefix)
                and backup.state == filestore_v1.types.Backup.State.READY
            ):
                backup_list.append(backup_id)
        # Sort backups reverse-lexigraphically, which amounts to
        # sorting them by date, newest first
        backup_list.sort(reverse=True)
        self.logger.debug(f"Backups for {self._name}: {backup_list}")
        return backup_list

    def delete_backups(self, keep: int = 6, prefix: str | None = None) -> None:
        """Delete all but 'keep' backups for this file share."""
        if keep < 1:
            raise ValueError("'keep' must be a positive integer")
        backups = self.list(prefix=prefix)
        doomed = backups[keep:]
        self._logger.info(
            f"Requesting backup deletion for {self._name}: {doomed}"
        )
        for victim in doomed:
            # Also fire-and-forget
            request = filestore_v1.types.DeleteBackupRequest(
                name=f"{self.backup_parent}/backups/{victim}"
            )
            self._client.delete_backup(request=request)
