from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from reader import Reader

from discord_twitter_webhooks.add_missing_tags import add_missing_tags
from discord_twitter_webhooks.add_new_feed import create_group
from discord_twitter_webhooks.get_feed_list import FeedList, get_feed_list
from discord_twitter_webhooks.remove_group import remove_group
from discord_twitter_webhooks.search import create_html_for_search_results
from discord_twitter_webhooks.send_to_discord import send_to_discord
from discord_twitter_webhooks.settings import get_reader

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

reader: Reader | None = get_reader()

if not reader:
    msg = "Failed to initialize reader."
    raise RuntimeError(msg)


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> Response:
    """Return the index page.

    Returns:
        The index page.
    """
    feeds: list[FeedList] = get_feed_list(reader)
    return templates.TemplateResponse("index.html", {"request": request, "feed_list": feeds})


@app.get("/add", response_class=HTMLResponse)
def add(request: Request) -> Response:
    """Return the add page.

    Returns:
        The add page.
    """
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add")
def add_post(  # noqa: PLR0913
    name: Annotated[str, Form(title="Group Name")],
    webhooks: Annotated[str, Form(title="Webhook URLs")],
    usernames: Annotated[str, Form(title="Twitter Usernames")],
    include_retweets: Annotated[bool, Form(title="Include Retweets?")] = False,  # noqa: FBT002
    include_replies: Annotated[bool, Form(title="Include Replies?")] = False,  # noqa: FBT002
    send_text: Annotated[bool, Form(title="Send Text?")] = True,  # noqa: FBT002
    send_embed: Annotated[bool, Form(title="Send Embed?")] = False,  # noqa: FBT002
    embed_color: Annotated[str, Form(title="Embed Color")] = "#1DA1F2",
    embed_author_name: Annotated[str, Form(title="Embed Author Name")] = "",
    embed_author_url: Annotated[str, Form(title="Embed Author URL")] = "",
    embed_author_icon_url: Annotated[str, Form(title="Embed Author Icon URL")] = "",
    embed_url: Annotated[str, Form(title="Embed URL")] = "",
    embed_timestamp: Annotated[bool, Form(title="Show Timestamp?")] = True,  # noqa: FBT002
    embed_image: Annotated[str, Form(title="Embed Image URL")] = "",
    embed_footer_text: Annotated[str, Form(title="Embed Footer Text")] = "",
    embed_footer_icon_url: Annotated[str, Form(title="Embed Footer Icon URL")] = "",
    embed_show_title: Annotated[bool, Form(title="Show Title?")] = True,  # noqa: FBT002
    embed_show_author: Annotated[bool, Form(title="Show Author?")] = True,  # noqa: FBT002
    send_only_link: Annotated[bool, Form(title="Send Only Link?")] = False,  # noqa: FBT002
    send_only_link_preview: Annotated[bool, Form(title="Should the link make a preview?")] = False,  # noqa: FBT002
    make_text_a_link: Annotated[bool, Form(title="Make Text a Link?")] = False,  # noqa: FBT002
    make_text_a_link_preview: Annotated[bool, Form(title="Should the link make a preview?")] = False,  # noqa: FBT002
    make_text_a_link_url: Annotated[str, Form(title="Link URL")] = "",
    upload_media: Annotated[bool, Form(title="Upload images to Discord?")] = False,  # noqa: FBT002
    append_usernames: Annotated[bool, Form(title="Append usernames to text?")] = False,  # noqa: FBT002
    translate: Annotated[bool, Form(title="Translate the tweet?")] = False,  # noqa: FBT002
    translate_to: Annotated[str, Form(title="Language to translate to")] = "en",
    translate_from: Annotated[str, Form(title="Language to translate from")] = "auto",
    whitelist_words: Annotated[str, Form(title="Whitelisted words")] = "",
    whitelist_active: Annotated[bool, Form(title="Use whitelist?")] = False,  # noqa: FBT002
    blacklist_words: Annotated[str, Form(title="Blacklisted words")] = "",
    blacklist_active: Annotated[bool, Form(title="Use blacklist?")] = False,  # noqa: FBT002
    unescape_html: Annotated[bool, Form(title="Unescape HTML?")] = False,  # noqa: FBT002
    remove_utm: Annotated[bool, Form(title="Remove UTM?")] = False,  # noqa: FBT002
    remove_copyright: Annotated[bool, Form(title="Remove Copyright?")] = False,  # noqa: FBT002
    convert_usernames_to_links: Annotated[bool, Form(title="Convert usernames to links?")] = True,  # noqa: FBT002
    username_link_destination: Annotated[str, Form(title="Username link destination")] = "",
    convert_hashtags_to_links: Annotated[bool, Form(title="Convert hashtags to links?")] = True,  # noqa: FBT002
    hashtag_link_destination: Annotated[str, Form(title="Hashtag link destination")] = "",
) -> str:
    """Create a new group.

    Returns:
        str: The add page.
    """
    return create_group(
        reader=reader,
        name=name,
        webhook_value=webhooks,
        usernames_value=usernames,
        include_retweets=include_retweets,
        include_replies=include_replies,
        send_text=send_text,
        send_embed=send_embed,
        embed_color=embed_color,
        embed_author_name=embed_author_name,
        embed_author_url=embed_author_url,
        embed_author_icon_url=embed_author_icon_url,
        embed_url=embed_url,
        embed_timestamp=embed_timestamp,
        embed_image=embed_image,
        embed_footer_text=embed_footer_text,
        embed_footer_icon_url=embed_footer_icon_url,
        embed_show_title=embed_show_title,
        embed_show_author=embed_show_author,
        send_only_link=send_only_link,
        send_only_link_preview=send_only_link_preview,
        make_text_a_link=make_text_a_link,
        make_text_a_link_preview=make_text_a_link_preview,
        make_text_a_link_url=make_text_a_link_url,
        upload_media=upload_media,
        append_usernames=append_usernames,
        translate=translate,
        translate_to=translate_to,
        translate_from=translate_from,
        whitelist_words=whitelist_words,
        whitelist_active=whitelist_active,
        blacklist_words=blacklist_words,
        blacklist_active=blacklist_active,
        unescape_html=unescape_html,
        remove_utm=remove_utm,
        remove_copyright=remove_copyright,
        convert_usernames_to_links=convert_usernames_to_links,
        username_link_destination=username_link_destination,
        convert_hashtags_to_links=convert_hashtags_to_links,
        hashtag_link_destination=hashtag_link_destination,
    )


