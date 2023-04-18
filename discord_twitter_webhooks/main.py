from dataclasses import dataclass
from typing import TYPE_CHECKING

from flask import Flask, render_template, request
from loguru import logger
from reader import Reader

from discord_twitter_webhooks.get_include_replies import get_include_replies
from discord_twitter_webhooks.get_include_retweets import get_include_retweets
from discord_twitter_webhooks.settings import get_reader

if TYPE_CHECKING:
    from collections.abc import Iterable

    from reader import Feed

app = Flask(__name__)


@dataclass
class FeedList:
    """A feed."""

    name: str
    feeds: list["Feed"] | None = None
    webhook: str | None = None
    include_retweets: bool | None = None
    include_replies: bool | None = None


def create_list_item(reader: Reader, name: str) -> FeedList:
    """Create a list item. This is used in the feed list in the index page.

    Each group of feeds has settings, these are stored as global tags (https://reader.readthedocs.io/en/latest/guide.html#resource-tags)

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
                logger.error(f"Name is None for feed {feed}")
                continue

            if name_list:
                for _name in name_list:
                    list_item: FeedList = create_list_item(reader, _name)
                    add_feeds_to_list_item(reader=reader, list_item=list_item, feed_list=feed_list, name=_name)
            else:
                list_item: FeedList = create_list_item(reader, name)
                add_feeds_to_list_item(reader=reader, list_item=list_item, feed_list=feed_list, name=name)

    return feed_list


@app.route("/")
def index() -> str:
    reader = get_reader()

    if reader is None:
        return "Failed to initialize reader."

    feed_list: list[FeedList] = get_feed_list(reader)
    return render_template("index.html", feed_list=feed_list) if feed_list else "Failed to initialize reader."


@app.route("/add")
def add() -> str:
    return render_template("add.html")


@app.route("/add", methods=["POST"])
def add_post() -> str:
    """Add a new feed.

    Returns:
        str: The response.
    """
    reader = get_reader()

    if reader is None:
        return "Failed to initialize reader."

    name: str | None = request.form.get("name")
    webhook_value: str | None = request.form.get("url")
    usernames_value: str | None = request.form.get("usernames")
    include_retweets: bool = get_include_retweets(request)
    include_replies: bool = get_include_replies(request)

    # Check if name contains a semicolon
    if name is not None and ";" in name:
        # TODO: Return our previous values
        return (
            f"Error, name cannot contain a semicolon.\n\nPlease go back and try again.\nName: '{name}'\n"
            f"Webhook: '{webhook_value}'\nUsernames: '{usernames_value}'"
        )

    if webhook_value is None or usernames_value is None:
        # TODO: Return our previous values
        return (
            "Error: webhook or usernames was None. Please go back and try again.\n\n"
            f"Webhook: '{webhook_value}'\nUsernames: '{usernames_value}'"
        )

    # Check if the name already exists
    # Get all global tags
    global_tags = reader.get_tags(())
    for global_tag in global_tags:
        # Check if the name is already in use, each global tag starts with the name, followed by an underscore
        if global_tag[0].startswith(f"{name}_"):
            return (
                f"Error, name already exists.\n\nPlease go back and try again.\nName: '{name}'\n"
                f"Webhook: '{webhook_value}'\nUsernames: '{usernames_value}'"
            )

    # Get all usernames and add them to the reader if they don't exist, or add the new name to the existing feed.
    for username in usernames_value.split(" "):
        feed_url: str = f"https://nitter.lovinator.space/{username}/rss"

        # Check if the feed already exists
        feeds: Iterable[Feed] = reader.get_feeds()
        for feed in feeds:
            # Each feed has a name tag, webhooks and include_retweets and include_replies will be added
            # as global tag named "name_webhook", "name_include_retweets" and "name_include_replies
            # For example, if the name is "TheLovinator", the webhook will be "TheLovinator_webhook", the
            # include_retweets will be "TheLovinator_include_retweets" and the include_replies will
            # be "TheLovinator_include_replies"
            if feed.url == feed_url:
                # Get the old name and append the new name to it, this will be used when getting the global tags
                old_name: str | None = str(reader.get_tag(feed, "name"))
                if old_name is None:
                    # TODO: Make this better, we should return a template with a message instead of just a string
                    return (
                        f"Error, failed to get old name when adding new name to it.\n\nFeed URL: '{feed_url}'\nOld"
                        f" name: '{old_name}'\nNew name: '{name}'"
                    )

                # Add the new name to the old name. For example, if the old name is "TheLovinator" and the new name is
                # "TheLovinator2", the new name will be "TheLovinator;TheLovinator2"
                new_name: str = f"{old_name};{name}"

                # Set the names as the tag
                reader.set_tag(feed, "name", new_name)  # type: ignore  # noqa: PGH003

                # Add our new global tags
                reader.set_tag((), f"{name}_webhook", webhook_value)  # type: ignore  # noqa: PGH003
                reader.set_tag((), f"{name}_include_retweets", include_retweets)  # type: ignore  # noqa: PGH003
                reader.set_tag((), f"{name}_include_replies", include_replies)  # type: ignore  # noqa: PGH003

                # TODO: Make this better, we should return a template with a message instead of just a string
                return (
                    f"Added '{name}' to the existing feed for '{username}'. Before it was '{old_name}'. Now it is"
                    f" '{new_name}'."
                )

        # If the feed doesn't exist, add it
        reader.add_feed(feed_url, exist_ok=True)

        feed: Feed = reader.get_feed(feed_url)

        # Add the name as a tag
        reader.set_tag(feed, "name", name)  # type: ignore  # noqa: PGH003

        # Add our new global tags
        reader.set_tag((), f"{name}_webhook", webhook_value)  # type: ignore  # noqa: PGH003
        reader.set_tag((), f"{name}_include_retweets", include_retweets)  # type: ignore  # noqa: PGH003
        reader.set_tag((), f"{name}_include_replies", include_replies)  # type: ignore  # noqa: PGH003

    # TODO: Make this better, we should return a template with a message instead of just a string
    return (
        f"Added new group '{name}' with usernames '{usernames_value}'.\n\nWebhook: '{webhook_value}'\nInclude retweets:"
        f" '{include_retweets}'\nInclude replies: '{include_replies}'"
    )
