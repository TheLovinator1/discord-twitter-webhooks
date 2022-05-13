import re

from discord_twitter_webhooks import settings


def username_to_link(text: str) -> str:
    """Change /u/username to clickable link.

    Before: /u/username
    After: [u/username](https://www.reddit.com/u/username/)

    Args:
        text (str): Text from the tweet
    Returns:
        str: Text with the username replaced with a clickable link
    """
    regex = re.sub(
        r"(\B/u/|^/u/)([^\s^/]*)/?",
        r"[/u/\g<2>](https://reddit.com/u/\g<2>)",
        text,
        flags=re.MULTILINE,
    )
    settings.logger.debug(f"Text before username_to_link: {text}")
    settings.logger.debug(f"Text after username_to_link: {regex}")
    return regex


def subreddit_to_link(text: str) -> str:
    """Change /r/subreddit to clickable link.

    Before: /r/sweden
    After: [r/sweden](https://www.reddit.com/r/sweden/)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the subreddit replaced with a clickable link
    """
    regex = re.sub(
        r"(\B/r/|^/r/)([^\s^/]*)/?",
        r"[/r/\g<2>](https://reddit.com/r/\g<2>)",
        text,
        flags=re.MULTILINE,
    )
    settings.logger.debug(f"Text before subreddit_to_link: {text}")
    settings.logger.debug(f"Text after subreddit_to_link: {regex}")
    return regex
