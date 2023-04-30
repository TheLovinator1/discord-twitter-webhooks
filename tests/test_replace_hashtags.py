from discord_twitter_webhooks.dataclasses import Settings
from discord_twitter_webhooks.replace_hashtags import replace_hashtags


def test_replace_hashtags() -> None:
    """Test replace_hashtags()."""
    settings_nitter = Settings(hashtag_link_destination="Nitter")

    assert replace_hashtags("Hello #world", settings_nitter) == "Hello [#world](https://nitter.net/hashtag/world)"

    settings_twitter = Settings(hashtag_link_destination="Twitter")

    assert replace_hashtags("Hello #world", settings_twitter) == "Hello [#world](https://twitter.com/hashtag/world)"
