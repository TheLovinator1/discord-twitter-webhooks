import re

from loguru import logger
from reader import Reader
from reader.exceptions import TagNotFoundError


def remove_group(name: str, reader: Reader) -> None:
    """Remove a group."""
    # Remove the feeds from the group if they are not in any other group.
    for feed in reader.get_feeds():
        tags = dict(reader.get_tags(feed))
        if name in tags["name"]:
            # Remove the group from the feed
            new_name: str = re.sub(rf";?{name}", "", str(tags["name"]))

            # Remove ; if it is the first or last character
            clean_name: str = new_name.removeprefix(";").removesuffix(";")

            # If the name is not empty, set the new name, otherwise delete the feed
            if clean_name:
                reader.set_tag(feed, "name", new_name)  # type: ignore  # noqa: PGH003
                logger.debug(f"Removed group {name} from feed {feed}")
            else:
                reader.delete_tag(feed, "name")
                reader.delete_feed(feed)
                logger.debug(f"Deleted feed {feed}")

            remove_global_tags(name, reader)

            logger.info(f"Removed group {name}")


def remove_global_tags(name: str, reader: Reader) -> None:
    """Remove the global tags for a group.

    Args:
        name: The name of the group.
        reader: The reader to use to remove the tags.
    """
    tags: list[str] = [
        f"{name}_webhooks",
        f"{name}_usernames",
        f"{name}_include_retweets",
        f"{name}_include_replies",
        f"{name}_append_usernames",
        f"{name}_blacklist",
        f"{name}_blacklist_active",
        f"{name}_whitelist",
        f"{name}_whitelist_active",
        f"{name}_embed_author_icon_url",
        f"{name}_embed_author_name",
        f"{name}_embed_author_url",
        f"{name}_embed_color",
        f"{name}_embed_color_random",
        f"{name}_embed_footer_icon_url",
        f"{name}_embed_footer_text",
        f"{name}_embed_image",
        f"{name}_embed_show_author",
        f"{name}_embed_show_title",
        f"{name}_embed_timestamp",
        f"{name}_embed_url",
        f"{name}_hashtag_link_destination",
        f"{name}_make_text_a_link",
        f"{name}_make_text_a_link_preview",
        f"{name}_make_text_a_link_url",
        f"{name}_remove_copyright",
        f"{name}_remove_utm",
        f"{name}_send_embed",
        f"{name}_send_only_link",
        f"{name}_send_only_link_preview",
        f"{name}_send_text",
        f"{name}_translate",
        f"{name}_translate_from",
        f"{name}_translate_to",
        f"{name}_unescape_html",
        f"{name}_upload_media",
        f"{name}_username_link_destination",
    ]

    for tag in tags:
        try:
            reader.delete_tag((), tag)
            logger.debug(f"Deleted tag {tag}")
        except TagNotFoundError:
            logger.error(f"Tag {tag} not found when trying to delete it")
