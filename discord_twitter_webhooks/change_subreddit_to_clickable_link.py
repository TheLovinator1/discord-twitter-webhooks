import re


def change_subreddit_to_clickable_link(text: str) -> str:
    """Change /r/subreddit to clickable link.

    Before: /r/sweden
    After: [r/sweden](https://www.reddit.com/r/sweden/)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the subreddit replaced with a clickable link
    """
    # Change /r/subreddit to clickable link
    return re.sub(
        r"(/r/)([^\s^\/]*)(/|)",
        r"[/r/\g<2>](https://reddit.com/r/\g<2>)",
        text,
        flags=re.MULTILINE,
    )
