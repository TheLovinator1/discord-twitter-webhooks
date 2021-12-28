import re

from discord_twitter_webhooks.settings import logger


def remove_discord_link_previews(text: str) -> str:
    """Remove the discord link previews.

    We do this because Discord will add link previews after the message.
    This takes up too much space. We do this by appending a <> before and after the link.

    Before: https://www.example.com/
    After: <https://www.example.com/>

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the discord link previews removed
    """
    logger.debug(f"remove_discord_link_previews: text={text}")
    new_text = re.sub(
        r"(https://\S*)\)",
        r"<\g<1>>)",
        text,
        flags=re.MULTILINE,
    )
    logger.debug(f"remove_discord_link_previews: new_text={new_text}")
    return new_text
