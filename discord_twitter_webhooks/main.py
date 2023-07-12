import functools
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from reader import Reader
from reader.types import EntryLike
from starlette import status

from discord_twitter_webhooks._dataclasses import (
    ApplicationSettings,
    Group,
    get_group,
    get_app_settings,
    set_app_settings,
)
from discord_twitter_webhooks.reader_settings import get_reader
from discord_twitter_webhooks.send_to_discord import send_to_discord, send_link, send_text, send_embed
from discord_twitter_webhooks.translate import languages_from, languages_to

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

reader: Reader = get_reader()

# TODO: Add /debug page to show all the database fields
# TODO: Add backup/restore functionality


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Response:
    """Return the index page.

    Returns:
        The index page.
    """
    groups = reader.get_tag((), "groups", [])
    list_of_groups = [get_group(reader, group) for group in groups]
    list_of_groups = [group for group in list_of_groups if group]  # Remove None values

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "groups": list_of_groups,
            "app_settings": get_app_settings(reader),
        },
    )


@app.get("/add", response_class=HTMLResponse)
async def add(request: Request) -> Response:
    """Return the add page.

    Returns:
        The add page.
    """
    return templates.TemplateResponse(
        "feed.html",
        {
            "request": request,
            "settings": Group(),
            "modifying": False,
            "group_name": None,
            "languages_from": languages_from,
            "languages_to": languages_to,
        },
    )


@app.get("/modify/{uuid}", response_class=HTMLResponse)
async def modify(request: Request, uuid: str) -> Response:
    """Return the add page.

    Returns:
        The add page.
    """
    # Get the old settings
    group: Group = get_group(reader, uuid)

    return templates.TemplateResponse(
        "feed.html",
        {
            "request": request,
            "settings": group,
            "modifying": True,
            "languages_from": languages_from,
            "languages_to": languages_to,
        },
    )


