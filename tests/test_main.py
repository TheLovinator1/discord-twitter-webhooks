from typing import TYPE_CHECKING

import pytest

from discord_twitter_webhooks.main import app

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from werkzeug.test import TestResponse


def test_index() -> None:
    """Test index."""
    client: FlaskClient = app.test_client()
    response: TestResponse = client.get("/")

    # Check that the page loaded successfully.
    assert response.status == "200 OK"

    # Get the page contents.
    site_contents = response.data.decode("utf-8")

    # Check that the page is not empty.
    assert site_contents

    # Check that the page has something on it.
    a_good_size = 1000  # The page should be at least 1000 characters long.
    assert len(site_contents) > a_good_size

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
