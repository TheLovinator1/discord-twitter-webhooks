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
        text: Text from the tweet

    Returns:
        Text with the Discord link previews removed
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

    Before: https://store.steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter

    After: https://store.steampowered.com/app/457140/Oxygen_Not_Included/

    Args:
        text: Text from the tweet

    Returns:
        str: Text with the utm_source parameter removed
    """  # noqa: E501, pylint: disable=line-too-long
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
        text: Text from the tweet

    Returns:
        str: Text with the copyright symbols removed
    """
    settings.logger.debug(f"Text before: {text}")

    symbols = ["®", "™", "©"]
    for symbol in symbols:
        text = text.replace(symbol, "")

    settings.logger.debug(f"Text after copyright symbols: {text}")
    return text


def remove_media_links(entities, text: str) -> str:
    """Twitter appends a link to the media. It it not needed in Discord
    so we remove it.


    Args:
        entities (_type_): Object with the entities from the tweet
        text: Text from the tweet

    Returns:
        str: Text with the media links removed
    """
    for url in entities["urls"]:
        if "status" not in url:
            # This removed every link in this tweet:
            # https://twitter.com/SteamDB/status/1528783609833865217
            # So we check if the url is from twitter.com now
            if url["expanded_url"].startswith("https://twitter.com/"):
                settings.logger.debug(f"Removing url: {url}")
                text = text.replace(url["url"], "")
            else:
                settings.logger.warning(f"Found URL without status: {url}")
    return text
