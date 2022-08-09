"""Replace stuff in the tweet text.

username_with_link: Replace @username with a link to their Twitter profile.
tco_url_link_with_real_link: Replace the t.co url with the real url so users know where the
    link goes to.
hashtag_with_link: Replace the hashtag with a link to Twitter search.
"""

import re

from discord_twitter_webhooks import settings


def username_with_link(text: str) -> str:
    """Replace @username with a link to their Twitter profile.

    Before: @TheLovinator1

    After: [@TheLovinator1](https://twitter.com/TheLovinator1)

    Args:
        text: Text from the tweet

    Returns:
        Text with the username replaced with a link
    """
    regex = re.sub(
        r"\B@(\w*)",
        r"[\g<0>](https://twitter.com/\g<1>)",
        text,
    )

    settings.logger.debug(f"username_with_link() - Text before: {text}")
    settings.logger.debug(f"username_with_link() - Text after: {regex}")
    return regex


def tco_url_link_with_real_link(entities: dict, text: str) -> str:
    """Replace the t.co url with the real url so users know where the
    link goes to.

    Before: https://t.co/1YC2hc8iUq

    After: https://www.youtube.com/

    Args:
        entities: Entities from the tweet.
        text: Text from the tweet.

    Returns:
        Text with the t.co link replaced with the real link.
    """
    for url in entities["urls"]:
        text = text.replace(url["url"], url["expanded_url"])

    settings.logger.debug(f"tco_url_link_with_real_link: {text}")
    return text


def hashtag_with_link(text: str) -> str:
    """Replace the hashtag with a link to Twitter search.

    Before: #Hello

    After: [#Hello](https://twitter.com/hashtag/Hello)

    Args:
        text: Text from the tweet

    Returns:
        Text with the hashtag replaced with a link
    """
    regex = re.sub(
        r"\B#(\w*)",
        r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
        text,
    )

    settings.logger.debug(f"hashtag_with_link() - Text before: {text}")
    settings.logger.debug(f"hashtag_with_link() - Text after: {regex}")
    return regex
