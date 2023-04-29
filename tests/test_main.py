from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from discord_twitter_webhooks.main import app

if TYPE_CHECKING:
    from httpx import Response


client = TestClient(app)
temp_name: str = f"Test_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"


def test_index_page() -> None:
    """Test that the index page loads."""
    response: Response = client.get("/")

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
        assert "Add a new feed" in response.text
    except AssertionError:
        assert "remove_group" in response.text
    except Exception as err:  # noqa: BLE001
        pytest.fail(f"Unexpected error: {err}")


def test_add_page() -> None:
    """Test that the add page loads."""
    response: Response = client.get("/add")

    # Check that the page loaded successfully.
    assert response.status_code == 200  # noqa: PLR2004

    # Check that the page is not empty.
    assert response.text

    # Check that the page has something on it.
    assert len(response.text) > 1000  # noqa: PLR2004

    # Check that the page contains our HTML and not some other HTML.
    assert "p-2 mb-4 border border-dark" in response.text

    # Check that the page contains the add feed button.
    assert '<button class="btn btn-dark btn-sm">Add feed</button>' in response.text


def test_add_new_group() -> None:
    """Test if we can add a new group."""
    response: Response = client.post(
        "/add",
        data={
            "name": temp_name,
            "webhooks": "https://twitter.com/elonmusk",
            "usernames": "elonmusk",
            "include_retweets": True,
            "include_replies": True,
        },  # type: ignore  # noqa: PGH003
    )

    # Check that the page loaded successfully.
    assert response.status_code == 200  # noqa: PLR2004

    # Check that the page is not empty.
    assert response.text

    # Check that the page has something on it.
    assert len(response.text) > 100  # noqa: PLR2004

    # Check that it starts with the correct text.
    assert response.text.startswith(f"\"Added '{temp_name}' to the existing feed for 'elonmusk'. Before it was")


def test_remove_group() -> None:
    """Test if we can remove a group."""
    # Add a group to remove.
    client.post(
        "/add",
        data={
            "name": temp_name,
            "url": "https://twitter.com/elonmusk",
            "usernames": "elonmusk",
            "include_retweets": True,
            "include_replies": True,
        },  # type: ignore  # noqa: PGH003
    )

    # Remove the group.
    response: Response = client.post(
        "/remove_group",
        data={
            "name": temp_name,
        },  # type: ignore  # noqa: PGH003
    )

    # Check that the page loaded successfully.
    assert response.status_code == 200  # noqa: PLR2004

    # Check that the page is not empty.
    assert response.text

    # Check that it starts with the correct text.
    assert response.text == '"OK"'
