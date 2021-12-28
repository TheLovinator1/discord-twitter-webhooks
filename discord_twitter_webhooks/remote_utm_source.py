import re

from discord_twitter_webhooks.settings import logger


def remove_utm_source(text: str) -> str:
    """Remove the utm_source parameter from the url.

    Before: https://store.steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter # noqa
    After: https://store.steampowered.com/app/457140/Oxygen_Not_Included/

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the utm_source parameter removed
    """
    logger.debug(f"remove_utm_source: text={text}")
    new_text = re.sub(
        r"(\?utm_source)\S*",
        r"",
        text,
        flags=re.MULTILINE,
    )
    logger.debug(f"remove_utm_source: new_text={new_text}")
    return new_text