@app.post("/remove_group")
def remove_group_post(name: Annotated[str, Form()]) -> str:
    """Remove a group.

    Returns:
        str: The index page.
    """
    return remove_group(name=name, reader=reader)


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, query: str) -> Response:
    """Get entries matching a full-text search query.

    Args:
        query: The query to search for.
        request: The request object.

    Returns:
        HTMLResponse: The search page.
    """
    reader.update_search()

    context = {
        "request": request,
        "search_html": create_html_for_search_results(query),
        "query": query,
        "search_amount": reader.search_entry_counts(query),
    }
    return templates.TemplateResponse("search.html", context)


@app.get("/mark_as_unread/{group_name}")
def mark_as_unread(group_name: str) -> str:
    """Mark a feed as unread.

    Returns:
        str: The index page.
    """
    feeds = list(reader.get_feeds())
    for feed in feeds:
        # Get the tags for the feed.
        tags = list(reader.get_tags(feed))
        logger.info(f"Tags for {feed}: {tags}")
        for tag in tags:
            if group_name in tag:
                # Mark all entries as unread.
                for entry in reader.get_entries(feed=feed):
                    reader.set_entry_read(entry, False)
                    logger.info(f"Marked {entry.title} as unread.")
    return "OK"


@app.on_event("startup")
def startup() -> None:
    """This is called when the server starts.

    It adds missing tags and starts the scheduler.
    """
    add_missing_tags(reader=reader)

    scheduler: BackgroundScheduler = BackgroundScheduler()

    # Check for new entries every 5 minutes. They will be sent to Discord if they are new.
    # TODO: Make this configurable.
    scheduler.add_job(sched_func, "interval", minutes=5, next_run_time=datetime.now(tz=timezone.utc))
    scheduler.start()


def sched_func() -> None:
    """A function to be called by the scheduler."""
    send_to_discord(reader)
