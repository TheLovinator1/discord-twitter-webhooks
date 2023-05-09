from loguru import logger
from reader import Entry

from discord_twitter_webhooks.dataclasses import Settings


def send_text(entry: Entry, settings: Settings) -> None:
    """Send text to Discord.

    Args:
        entry: The entry to send.
        settings: The settings to use.
        reader: The reader to use.
    """
    logger.debug(f"Sending {entry.title} to {settings.webhooks}")