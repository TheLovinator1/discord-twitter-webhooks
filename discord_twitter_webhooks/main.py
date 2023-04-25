from flask import Flask, render_template, request
from reader import Reader

from discord_twitter_webhooks.add_new_feed import add_new_feed
from discord_twitter_webhooks.get_feed_list import FeedList, get_feed_list
from discord_twitter_webhooks.settings import get_reader

app = Flask(__name__)

reader: Reader | None = get_reader()

if not reader:
    msg = "Failed to initialize reader."
    raise RuntimeError(msg)


@app.route("/")
def index() -> str:
    feed_list: list[FeedList] = get_feed_list(reader)
    return render_template("index.html", feed_list=feed_list)


@app.route("/add")
def add() -> str:
    return render_template("add.html")


@app.route("/add", methods=["POST"])
def add_post() -> str:
    """Add a new feed."""
    return add_new_feed(r=request, reader=reader)
