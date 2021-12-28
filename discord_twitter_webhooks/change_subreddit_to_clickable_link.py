import re

from discord_twitter_webhooks.settings import logger


def change_subreddit_to_clickable_link(text: str) -> str:
    """Change /r/subreddit to clickable link.

    Before: /r/sweden
    After: [r/sweden](https://www.reddit.com/r/sweden/)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the subreddit replaced with a clickable link
    """
    logger.debug(f"change_subreddit_to_clickable_link: text={text}")
    new_text = re.sub(
        r"(/r/)([^\s^\/]*)(/|)",
        r"[/r/\g<2>](https://reddit.com/r/\g<2>)",
        text,
        flags=re.MULTILINE,
    )
    logger.debug(f"change_subreddit_to_clickable_link: new_text={new_text}")
    return new_text
