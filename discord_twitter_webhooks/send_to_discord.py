from typing import TYPE_CHECKING

from loguru import logger
from reader import Entry, Reader

from discord_twitter_webhooks.get_settings import get_settings
from discord_twitter_webhooks.send_embed import send_embed
from discord_twitter_webhooks.send_link import send_link
from discord_twitter_webhooks.send_text import send_text

if TYPE_CHECKING:
    from discord_twitter_webhooks.dataclasses import Settings


def send_tag(entry: Entry, tag_name: str, reader: Reader) -> None:
    """Send an entry to Discord.

    Args:
        entry: The entry to send.
        tag_name: The tag to send the entry to.
        reader: The reader to use to get the tags.
    """
    # Get the settings for the tag.
    settings: Settings = get_settings(reader=reader, tag_name=tag_name)

    if settings.send_only_link:
        send_link(entry=entry, settings=settings)
    elif settings.send_text:
        send_text(entry=entry, settings=settings)
    elif settings.send_embed:
        send_embed(entry=entry, settings=settings)
    else:
        logger.warning(f"Unknown settings for tag {tag_name}.")


def send_to_discord(reader: Reader) -> None:
    """Send all new entries to Discord.

    This is called by the scheduler every 5 minutes. It will check for new entries and send them to Discord.

    Args:
        reader: The reader which contains the entries.
        feed: The feed to send the entries from.
    """
    # Check for new entries.
    reader.update_feeds()

    # Loop through the unread entries.
    entries = list(reader.get_entries(read=False))

    if not entries:
        logger.info("No new entries found.")
        return

    # Loop through all the unread entries.
    # Unread entries are new entries that we haven't sent to Discord yet.
    for entry in entries:
        # Set the webhook to read, so we don't send it again.
        # If an error occurs, we will mark it as unread so we can try again later.
        reader.set_entry_read(entry, True)

        # Loop through the global tags so we can get the name tags.
        global_tags = list(reader.get_tags(entry.feed))
        for global_tag in global_tags:
            # Check if the tag is a name tag.
            # For example: ('name', 'Games')
            global_tag_name: str = global_tag[0]
            if global_tag_name == "name":
                tag_names: str = str(global_tag[1])
                # Group names can be separated by a semicolon.
                for tag in tag_names.split(";"):
                    # Send the tag and entry to another function where we will decide what to do with it.
                    send_tag(entry, tag, reader)
                    # Send the tag and entry to another function where we will decide what to do with it.
                    send_tag(entry, tag, reader)
                    send_tag(entry, tag, reader)
