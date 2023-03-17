import re

from discord_twitter_webhooks import settings


def username_to_link(text: str) -> str:
    """Change /u/username to clickable link.

    Before: /u/username
    After: [u/username](https://www.reddit.com/u/username/)

    Args:
        text: Text from the tweet
    Returns:
        Text with the username replaced with a clickable link.
    """
    # TODO: Add comments describing the regex
    regex: str = re.sub(
        r"(\B/u/|^/u/)([^\s^/]*)/?",
        r"[/u/\g<2>](https://reddit.com/u/\g<2>)",
        text,
        flags=re.MULTILINE,
    )
    settings.logger.debug("username_to_link() - Text before: %s", text)
    settings.logger.debug("username_to_link() - Text after: %s", regex)
    return regex


def subreddit_to_link(text: str) -> str:
    """Change /r/subreddit to clickable link.

    Before: /r/sweden

    After: [r/sweden](https://www.reddit.com/r/sweden/)

    Args:
        text: Text from the tweet

    Returns:
        Text with the subreddit replaced with a clickable link
    """
    # TODO: Add comments describing the regex
    regex: str = re.sub(
        r"(\B/r/|^/r/)([^\s^/]*)/?",
        r"[/r/\g<2>](https://reddit.com/r/\g<2>)",
        text,
        flags=re.MULTILINE,
    )
    settings.logger.debug("subreddit_to_link() - Text before: %s", text)
    settings.logger.debug("subreddit_to_link() - Text after: %s", regex)
    return regex
