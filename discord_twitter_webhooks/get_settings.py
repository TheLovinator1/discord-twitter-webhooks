from loguru import logger
from reader import Reader

from discord_twitter_webhooks.dataclasses import Settings


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
        if global_tag_name == f"{tag_name}_usernames":
            settings.usernames = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_include_replies":
            settings.include_replies = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_include_retweets":
            settings.include_retweets = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_webhooks":
            settings.webhooks = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_append_usernames":
            settings.append_usernames = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_blacklist":
            settings.blacklist = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_blacklist_active":
            settings.blacklist_active = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_whitelist":
            settings.whitelist = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_whitelist_active":
            settings.whitelist_active = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_author_icon_url":
            settings.embed_author_icon_url = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_author_name":
            settings.embed_author_name = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_author_url":
            settings.embed_author_url = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_color":
            settings.embed_color = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_color_random":
            settings.embed_color_random = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_footer_icon_url":
            settings.embed_footer_icon_url = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_footer_text":
            settings.embed_footer_text = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_image":
            settings.embed_image = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_show_author":
            settings.embed_show_author = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_show_title":
            settings.embed_show_title = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_timestamp":
            settings.embed_timestamp = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_embed_url":
            settings.embed_url = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_hashtag_destination":
            settings.hashtag_destination = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_make_text_a_link":
            settings.make_text_a_link = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_make_text_a_link_preview":
            settings.make_text_a_link_preview = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_make_text_a_link_url":
            settings.make_text_a_link_url = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_remove_copyright":
            settings.remove_copyright = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_remove_utm":
            settings.remove_utm = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_send_embed":
            settings.send_embed = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_send_only_link":
            settings.send_only_link = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_send_only_link_preview":
            settings.send_only_link_preview = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_send_text":
            settings.send_text = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_translate":
            settings.translate = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_translate_from":
            settings.translate_from = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_translate_to":
            settings.translate_to = str(global_tag[1])
        elif global_tag_name == f"{tag_name}_unescape_html":
            settings.unescape_html = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_upload_media":
            settings.upload_media = bool(global_tag[1])
        elif global_tag_name == f"{tag_name}_username_destination":
            settings.username_destination = str(global_tag[1])
        elif global_tag_name.startswith(f"{tag_name}_"):
            # We don't know what this is.
            logger.error(f"Unknown global tag '{global_tag_name}' for tag '{tag_name}'.")
    return settings
