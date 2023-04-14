from dataclasses import dataclass
from itertools import groupby
from typing import TYPE_CHECKING

from flask import Flask, render_template, request

from discord_twitter_webhooks.settings import init_reader

if TYPE_CHECKING:
    from reader import Feed

app = Flask(__name__)


@dataclass
class TwitterGroup:
    name: str
    webhook_url: str
    rss_feeds: list[str]
    include_retweets: bool = False
    include_replies: bool = False


@app.route("/")
def index() -> str:
    html: str = ""
    html += "<h1>Discord Twitter Webhooks</h1>"
    reader = init_reader()

    if reader is None:
        return "Failed to initialize reader"

    reader.update_feeds()

    html_before = html
    feed_list = []
    rss_feeds = []

    # Create a list of TwitterGroup objects
    for feed in reader.get_feeds():
        tags = reader.get_tags(feed)
        rss_feeds.append(feed.url)
        feed_group = TwitterGroup("", "", include_replies=False, include_retweets=False, rss_feeds=rss_feeds)

        for tag in tags:
            if tag[0] == "name":
                feed_group.name = str(tag[1]) or "No name"
            elif tag[0] == "webhook":
                feed_group.webhook_url = str(tag[1]) or "No webhook"
            elif tag[0] == "include_retweets":
                feed_group.include_retweets = bool(tag[1])
            elif tag[0] == "include_replies":
                feed_group.include_replies = bool(tag[1])
        feed_list.append(feed_group)

    # Group by name
    feed_list.sort(key=lambda x: x.name)
    feed_list = [list(g) for k, g in groupby(feed_list, lambda x: x.name)]

    # Add the feeds to the html
    for things in feed_list:
        html += f"<h2>{things[0].name}</h2>"
        html += "<p>Feeds:</p>"
        html += "<ul>"
        feeds = things[0].rss_feeds
        for feed in feeds:
            html += f"<li>{feed}</li>"

        html += "</ul>"

        html += f"<p>Webhook: {things[0].webhook_url}</p>"
        html += f"<p>Include retweets: {things[0].include_retweets}</p>"
        html += f"<p>Include replies: {things[0].include_replies}</p>"
        html += "<hr>"

    # If the html hasn't changed, add the add link
    if html == html_before:
        html += "<p>You can add more feeds here: <a href='/add'>/add</a></p>"

    return html


@app.route("/add")
def add() -> str:
    return render_template("add.html")


@app.route("/add", methods=["POST"])
def add_post() -> str:
    reader = init_reader()

    if reader is None:
        return "Error"

    name: str | None = request.form.get("name")
    webhook_value: str | None = request.form.get("url")
    usernames_value: str | None = request.form.get("usernames")
    include_retweets_value: str | None = request.form.get("include_retweets")
    include_replies_value: str | None = request.form.get("include_replies")

    if webhook_value is None or usernames_value is None:
        return "Error"

    username_list: list[str] = usernames_value.split(" ")

    include_retweets: bool = include_retweets_value == "true"
    include_replies: bool = include_replies_value == "true"

    for username in username_list:
        feed_url: str = f"https://nitter.lovinator.space/{username}/rss"
        reader.add_feed(feed_url, exist_ok=True)

        feed: Feed = reader.get_feed(feed_url)

        # Add webhook, include_retweets and include_replies to the feed as tags
        reader.set_tag(feed, "name", name)  # type: ignore
        reader.set_tag(feed, "webhook", webhook_value or None)  # type: ignore
        reader.set_tag(feed, "include_retweets", include_retweets or False)  # type: ignore
        reader.set_tag(feed, "include_replies", include_replies or False)  # type: ignore

        feed_name: str | None = reader.get_tag(feed, "name")  # type: ignore
        feed_webhook: str | None = reader.get_tag(feed, "webhook")  # type: ignore
        feed_include_retweets: bool | None = reader.get_tag(feed, "include_retweets")  # type: ignore
        feed_include_replies: bool | None = reader.get_tag(feed, "include_replies")  # type: ignore

        if feed_name is None or feed_webhook is None or feed_include_retweets is None or feed_include_replies is None:
            return (
                f"Error - Something was None that shouldn't be it:\nname: {feed_name}\nwebhook: {feed_webhook}\n"
                f"include_retweets: {feed_include_retweets}\ninclude_replies: {feed_include_replies}"
            )
    return f"Added {name} with usernames {usernames_value} and webhook {webhook_value} to the database."
