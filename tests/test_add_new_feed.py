from pathlib import Path

from reader import Reader, make_reader

from discord_twitter_webhooks.add_new_feed import create_group


def test_add_new_feed(tmp_path: str) -> None:
    """Test add_new_feed."""
    db_path = Path(tmp_path, "test.db")
    reader: Reader = make_reader(str(db_path))

    new_feed: str = create_group(
        name="test",
        webhook_value="https://twitter.com/elonmusk",
        usernames_value="elonmusk",
        include_retweets=True,
        include_replies=True,
        reader=reader,
    )
    assert new_feed
    assert (
        new_feed
        == "Added new group 'test' with usernames 'elonmusk'.\n\nWebhook: 'https://twitter.com/elonmusk'\nInclude"
        " retweets: 'True'\nInclude replies: 'True'"
    )
