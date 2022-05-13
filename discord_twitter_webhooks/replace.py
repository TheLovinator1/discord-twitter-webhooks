import contextlib
import re

from discord_twitter_webhooks import settings


def username_with_link(text: str) -> str:
    """Replace @username with link to their twitter profile.

    Before: @TheLovinator1
    After: [@TheLovinator1](https://twitter.com/TheLovinator1)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the username replaced with a link
    """
    regex = re.sub(
        r"\B@(\w*)",
        r"[\g<0>](https://twitter.com/\g<1>)",
        text,
    )

    settings.logger.debug(f"Text before username_with_link: {text}")
    settings.logger.debug(f"Text after username_with_link: {regex}")
    return regex


def tco_url_link_with_real_link(tweet, text: str) -> str:
    """Replace the t.co url with the real url so users know where the
    link goes to.

    Before: https://t.co/1YC2hc8iUq
    After: https://www.youtube.com/

    Args:
        tweet ([type]): Tweet object
        text (str): Text from the tweet

    Returns:
        str: Text with the t.co url replaced with the real url
    """
    try:
        # Tweet is more than 140 characters
        for url in tweet.extended_tweet["entities"]["urls"]:
            settings.logger.debug(f"tco_url_link_with_real_link - Extended tweet - url: {url}")  # noqa: E501, pylint: disable=line-too-long
            text = text.replace(url["url"], url["expanded_url"])
            settings.logger.debug(f"tco_url_link_with_real_link - Extended tweet - text: {text}")  # noqa: E501, pylint: disable=line-too-long
    except AttributeError:
        # Tweet is less than 140 characters
        with contextlib.suppress(AttributeError):
            for url in tweet.entities["urls"]:
                settings.logger.debug(
                    f"tco_url_link_with_real_link - url: {url}",
                )
                text = text.replace(url["url"], url["expanded_url"])
                settings.logger.debug(
                    f"tco_url_link_with_real_link - text: {text}",
                )
    return text


def hashtag_with_link(text: str) -> str:
    """Replace hashtag with link to Twitter search.

    Before: #Hello
    After: [#Hello](https://twitter.com/hashtag/Hello)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the hashtag replaced with a link
    """
    regex = re.sub(
        r"\B#(\w*)",
        r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
        text,
    )

    settings.logger.debug(f"Text before hashtag_with_link: {text}")
    settings.logger.debug(f"Text after hashtag_with_link: {regex}")
    return regex
