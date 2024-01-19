"""Test basic module functionality."""
import google.auth
import rubin_google_filestore_tools
import rubin_google_filestore_tools.filestore


def test_import() -> None:
    """Test that module imported and we can create an object."""
    try:
        bkt = rubin_google_filestore_tools.filestore.FilestoreTool(
            project="my-project",
            location="us-central1-c",
            instance="my-filestore",
        )
        assert bkt is not None
    except google.auth.exceptions.DefaultCredentialsError:
        # We do not have credentials when we're running under GHA
        pass
