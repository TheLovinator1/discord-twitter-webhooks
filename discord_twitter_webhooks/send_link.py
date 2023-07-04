from loguru import logger
from reader import Entry

from discord_twitter_webhooks._dataclasses import Group


def send_link(entry: Entry, group: Group) -> None:
    """Send a link to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    logger.debug(f"Sending {entry.title} as a link to {group.webhooks}")
