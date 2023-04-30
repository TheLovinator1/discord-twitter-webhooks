import re

from loguru import logger

from discord_twitter_webhooks.dataclasses import Settings


def replace_hashtags(text: str, settings: Settings) -> str:
    """Replace the hashtag with a link to Twitter search.

    Before: #Hello

    After: [#Hello](https://twitter.com/hashtag/Hello)

    Args:
        text: Text from the tweet
        settings: The settings to use

    Returns:
        Text with the hashtag replaced with a link
    """
    if settings.hashtag_link_destination == "Nitter":
        hashtag_domain: str = "https://nitter.net/hashtag/"
    elif settings.hashtag_link_destination == "Twitter":
        hashtag_domain: str = "https://twitter.com/hashtag/"
    else:
        logger.error(
            "Invalid hashtag link destination {}. Using default destination.",
            settings.hashtag_link_destination,
        )
        hashtag_domain: str = "https://twitter.com/hashtag/"

    regex: str = re.sub(
        r" (#(\w*))",
        rf" [\g<1>]({hashtag_domain}\g<2>)",
        text,
    )
    return regex
