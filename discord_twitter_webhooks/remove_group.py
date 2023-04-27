import re

from loguru import logger
from reader import Reader


def remove_group(name: str, reader: Reader) -> str:
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

            # Remove the group from the global tags
            global_tags = dict(reader.get_tags(()))
            if f"{name}_include_retweets" in global_tags:
                reader.delete_tag((), f"{name}_include_retweets")
                logger.debug(f"Deleted tag {name}_include_retweets")
            if f"{name}_include_replies" in global_tags:
                reader.delete_tag((), f"{name}_include_replies")
                logger.debug(f"Deleted tag {name}_include_replies")
            if f"{name}_webhook" in global_tags:
                reader.delete_tag((), f"{name}_webhook")
                logger.debug(f"Deleted tag {name}_webhook")

            logger.info(f"Removed group {name}")
    return "OK"
