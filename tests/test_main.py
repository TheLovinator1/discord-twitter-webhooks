from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from discord_twitter_webhooks.main import app

if TYPE_CHECKING:
    from httpx import Response


client = TestClient(app)


def test_index() -> None:
    """Test index."""
    response: Response = client.get("/")

    # Check that the page loaded successfully.
    assert response.status_code == 200  # noqa: PLR2004

    # Get the page contents.
    site_contents = response.text

    # Check that the page is not empty.
    assert site_contents

    # Check that the page has something on it.
    assert len(site_contents) > 1000  # noqa: PLR2004

    # Check that the page contains our HTML and not some other HTML.
    assert "p-2 mb-2 border border-dark" in site_contents

    # Check that the page contains either the "Add a new feed" button or the "Remove a group" button.
    # Remove a group button is only shown if there is at least one group.
    # Add a new feed button is only shown if there are no groups.
    try:
        assert "Add a new feed" in site_contents
    except AssertionError:
        assert "remove_group" in site_contents
    except Exception as err:  # noqa: BLE001
        pytest.fail(f"Unexpected error: {err}")
