import re

from discord_twitter_webhooks.settings import logger


def replace_username_with_link(text: str) -> str:
    """Replace @username with link to their twitter profile.

    Before: @TheLovinator1
    After: [@TheLovinator1](https://twitter.com/TheLovinator1)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the username replaced with a link
    """
    logger.debug(f"replace_username_with_link: text={text}")
    new_text = re.sub(
        r"\B@(\w*)",
        r"[\g<0>](https://twitter.com/\g<1>)",
        text,
        flags=re.MULTILINE,
    )
    logger.debug(f"replace_username_with_link: new_text={new_text}")
    return new_text
