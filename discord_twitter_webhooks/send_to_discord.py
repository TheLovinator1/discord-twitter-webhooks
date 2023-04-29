from dataclasses import dataclass

from loguru import logger
from reader import Entry, Reader


@dataclass
class Settings:
    """A feed."""

    webhook: str | None = None
    include_retweets: bool | None = None
    include_replies: bool | None = None


def send_text(entry: Entry, settings: Settings, reader: Reader) -> None:
    """Send text to Discord.

    Args:
        entry: The entry to send.
        settings: The settings to use.
        reader: The reader to use.
    """
    logger.debug(f"Sending {entry.title} to {settings.webhook}")


def get_settings(reader: Reader, tag_name: str) -> Settings:
    """Get the settings for a tag.

    Args:
        reader: The reader to use.
        tag_name: The name of the tag.

    Returns:
        Settings: The settings.
    """
    include_replies: bool = False
    include_retweets: bool = False
    webhook_url: str = ""

    # Get our settings. These are global tags.
    global_tags = list(reader.get_tags(()))
    for global_tag in global_tags:
        # If we should send replies.
        if global_tag[0] == f"{tag_name}_include_replies":
            include_replies = bool(global_tag[1])

        # If we should send retweets.
        if global_tag[0] == f"{tag_name}_include_retweets":
            include_retweets = bool(global_tag[1])

        # Get the webhook URL.
        if global_tag[0] == f"{tag_name}_webhook":
            webhook_url = str(global_tag[1])

    logger.info(f"Webhook URL: {webhook_url}")
    logger.info(f"Include Retweets: {include_retweets}")
    logger.info(f"Include Replies: {include_replies}")

    if not include_replies or not include_retweets or not webhook_url:
        return Settings()

    return Settings(webhook=webhook_url, include_replies=include_replies, include_retweets=include_retweets)


def send_tag(entry: Entry, tag_name: str, reader: Reader) -> None:
    """Send an entry to Discord.

    Args:
        entry: The entry to send.
        tag_name: The tag to send the entry to.
        reader: The reader to use to get the tags.
    """
    # Get the settings for the tag.
    settings: Settings = get_settings(reader=reader, tag_name=tag_name)
    send_text(entry=entry, settings=settings, reader=reader)


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
                # Group names can be separated by a semicolon.
                for tag in global_tag_name.split(";"):
                    tag_name: str = tag[1]

                    # Send the tag and entry to another function where we will decide what to do with it.
                    send_tag(entry, tag_name, reader)
