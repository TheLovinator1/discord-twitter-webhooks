import re

from discord_twitter_webhooks.settings import logger


def change_reddit_username_to_link(text: str) -> str:
    """Change /u/username to clickable link.

    Before: /u/username
    After: [u/username](https://www.reddit.com/u/username/)

    Args:
        text (str): Text from the tweet
    Returns:
        str: Text with the username replaced with a clickable link
    """
    logger.debug(f"change_reddit_username_to_link: text={text}")
    new_text = re.sub(
        r"(/u/|/user/)([^\s^\/]*)(/|)",
        r"[/u/\g<2>](https://reddit.com/u/\g<2>)",
        text,
        flags=re.MULTILINE,
    )

    logger.debug(f"change_reddit_username_to_link: new_text={new_text}")
    return new_text
