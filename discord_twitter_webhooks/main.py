from typing import TYPE_CHECKING

from flask import Flask, render_template, request

from discord_twitter_webhooks.get_feed_list import FeedList, get_feed_list
from discord_twitter_webhooks.get_include_replies import get_include_replies
from discord_twitter_webhooks.get_include_retweets import get_include_retweets
from discord_twitter_webhooks.settings import get_reader

if TYPE_CHECKING:
    from collections.abc import Iterable

    from reader import Feed

app = Flask(__name__)


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
