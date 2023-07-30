import os
from datetime import datetime, timezone

import pytest
from discord_webhook import DiscordWebhook
from reader import Entry

from discord_twitter_webhooks._dataclasses import Group
from discord_twitter_webhooks.send_to_discord import send_text, send_webhook

test_url: str | None = os.environ.get("TEST_WEBHOOK_URL", None)


@pytest.mark.skipif(not test_url, reason="TEST_WEBHOOK_URL not set")
def test_send_webhook() -> None:
    """Test sending a plain webhook to Discord.

    This test requires the environment variable TEST_WEBHOOK_URL to be set.
    """
    if not test_url:
        pytest.skip("TEST_WEBHOOK_URL was not set")

    webhook = DiscordWebhook(url=test_url, content="Testing test_send_webhook")
    entry = Entry(
        id="123456789",
        title="Testing test_send_webhook",
        link="https://twitter.com/Steam/status/123456789",
        summary="<p>Testing test_send_webhook</p>",
        published=datetime.now(timezone.utc),
        updated=datetime.now(timezone.utc),
        author="Steam",
    )
    group = Group(webhooks=[test_url])

    assert send_webhook(webhook=webhook, entry=entry, group=group) == entry.title


@pytest.mark.skipif(not test_url, reason="TEST_WEBHOOK_URL not set")
def test_send_text() -> None:
    """Test sending the tweet as text to Discord.

    This test requires the environment variable TEST_WEBHOOK_URL to be set.
    """
    if not test_url:
        pytest.skip("TEST_WEBHOOK_URL was not set")

    entry = Entry(
        id="123456789",
        title="Testing test_send_text",
        link="https://twitter.com/Steam/status/123456789",
        summary="<p>Testing test_send_text</p>",
        published=datetime.now(timezone.utc),
        updated=datetime.now(timezone.utc),
        author="Steam",
    )
    group = Group(webhooks=[test_url])

    assert (
        send_text(entry=entry, group=group)
        == "[Steam](<https://twitter.com/Steam/status/123456789>) tweeted:\nTesting test_send_text"
    )


@pytest.mark.skipif(not test_url, reason="TEST_WEBHOOK_URL not set")
def test_send_text_without_username() -> None:
    """Test sending the tweet as text to Discord without the username.

    This test requires the environment variable TEST_WEBHOOK_URL to be set.
    """
    if not test_url:
        pytest.skip("TEST_WEBHOOK_URL was not set")

    entry = Entry(
        id="123456789",
        title="Testing test_send_text_without_username",
        link="https://twitter.com/Steam/status/123456789",
        summary="<p>Testing test_send_text_without_username</p>",
        published=datetime.now(timezone.utc),
        updated=datetime.now(timezone.utc),
        author="Steam",
    )
    group = Group(webhooks=[test_url], send_as_text_username=False)

    assert send_text(entry=entry, group=group) == "Testing test_send_text_without_username"
