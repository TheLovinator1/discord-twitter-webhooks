"""Functions for Reddit specific stuff

username_to_link: Change /u/username to clickable link.
subreddit_to_link: Change /r/subreddit to clickable link.
"""
import re
import settings


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
    regex = re.sub(
        r"(\B/u/|^/u/)([^\s^/]*)/?",
        r"[/u/\g<2>](https://reddit.com/u/\g<2>)",
        text,
        flags=re.MULTILINE,
    )
    settings.logger.debug(f"username_to_link() - Text before: {text}")
    settings.logger.debug(f"username_to_link() - Text after: {regex}")
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
    regex = re.sub(
        r"(\B/r/|^/r/)([^\s^/]*)/?",
        r"[/r/\g<2>](https://reddit.com/r/\g<2>)",
        text,
        flags=re.MULTILINE,
    )
    settings.logger.debug(f"subreddit_to_link() - Text before: {text}")
    settings.logger.debug(f"subreddit_to_link() - Text after: {regex}")
    return regex
