import re


def username_to_link(text: str) -> str:
    """Change /u/username to clickable link.

    Before: /u/username
    After: [u/username](https://www.reddit.com/u/username/)

    Args:
        text (str): Text from the tweet
    Returns:
        str: Text with the username replaced with a clickable link
    """
    # TODO: This doesn't work for URLs without https or http
    return re.sub(
        r"((https|http):?//(www\.?)reddit\.com|^)((/|)(user|u)/)([^\s^\/]*)(/|)",
        r"[\g<1>/u/\g<7>](https://reddit.com/u/\g<7>)",
        text,
        flags=re.MULTILINE,
    )


def subreddit_to_link(text: str) -> str:
    """Change /r/subreddit to clickable link.

    Before: /r/sweden
    After: [r/sweden](https://www.reddit.com/r/sweden/)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the subreddit replaced with a clickable link
    """
    # TODO: This doesn't work for URLs without https or http
    return re.sub(
        r"((https|http):?//(www\.?)reddit\.com|^)(/r|^r)/([^\s^\/]*)(/|)",
        r"[\g<1>/r/\g<5>](https://reddit.com/r/\g<5>)",
        text,
        flags=re.MULTILINE,
    )
