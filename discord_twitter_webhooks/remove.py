import re

from discord_twitter_webhooks import settings


def discord_link_previews(text: str) -> str:
    """Remove the Discord link previews.

    We do this because Discord will add link previews after the message.
    This takes up too much space. We do this by appending a <> before
    and after the link.

    Before: https://www.example.com/
    After: <https://www.example.com/>

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the Discord link previews removed
    """
    regex = re.sub(
        r"(^(https:|http:|www\.)\S*)",
        r"<\g<1>>",
        text,
    )

    settings.logger.debug(f"Text before username_to_link: {text}")
    settings.logger.debug(f"Text after username_to_link: {regex}")
    return regex


def utm_source(text: str) -> str:
    """Remove the utm_source parameter from the url.

    Before:
    https://store.steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter

    After: https://store.steampowered.com/app/457140/Oxygen_Not_Included/

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the utm_source parameter removed
    """
    regex = re.sub(
        r"(\?utm_source)\S*",
        r"",
        text,
    )

    settings.logger.debug(f"Text before username_to_link: {text}")
    settings.logger.debug(f"Text after username_to_link: {regex}")
    return regex


def copyright_symbols(text: str) -> str:
    """Remove ®, ™ and © symbols.

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the copyright symbols removed
    """
    settings.logger.debug(f"Text before: {text}")

    text = text.replace("®", "")
    settings.logger.debug(f"Text after removed ®: {text}")

    text = text.replace("™", "")
    settings.logger.debug(f"Text after removed ™: {text}")

    text = text.replace("©", "")
    settings.logger.debug(f"Text after removed ©: {text}")

    return text
