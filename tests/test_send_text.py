import os
from pathlib import Path

import pytest
from reader import Entry, Reader, make_reader

from discord_twitter_webhooks.dataclasses import Settings
from discord_twitter_webhooks.send_text import send_text


def test_send_text(tmp_path: Path) -> None:
    """Test send_text()."""
    # Get the webhook URL from the environment.
    webhook_url: str = os.environ.get("WEBHOOK_URL", "")

    # Skip the test if there is no webhook URL.
    if not webhook_url:
        pytest.skip("No webhook URL set.")

    # Make sure we have a webhook URL.
    assert webhook_url

    # Create a temporary reader database and add a feed.
    reader: Reader = make_reader(str(tmp_path / "test.db"))
    reader.add_feed("https://nitter.lovinator.space/elonmusk/rss")

    # Update the feeds.
    reader.update_feeds()

    # Create a Settings object and add our webhook URL to it.
    settings: Settings = Settings(webhooks=webhook_url)
    assert settings.webhooks

    # Loop through all the entries from the RSS feed.
    for entry in reader.get_entries():
        # Make sure we have an Entry.
        assert isinstance(entry, Entry)

        # Send the entry.
        send_text(entry, settings)

        # Only send one entry.
        break
