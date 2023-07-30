from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from discord_twitter_webhooks.main import app

if TYPE_CHECKING:
    from httpx import Response


client = TestClient(app)
temp_name: str = f"Test_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
random_uuid: str = str(uuid4())


def test_index_page() -> None:
    """Test that the index page loads."""
    response: Response = client.get("/", timeout=5)

    # Check that the page loaded successfully.
    assert response.status_code == 200  # noqa: PLR2004

    # Check that the page is not empty.
    assert response.text

    # Check that the page has something on it.
    assert len(response.text) > 1000  # noqa: PLR2004

    # Check that the page contains our HTML and not some other HTML.
    assert "p-2 mb-2 border border-dark" in response.text

    # Check that the page contains either the "Add a new feed" button or the "Remove a group" button.
    # Remove a group button is only shown if there is at least one group.
    # Add a new feed button is only shown if there are no groups.
    try:
        assert "No groups found. You can add one" in response.text
    except AssertionError:
        assert "remove_group" in response.text
    except Exception as err:  # noqa: BLE001
        pytest.fail(f"Unexpected error: {err}")


def test_add_page() -> None:
    """Test that the add page loads."""
    response: Response = client.get("/add", timeout=5)

    # Check that the page loaded successfully.
    assert response.status_code == 200  # noqa: PLR2004

    # Check that the page is not empty.
    assert response.text

    # Check that the page has something on it.
    assert len(response.text) > 1000  # noqa: PLR2004

    # Check that the page contains our HTML and not some other HTML.
    assert "p-2 border border-dark" in response.text

    # Check that the page contains the add feed button.
    assert '<button class="btn btn-dark btn-sm">Add</button>' in response.text


def test_settings_page() -> None:
    """Test that the settings page loads."""
    response: Response = client.get("/settings")

    # Check that the page loaded successfully.
    assert response.status_code == 200  # noqa: PLR2004

    # Check that the page is not empty.
    assert response.text

    # Check that the page has something on it.
    assert len(response.text) > 1000  # noqa: PLR2004

    # Check that the page contains our HTML and not some other HTML.
    assert "p-2 border border-dark" in response.text


def test_add_new_group() -> None:
    """Test if we can add a new group."""
    # Get the old index page.
    old_index_page: Response = client.get("/", timeout=5)

    response: Response = client.post(
        "/feed",
        data={
            "name": temp_name,
            "uuid": random_uuid,
            "webhooks": "https://twitter.com/elonmusk",
            "usernames": "elonmusk",
        },  # type: ignore  # noqa: PGH003
    )

    # Check that the page loaded successfully.
    assert response.is_success

    # Check that the page is not empty.
    assert response.text

    # Check that the page has something on it.
    assert len(response.text) > 100  # noqa: PLR2004

    # Check that the index page is smaller than the old index page.
    assert len(response.text) > len(old_index_page.text)

    assert temp_name in response.text


def test_remove_group() -> None:
    """Test if we can remove a group."""
    # Get the old index page.
    old_index_page: Response = client.get("/", timeout=5)

    # Add a group to remove.
    client.post(
        "/add",
        data={
            "uuid": random_uuid,
            "name": temp_name,
            "url": "https://twitter.com/elonmusk",
            "usernames": "elonmusk",
        },
    )

    # Remove the group.
    response: Response = client.post(
        "/remove_group",
        data={
            "name": temp_name,
            "uuid": random_uuid,
        },
    )

    # Check that the page loaded successfully.
    assert response.status_code == 200  # noqa: PLR2004

    # Check that the page is not empty.
    assert response.text

    # Check that the index page is smaller than the old index page.
    assert len(response.text) < len(old_index_page.text)

    assert temp_name not in response.text