@app.post("/feed")
async def feed(
    request: Request,
    name: Annotated[str, Form(title="Group Name")],
    webhooks: Annotated[str, Form(title="Webhook URLs")],
    usernames: Annotated[str, Form(title="Twitter Usernames")],
    uuid: Annotated[str, Form(title="UUID")] = "",
    send_retweets: Annotated[bool, Form(title="Include Retweets?")] = True,
    send_replies: Annotated[bool, Form(title="Include Replies?")] = True,
    send_as_text: Annotated[bool, Form(title="Send Text?")] = False,
    send_as_embed: Annotated[bool, Form(title="Send Embed?")] = False,
    embed_color: Annotated[str, Form(title="Embed Color")] = "#1DA1F2",
    embed_color_random: Annotated[bool, Form(title="Randomize Embed Color?")] = False,
    embed_author_name: Annotated[str, Form(title="Embed Author Name")] = "",
    embed_author_url: Annotated[str, Form(title="Embed Author URL")] = "",
    embed_author_icon_url: Annotated[str, Form(title="Embed Author Icon URL")] = "",
    embed_url: Annotated[str, Form(title="Embed URL")] = "",
    embed_timestamp: Annotated[bool, Form(title="Show Timestamp?")] = False,
    embed_image: Annotated[str, Form(title="Embed Image URL")] = "",
    embed_footer_text: Annotated[str, Form(title="Embed Footer Text")] = "",
    embed_footer_icon_url: Annotated[str, Form(title="Embed Footer Icon URL")] = "",
    embed_show_title: Annotated[bool, Form(title="Show Title?")] = False,
    embed_show_author: Annotated[bool, Form(title="Show Author?")] = False,
    send_as_link: Annotated[bool, Form(title="Send Only Link?")] = False,
    send_as_link_preview: Annotated[bool, Form(title="Should the link make a preview?")] = False,
    send_as_text_link_preview: Annotated[bool, Form(title="Should the link make a preview?")] = False,
    send_as_text_link: Annotated[bool, Form(title="Make the text a link?")] = False,
    send_as_text_link_url: Annotated[str, Form(title="Custom Link URL")] = "",
    unescape_html: Annotated[bool, Form(title="Unescape HTML?")] = True,
    remove_utm: Annotated[bool, Form(title="Remove UTM?")] = True,
    remove_copyright: Annotated[bool, Form(title="Remove Copyright?")] = True,
    translate: Annotated[bool, Form(title="Translate?")] = False,
    translate_from: Annotated[str, Form(title="Translate From")] = "auto",
    translate_to: Annotated[str, Form(title="Translate To")] = "en-GB",
):
    """Create or modify a group."""
    if not uuid:
        logger.info(f"Creating new group {name}")
        uuid = str(uuid4())

    # Webhooks and usernames are a single string with each item on a new line, so we split them to a real list
    # We are removing duplicates with set()
    webhooks_split = list(set(webhooks.splitlines()))
    usernames_split = list(set(usernames.splitlines()))

    if embed_color_random:
        # We will randomize the color later before sending the embed
        embed_color = "random"

    # Get the RSS feeds for each username
    # TODO: Check if the RSS feed is valid
    rss_feeds = [f"{get_app_settings(reader).nitter_instance}/{_feed}/rss" for _feed in usernames_split]

    group = Group(
        uuid=uuid,
        name=name,
        webhooks=webhooks_split,
        usernames=usernames_split,
        rss_feeds=rss_feeds,
        send_retweets=send_retweets,
        send_replies=send_replies,
        send_as_text=send_as_text,
        send_as_embed=send_as_embed,
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
        send_as_link=send_as_link,
        send_as_link_preview=send_as_link_preview,
        send_as_text_link=send_as_text_link,
        send_as_text_link_preview=send_as_text_link_preview,
        send_as_text_link_url=send_as_text_link_url,
        unescape_html=unescape_html,
        remove_utm=remove_utm,
        remove_copyright=remove_copyright,
        translate=translate,
        translate_from=translate_from,
        translate_to=translate_to,
    )

    # This will be used when adding group.rss_feeds
    rss_feeds = []

    # Add the group to the reader
    reader.set_tag((), uuid, group.__dict__)
    for _name in usernames_split:
        name_url = f"{get_app_settings(reader).nitter_instance}/{_name}/rss"  # TODO: Check if URL is valid
        # Add the rss feed to the reader
        reader.add_feed(name_url, exist_ok=True)

        # Add what groups the feed is connected to
        our_feed = reader.get_feed(name_url)
        groups = reader.get_tag(our_feed, "groups", [])  # type: ignore
        groups.append(uuid)
        reader.set_tag(our_feed, "groups", list(set(groups)))  # type: ignore
        logger.info(f"Added group {group.uuid} to feed {name_url}")

        rss_feeds.append(name_url)

    # Add the group to the groups list
    groups = reader.get_tag((), "groups", [])
    groups.append(uuid)
    reader.set_tag((), "groups", list(set(groups)))
    logger.info(f"Added group {group.uuid} to groups list")
    logger.info(f"Group list is now {set(groups)}")

    # Redirect to the index page.
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)  # TODO: What status code should this be?


@app.post("/remove_group")
async def remove_group_post(uuid: Annotated[str, Form()]) -> RedirectResponse:
    """Remove a group.

    Returns:
        str: The index page.
    """
    # TODO: We should also remove the rss feed if it was the last group using it.
    group: Group = get_group(reader, uuid)
    logger.info(f"Removing group {group}")

    reader.delete_tag((), uuid)

    groups = reader.get_tag((), "groups", [])
    groups.remove(uuid)
    reader.set_tag((), "groups", groups)

    # Redirect to the index page.
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)  # TODO: What status code should this be?


