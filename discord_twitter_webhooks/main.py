# sourcery skip: avoid-global-variables
import re

from flask import Flask, render_template, request
from loguru import logger
from reader import Reader

from discord_twitter_webhooks.add_new_feed import create_group
from discord_twitter_webhooks.get_feed_list import FeedList, get_feed_list
from discord_twitter_webhooks.include_replies import get_include_replies
from discord_twitter_webhooks.include_retweets import get_include_retweets
from discord_twitter_webhooks.settings import get_reader

app = Flask(__name__)

reader: Reader | None = get_reader()

if not reader:
    msg = "Failed to initialize reader."
    raise RuntimeError(msg)


@app.route("/")
def index() -> str:
    """Return the index page.

    Returns:
        str: The index page.
    """
    feeds: list[FeedList] = get_feed_list(reader)
    return render_template("index.html", feed_list=feeds)


@app.route("/add")
def add() -> str:
    """Return the add page.

    Returns:
        str: The add page.
    """
    return render_template("add.html")


@app.route("/add", methods=["POST"])
def add_post() -> str:
    """Create a new group.

    Returns:
        str: The add page.
    """
    name: str = request.form.get("name", "")
    webhook_value: str = request.form.get("url", "")
    usernames_value: str = request.form.get("usernames", "")
    include_retweets: bool = get_include_retweets(request)
    include_replies: bool = get_include_replies(request)
    return create_group(
        name=name,
        webhook_value=webhook_value,
        usernames_value=usernames_value,
        include_retweets=include_retweets,
        include_replies=include_replies,
        reader=reader,
    )


@app.route("/remove_group", methods=["POST"])
def remove_group_post() -> str:
    """Remove a group.

    Returns:
        str: The index page.
    """
    name: str = request.form["name"]
    return remove_group(name=name, reader=reader)


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
