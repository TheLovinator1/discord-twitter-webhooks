from loguru import logger
from reader import Entry, Reader

from discord_twitter_webhooks.dataclasses import Settings
from discord_twitter_webhooks.send_embed import send_embed
from discord_twitter_webhooks.send_link import send_link
from discord_twitter_webhooks.send_text import send_text


def get_settings(reader: Reader, tag_name: str) -> Settings:  # noqa: C901, PLR0912, PLR0915
    """Get the settings for a tag.

    Args:
        reader: The reader to use.
        tag_name: The name of the tag.

    Returns:
        Settings: The settings.
    """
    settings = Settings()

    # Get our settings, they are stored as global tags.
    global_tags = list(reader.get_tags(()))
    for global_tag in global_tags:
        global_tag_name: str = global_tag[0]
        if global_tag_name == f"{tag_name}_include_replies":
            settings.include_replies = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_include_retweets":
            settings.include_retweets = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_webhook":
            settings.webhooks = str(global_tag[1])
        if global_tag_name == f"{tag_name}_append_usernames":
            settings.append_usernames = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_blacklist":
            settings.blacklist_active = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_blacklist_active":
            settings.blacklist_active = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_whitelist":
            settings.whitelist = str(global_tag[1])
        if global_tag_name == f"{tag_name}_whitelist_active":
            settings.whitelist_active = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_author_icon_url":
            settings.embed_author_icon_url = str(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_author_name":
            settings.embed_author_name = str(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_author_url":
            settings.embed_author_url = str(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_color":
            settings.embed_color = str(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_color_random":
            settings.embed_color_random = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_footer_icon_url":
            settings.embed_footer_icon_url = str(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_footer_text":
            settings.embed_footer_text = str(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_image":
            settings.embed_image = str(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_show_author":
            settings.embed_show_author = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_show_title":
            settings.embed_show_title = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_timestamp":
            settings.embed_timestamp = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_embed_url":
            settings.embed_url = str(global_tag[1])
        if global_tag_name == f"{tag_name}_hashtag_link_destination":
            settings.hashtag_link_destination = str(global_tag[1])
        if global_tag_name == f"{tag_name}_make_text_a_link":
            settings.make_text_a_link = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_make_text_a_link_preview":
            settings.make_text_a_link_preview = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_make_text_a_link_url":
            settings.make_text_a_link_url = str(global_tag[1])
        if global_tag_name == f"{tag_name}_remove_copyright":
            settings.remove_copyright = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_remove_utm":
            settings.remove_utm = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_send_embed":
            settings.send_embed = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_send_only_link":
            settings.send_only_link = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_send_only_link_preview":
            settings.send_only_link_preview = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_send_text":
            settings.send_text = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_translate":
            settings.translate = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_translate_from":
            settings.translate_from = str(global_tag[1])
        if global_tag_name == f"{tag_name}_translate_to":
            settings.translate_to = str(global_tag[1])
        if global_tag_name == f"{tag_name}_unescape_html":
            settings.unescape_html = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_upload_media":
            settings.upload_media = bool(global_tag[1])
        if global_tag_name == f"{tag_name}_username_link_destination":
            settings.username_link_destination = str(global_tag[1])

    return settings


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
