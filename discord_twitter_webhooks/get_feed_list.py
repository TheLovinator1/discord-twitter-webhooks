from dataclasses import dataclass

from loguru import logger
from reader import Feed, Reader


@dataclass
class FeedList:
    """A feed."""

    name: str
    feeds: list[Feed] | None = None
    webhook: str | None = None
    include_retweets: bool | None = None
    include_replies: bool | None = None


def add_feeds_to_list_item(reader: Reader, list_item: FeedList, feed_list: list[FeedList], name: str) -> None:
    """Add feeds to a list item.

    Args:
        reader: The reader to use.
        list_item: The list item to add feeds to.
        feed_list: The feed list.
        name: The name of the list item.
    """
    feeds_to_add: list[Feed] = []
    for _feed in reader.get_feeds():
        tags = dict(reader.get_tags(_feed))
        split_name: list[str] = str(tags["name"]).split(";")
        feeds_to_add.extend(_feed for _split_name in split_name if _split_name == name)

    list_item.feeds = feeds_to_add

    # Only add if not already in the list
    if list_item not in feed_list:
        feed_list.append(list_item)


def create_list_item(reader: Reader, name: str) -> FeedList:
    """Create a list item. This is used in the feed list in the index page.

    Each group of feeds has settings, these are stored as global
    tags (https://reader.readthedocs.io/en/latest/guide.html#resource-tags)

    Current settings are:
    - webhook
       - The webhook to send the tweet to
    - include_retweets
       - Whether or not to send retweets to the webhook
    - include_replies
       - Whether or not to send replies to the webhook
    Args:
        reader: The reader to use.
        name: The name of the list item.

    Returns:
        FeedList: The list item.
    """
    list_item = FeedList(name=name)
    global_tags = list(reader.get_tags(()))
    for global_tag in global_tags:
        if global_tag[0] == f"{name}_webhook":
            list_item.webhook = str(global_tag[1])
        elif global_tag[0] == f"{name}_include_retweets":
            list_item.include_retweets = bool(global_tag[1])
        elif global_tag[0] == f"{name}_include_replies":
            list_item.include_replies = bool(global_tag[1])
        else:
            continue
    return list_item


def get_feed_list(reader: Reader) -> list[FeedList]:
    """Get the feed list.

    Args:
        reader: The reader to use.


    Returns:
            list[FeedList]: The feed list.
    """
    if reader is None:
        return []

    feed_list: list[FeedList] = []
    for feed in reader.get_feeds():
        tags = dict(reader.get_tags(feed))
        if tags["name"]:
            # Split the name by semicolon, we do this because we can have several groups of feeds with the same RSS feed
            name: str = str(tags["name"])

            name_list: list[str] | None = None
            if ";" in name:
                name_list = name.split(";")

            if name is None:
                logger.error("Name is None for feed {}", feed)
                continue

            if name_list:
                for _name in name_list:
                    list_item: FeedList = create_list_item(reader, _name)
                    add_feeds_to_list_item(reader=reader, list_item=list_item, feed_list=feed_list, name=_name)
            else:
                list_item: FeedList = create_list_item(reader, name)
                add_feeds_to_list_item(reader=reader, list_item=list_item, feed_list=feed_list, name=name)

    return feed_list
