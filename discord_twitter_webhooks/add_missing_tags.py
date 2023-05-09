from loguru import logger
from reader import Reader


def add_tag(name: str, reader: Reader) -> None:
    """Add missing tags to the reader.

    Currently, this adds the following tags if they are missing:
        - {name}_include_retweets
        - {name}_include_replies
        - {name}_webhook

    Args:
        name: The name of the feed to add the tags for.
        reader: The reader where the tags should be added.
    """
    global_tags = dict(reader.get_tags(()))
    if f"{name}_include_retweets" not in global_tags:
        logger.warning(f"You are missing the {name}_include_retweets")
    if f"{name}_include_replies" not in global_tags:
        logger.warning(f"You are missing the {name}_include_replies")
    if f"{name}_webhooks" not in global_tags:
        logger.warning(f"You are missing the tag {name}_webhooks")


def add_missing_tags(reader: Reader) -> None:
    """Add missing tags to the reader.

    Args:
        reader: The reader.
    """
    for feed in reader.get_feeds():
        tags = dict(reader.get_tags(feed))
        if tags["name"]:
            name: str = str(tags["name"])
            names: list[str] | None = None
            if ";" in name:
                names = name.split(";")

            if name is None:
                logger.error("Name is None for feed {} when adding missing tags.", feed)
                continue

            if names:
                for _name in names:
                    add_tag(_name, reader)
