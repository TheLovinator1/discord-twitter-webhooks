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
    return re.sub(
        r"(\B|^)(/u/|u/)([^\s^/]*)/?",
        r"[/u/\g<3>](https://reddit.com/u/\g<3>)",
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
    return re.sub(
        r"(\B|^)(/r/|r/)([^\s^/]*)/?",
        r"[/r/\g<3>](https://reddit.com/r/\g<3>)",
        text,
        flags=re.MULTILINE,
    )
