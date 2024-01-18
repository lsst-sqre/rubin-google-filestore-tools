"""Test basic module functionality."""
import rubin_google_filestore_tools


def test_import() -> None:
    """Test that module imported and we can create an object."""
    bkt = rubin_google_filestore_tools.filestore.FilestoreTool(
        project="my-project",
        location="us-central1-c",
        instance="my-filestore",
    )
    assert bkt is not None
