from loguru import logger
from reader import Entry, Reader

from discord_twitter_webhooks._dataclasses import Group
from discord_twitter_webhooks.send_embed import send_embed
from discord_twitter_webhooks.send_link import send_link
from discord_twitter_webhooks.send_text import send_text


def send_tag(entry: Entry, group: Group) -> None:
    """Send an entry to Discord.

    Args:
        entry: The entry to send.
        group: The group to use to send the entry.
    """
    if group.send_as_link:
        send_link(entry=entry, group=group)
    elif group.send_as_text:
        send_text(entry=entry, group=group)
    elif group.send_as_embed:
        send_embed(entry=entry, group=group)
    else:
        logger.warning(f"Unknown settings for tag {group.name}.")


def send_to_discord(reader: Reader) -> None:
    """Send all new entries to Discord.

    This is called by the scheduler every 5 minutes. It will check for new entries and send them to Discord.

    Args:
        reader: The reader which contains the entries.
    """
    # TODO: Actually implement this.
    # Check for new entries.
    reader.update_feeds()

    # Loop through the unread entries.
    entries = list(reader.get_entries(read=False))

    if not entries:
        logger.info("No new entries found.")
        return

    logger.info(f"Found {len(entries)} new entries.")
