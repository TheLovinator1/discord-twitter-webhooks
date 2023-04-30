from loguru import logger
from reader import Entry

from discord_twitter_webhooks.dataclasses import Settings


def send_link(entry: Entry, settings: Settings) -> None:
    """Send a link to Discord.

    Args:
        entry: The entry to send.
        settings: The settings to use.
        reader: The reader to use.
    """
    logger.debug(f"Sending {entry.title} as a link to {settings.webhooks}")
