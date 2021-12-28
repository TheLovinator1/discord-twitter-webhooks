import re


def change_reddit_username_to_link(text: str) -> str:
    """Change /u/username to clickable link.

    Before: /u/username
    After: [u/username](https://www.reddit.com/u/username/)

    Args:
        text (str): Text from the tweet
    Returns:
        str: Text with the username replaced with a clickable link
    """
    # Change /u/user to clickable link
    return re.sub(
        r"(/u/|/user/)([^\s^\/]*)(/|)",
        r"[/u/\g<2>](https://reddit.com/u/\g<2>)",
        text,
        flags=re.MULTILINE,
    )
