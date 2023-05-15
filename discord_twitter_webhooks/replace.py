import re

from loguru import logger


def username_with_link(text: str) -> str:
    """Replace @username with a link to their Twitter profile.

    Before: @TheLovinator1

    After: [@TheLovinator1](https://twitter.com/TheLovinator1)

    Args:
        text: Text from the tweet

    Returns:
        Text with the username replaced with a link
    """
    regex: str = re.sub(
        r"(@(\w){1,15}\b)",
        r"[\g<1>](https://twitter.com/\g<2>)",
        text,
    )

    logger.debug("Text before: {}", text)
    logger.debug("Text after: {}", regex)
    return regex


def tco_url_link_with_real_link(entities: dict, text: str) -> str:
    """Replace the t.co url with the real url so users know where the link goes to.

    Before: https://t.co/1YC2hc8iUq

    After: https://www.youtube.com/

    Args:
        entities: Entities from the tweet.
        text: Text from the tweet.

    Returns:
        Text with the t.co link replaced with the real link.
    """
    replaced_text: str = text
    if "urls" in entities:
        for url in entities["urls"]:
            old_url: str = url["url"]
            new_url: str = url["expanded_url"]

            # Remove trailing slash
            new_url = new_url.rstrip("/")

            # Replace the old URL with the new URL.
            replaced_text: str = text.replace(old_url, new_url)

    logger.debug("Replaced text: {}", replaced_text)
    return replaced_text


def hashtag_with_link(text: str) -> str:
    """Replace the hashtag with a link to Twitter search.

    Before: #Hello

    After: [#Hello](https://twitter.com/hashtag/Hello)

    Args:
        text: Text from the tweet

    Returns:
        Text with the hashtag replaced with a link
    """
    regex: str = re.sub(
        r"(#(\w*))",
        r"[\g<1>](https://twitter.com/hashtag/\g<2>)",
        text,
    )

    logger.debug("Text before: {}", text)
    logger.debug("Text after: {}", regex)
    return regex
