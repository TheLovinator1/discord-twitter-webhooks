import contextlib
import re


def username_with_link(text: str) -> str:
    """Replace @username with link to their twitter profile.

    Before: @TheLovinator1
    After: [@TheLovinator1](https://twitter.com/TheLovinator1)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the username replaced with a link
    """
    return re.sub(
        r"\B@(\w*)",
        r"[\g<0>](https://twitter.com/\g<1>)",
        text,
    )


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
            text = text.replace(url["url"], url["expanded_url"])

    except AttributeError:
        # Tweet is less than 140 characters
        with contextlib.suppress(AttributeError):
            for url in tweet.entities["urls"]:
                text = text.replace(url["url"], url["expanded_url"])
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
    return re.sub(
        r"\B#(\w*)",
        r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
        text,
    )
