import re

from loguru import logger


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
    regex: str = re.sub(
        r"(^(https:|http:|www\.)\S*)",
        r"<\g<1>>",
        text,
    )

    logger.debug("Text before: {}", text)
    logger.debug("Text after: {}", regex)
    return regex


def utm_source(text: str) -> str:
    """Remove the utm_source parameter from the url.

    Before: steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter

    After: steampowered.com/app/457140/Oxygen_Not_Included/

    Args:
        text: Text from the tweet

    Returns:
        Text with the utm_source parameter removed
    """
    regex: str = re.sub(
        r"(\?utm_source)\S*",
        r"",
        text,
    )

    logger.debug("Text before {}", text)
    logger.debug("Text after: {}", regex)
    return regex


def copyright_symbols(text: str) -> str:
    """Remove ®, ™ and © symbols.

    Args:
        text: Text from the tweet

    Returns:
        Text with the copyright symbols removed
    """
    logger.debug("Text before: {}", text)

    symbols: list[str] = ["®", "™", "©"]
    replaced_text: str = text
    for symbol in symbols:
        replaced_text: str = replaced_text.replace(symbol, "")

    logger.debug("Text after: {}", replaced_text)
    return replaced_text


def remove_media_links(entities: dict, text: str) -> str:
    """Twitter appends a link to the media. It is not needed in Discord, so we remove it.

    Args:
        entities: Object with the entities from the tweet
        text: Text from the tweet.

    Returns:
        Text with the media links removed
    """
    replaced_text: str = text
    for url in entities["urls"]:
        if "status" not in url:
            # This removed every link in this tweet:
            # https://twitter.com/SteamDB/status/1528783609833865217
            # Because of that we check if the url is from the twitter.com domain.
            if url["expanded_url"].startswith("https://twitter.com/"):
                logger.debug("Removing url: {}", url)
                replaced_text: str = replaced_text.replace(url["url"], "")
            else:
                logger.warning("Found URL without status: {}", url)
    return replaced_text