@app.get("/mark_as_unread/{uuid}")
async def mark_as_unread(uuid: str):
    """Mark a feed as unread.

    Args:
        uuid: The uuid of the feed to mark as unread.

    Returns:
        The index page. Or an error page if the feed could not be marked as unread.
    """
    # TODO: Mark feed as unread and send to Discord.
    logger.info(f"Marking feed {uuid} as unread")

    # Get the group
    group: Group = get_group(reader, uuid)

    if not group.rss_feeds:
        return HTMLResponse(f"No RSS feeds found for group {uuid}")

    # Get the feed
    feed = reader.get_feed(group.rss_feeds[0], None)
    logger.info(f"Feed is {feed}")

    # Get the entries
    entries = reader.get_entries(feed=feed)
    entries = list(entries)

    if not entries:
        # TODO: Return a proper error page
        return HTMLResponse(f"Failed to mark feed {uuid} as unread. No entries found.")

    # Mark the entry as unread
    entry: EntryLike
    for entry in entries:
        reader.mark_entry_as_unread(entry)

    for entry in entries:
        if group.send_as_link:
            send_link(entry=entry, group=group)
        if group.send_as_text:
            send_text(entry=entry, group=group)
        if group.send_as_embed:
            send_embed(entry=entry, group=group)

        # Mark the entry as read
        reader.mark_entry_as_read(entry)

    # Redirect to the index page.
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)  # TODO: What status code should this be?


@app.get("/settings")
async def settings(request: Request) -> Response:
    """Get the settings page.

    Args:
        request: The request object.

    Returns:
        Response: The settings page.
    """
    application_settings: ApplicationSettings = get_app_settings(reader)
    return templates.TemplateResponse("settings.html", {"request": request, "settings": application_settings})


@functools.lru_cache(maxsize=1)
@app.get("/favicon.svg")
async def favicon():
    """Get the favicon.

    Returns:
        Response: The favicon.
    """
    svg = """
    <svg xmlns="http://www.w3.org/2000/svg">
        <text x="50%" y="50%" dy=".3em" text-anchor="middle">🐦</text>
    </svg>
    """
    return Response(content=svg, media_type="image/svg+xml")


@app.post("/settings")
async def settings_post(
    request: Request,
    nitter_instance: Annotated[str, Form(title="Nitter instance")] = "",
    error_webhook: Annotated[str, Form(title="Error webhook")] = "",
    send_errors_to_discord: Annotated[bool, Form(title="Send errors to Discord?")] = False,
    deepl_auth_key: Annotated[str, Form(title="DeepL auth key")] = "",
) -> Response:
    """Save the settings.

    Args:
        request: The request object.
        nitter_instance: The Nitter instance to use.
        send_errors_to_discord: Whether to send errors to Discord.
        error_webhook: The webhook to send errors to.
        deepl_auth_key: The DeepL auth key to use.
    """
    if send_errors_to_discord and not error_webhook:
        logger.warning("You have enabled sending errors to Discord, but have not set a webhook. Disabling.")
        send_errors_to_discord = False

    app_settings = ApplicationSettings(
        nitter_instance=nitter_instance,
        send_errors_to_discord=send_errors_to_discord,
        error_webhook=error_webhook,
        deepl_auth_key=deepl_auth_key,
    )

    set_app_settings(reader, app_settings)
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "settings": app_settings,
        },
    )


@app.on_event("startup")
def startup() -> None:
    """This is called when the server starts.

    It adds missing tags and starts the scheduler.
    """
    log_format: str = "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <level>{level: <5}</level> <white>{message}</white>"
    logger.remove()
    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG",
        colorize=True,
        backtrace=False,
        diagnose=False,
        catch=True,
    )

    scheduler: BackgroundScheduler = BackgroundScheduler()

    # Check for new entries every 5 minutes. They will be sent to Discord if they are new.
    # TODO: Make this configurable.
    scheduler.add_job(sched_func, "interval", minutes=5, next_run_time=datetime.now(tz=timezone.utc))
    scheduler.start()


def sched_func() -> None:
    """The scheduler can't call a function with arguments, so we need to wrap it."""
    # TODO: We should update group.rss_feeds if the global nitter_instance has changed.
    # TODO: Check for errors and send to Discord. There is group.last_exception we can use.
    # TODO: Send to Discord if Nitter instance has problems.
    send_to_discord(reader)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
