from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from reader import Reader

from discord_twitter_webhooks.add_missing_tags import add_missing_tags
from discord_twitter_webhooks.add_new_feed import create_group
from discord_twitter_webhooks.dataclasses import GlobalSettings, Settings
from discord_twitter_webhooks.get_feed_list import FeedList, get_feed_list
from discord_twitter_webhooks.get_settings import get_settings
from discord_twitter_webhooks.global_settings import (
    get_global_settings,
    save_global_settings,
)
from discord_twitter_webhooks.logger import setup_logger
from discord_twitter_webhooks.modify_feed import modify_feed
from discord_twitter_webhooks.reader_settings import get_reader
from discord_twitter_webhooks.remove_group import remove_group
from discord_twitter_webhooks.search import create_html_for_search_results
from discord_twitter_webhooks.send_to_discord import send_to_discord

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

reader: Reader | None = get_reader()

if not reader:
    msg = "Failed to initialize reader."
    raise RuntimeError(msg)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Response:
    """Return the index page.

    Returns:
        The index page.
    """
    feeds: list[FeedList] = get_feed_list(reader)
    return templates.TemplateResponse("index.html", {"request": request, "feed_list": feeds})


@app.get("/add", response_class=HTMLResponse)
async def add(request: Request) -> Response:
    """Return the add page.

    Returns:
        The add page.
    """
    return templates.TemplateResponse(
        "add.html",
        {
            "request": request,
            "settings": None,
            "modifying": False,
            "group_name": None,
        },
    )


@app.get("/modify/{group_name}", response_class=HTMLResponse)
async def modify(request: Request, group_name: str) -> Response:
    """Return the add page.

    Returns:
        The add page.
    """
    # Get the old settings
    settings: Settings = get_settings(reader, group_name)

    if not settings:
        msg: str = f"Failed to get settings for {group_name}"
        raise RuntimeError(msg)

    return templates.TemplateResponse(
        "modify.html",
        {
            "request": request,
            "settings": settings,
            "modifying": True,
            "group_name": group_name,
        },
    )


@app.post("/add")
async def add_post(  # noqa: PLR0913
    name: Annotated[str, Form(title="Group Name")],
    webhooks: Annotated[str, Form(title="Webhook URLs")],
    usernames: Annotated[str, Form(title="Twitter Usernames")],
    include_retweets: Annotated[bool, Form(title="Include Retweets?")] = False,
    include_replies: Annotated[bool, Form(title="Include Replies?")] = False,
    send_text: Annotated[bool, Form(title="Send Text?")] = False,
    send_embed: Annotated[bool, Form(title="Send Embed?")] = False,
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
    send_only_link: Annotated[bool, Form(title="Send Only Link?")] = False,
    send_only_link_preview: Annotated[bool, Form(title="Should the link make a preview?")] = False,
    make_text_a_link: Annotated[bool, Form(title="Make Text a Link?")] = False,
    make_text_a_link_preview: Annotated[bool, Form(title="Should the link make a preview?")] = False,
    make_text_a_link_url: Annotated[str, Form(title="Link URL")] = "",
    upload_media: Annotated[bool, Form(title="Upload images to Discord?")] = False,
    append_usernames: Annotated[bool, Form(title="Append usernames to text?")] = False,
    translate: Annotated[bool, Form(title="Translate the tweet?")] = False,
    translate_to: Annotated[str, Form(title="Language to translate to")] = "en",
    translate_from: Annotated[str, Form(title="Language to translate from")] = "auto",
    whitelist: Annotated[str, Form(title="Whitelisted words")] = "",
    whitelist_active: Annotated[bool, Form(title="Use whitelist?")] = False,
    blacklist: Annotated[str, Form(title="Blacklisted words")] = "",
    blacklist_active: Annotated[bool, Form(title="Use blacklist?")] = False,
    unescape_html: Annotated[bool, Form(title="Unescape HTML?")] = False,
    remove_utm: Annotated[bool, Form(title="Remove UTM?")] = False,
    remove_copyright: Annotated[bool, Form(title="Remove Copyright?")] = False,
    username_destination: Annotated[str, Form(title="Username link destination")] = "",
    hashtag_destination: Annotated[str, Form(title="Hashtag link destination")] = "",
) -> RedirectResponse:
    """Create a new group.

    Returns:
        str: The add page.
    """
    create_group(
        reader=reader,
        name=name,
        webhook_value=webhooks,
        usernames_value=usernames,
        include_retweets=include_retweets,
        include_replies=include_replies,
        send_text=send_text,
        send_embed=send_embed,
        embed_color=embed_color,
        embed_color_random=embed_color_random,
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
        whitelist=whitelist,
        whitelist_active=whitelist_active,
        blacklist=blacklist,
        blacklist_active=blacklist_active,
        unescape_html=unescape_html,
        remove_utm=remove_utm,
        remove_copyright=remove_copyright,
        username_destination=username_destination,
        hashtag_destination=hashtag_destination,
    )

    # Redirect to the index page.
    return RedirectResponse(url="/", status_code=303)


@app.post("/modify")
async def modify_post(  # noqa: PLR0913
    name: Annotated[str, Form(title="Group Name")] = "",
    webhooks: Annotated[str, Form(title="Webhook URLs")] = "",
    usernames: Annotated[str, Form(title="Twitter Usernames")] = "",
    include_retweets: Annotated[bool, Form(title="Include Retweets?")] = False,
    include_replies: Annotated[bool, Form(title="Include Replies?")] = False,
    send_text: Annotated[bool, Form(title="Send Text?")] = False,
    send_embed: Annotated[bool, Form(title="Send Embed?")] = False,
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
    embed_show_author: Annotated[bool, Form(title="Show Author?")] = True,
    send_only_link: Annotated[bool, Form(title="Send Only Link?")] = False,
    send_only_link_preview: Annotated[bool, Form(title="Should the link make a preview?")] = False,
    make_text_a_link: Annotated[bool, Form(title="Make Text a Link?")] = False,
    make_text_a_link_preview: Annotated[bool, Form(title="Should the link make a preview?")] = False,
    make_text_a_link_url: Annotated[str, Form(title="Link URL")] = "",
    upload_media: Annotated[bool, Form(title="Upload images to Discord?")] = False,
    append_usernames: Annotated[bool, Form(title="Append usernames to text?")] = False,
    translate: Annotated[bool, Form(title="Translate the tweet?")] = False,
    translate_to: Annotated[str, Form(title="Language to translate to")] = "en",
    translate_from: Annotated[str, Form(title="Language to translate from")] = "auto",
    whitelist: Annotated[str, Form(title="Whitelisted words")] = "",
    whitelist_active: Annotated[bool, Form(title="Use whitelist?")] = False,
    blacklist: Annotated[str, Form(title="Blacklisted words")] = "",
    blacklist_active: Annotated[bool, Form(title="Use blacklist?")] = False,
    unescape_html: Annotated[bool, Form(title="Unescape HTML?")] = False,
    remove_utm: Annotated[bool, Form(title="Remove UTM?")] = False,
    remove_copyright: Annotated[bool, Form(title="Remove Copyright?")] = False,
    username_destination: Annotated[str, Form(title="Username link destination")] = "",
    hashtag_destination: Annotated[str, Form(title="Hashtag link destination")] = "",
) -> RedirectResponse:
    """Create a new group.

    Returns:
        str: The add page.
    """
    if not name:
        # TODO: Add a flash message.
        return "Name cannot be empty."  # type: ignore  # noqa: PGH003

    modify_feed(
        reader=reader,
        name=name,
        webhooks=webhooks,
        usernames=usernames,
        include_retweets=include_retweets,
        include_replies=include_replies,
        send_text=send_text,
        send_embed=send_embed,
        embed_color=embed_color,
        embed_color_random=embed_color_random,
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
        whitelist=whitelist,
        whitelist_active=whitelist_active,
        blacklist=blacklist,
        blacklist_active=blacklist_active,
        unescape_html=unescape_html,
        remove_utm=remove_utm,
        remove_copyright=remove_copyright,
        username_destination=username_destination,
        hashtag_destination=hashtag_destination,
    )

    # Redirect to the index page.
    return RedirectResponse(url="/", status_code=303)


@app.post("/remove_group")
async def remove_group_post(name: Annotated[str, Form()]) -> RedirectResponse:
    """Remove a group.

    Returns:
        str: The index page.
    """
    remove_group(name=name, reader=reader)

    # Redirect to the index page.
    return RedirectResponse(url="/", status_code=303)


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
async def mark_as_unread(group_name: str) -> RedirectResponse:
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

                    # Send the feed to the webhook.
                    send_to_discord(reader)

                    # Only do for one feed.
                    break

    # Redirect to the index page.
    return RedirectResponse(url="/", status_code=303)


@app.get("/settings")
async def settings(request: Request) -> Response:
    """Get the settings page.

    Args:
        request: The request object.

    Returns:
        Response: The settings page.
    """
    global_settings: GlobalSettings = get_global_settings(reader=reader)
    return templates.TemplateResponse("settings.html", {"request": request, "settings": global_settings})


@app.post("/settings")
async def settings_post(
    request: Request,
    nitter_instance: Annotated[str, Form(title="Nitter instance")] = "",
    translator_instance: Annotated[str, Form(title="Translator instance")] = "",
    error_webhook: Annotated[str, Form(title="Error webhook")] = "",
    send_errors_to_discord: Annotated[bool, Form(title="Send errors to Discord?")] = False,
) -> Response:
    """Save the settings.

    Args:
        request: The request object.
        nitter_instance: The Nitter instance to use.
        translator_instance: The translator instance to use.
        send_errors_to_discord: Whether to send errors to Discord.
        error_webhook: The webhook to send errors to.
    """
    logger.info(send_errors_to_discord)
    save_settings(
        nitter_instance=nitter_instance,
        translator_instance=translator_instance,
        send_errors_to_discord=send_errors_to_discord,
        error_webhook=error_webhook,
    )
    global_settings: GlobalSettings = get_global_settings(reader=reader)
    return templates.TemplateResponse("settings.html", {"request": request, "settings": global_settings})


def save_settings(
    nitter_instance: str,
    translator_instance: str,
    send_errors_to_discord: bool,
    error_webhook: str,
) -> None:
    """Save the settings."""
    global_settings = GlobalSettings()
    global_settings.nitter_instance = nitter_instance
    global_settings.translator_instance = translator_instance
    global_settings.send_errors_to_discord = send_errors_to_discord
    global_settings.error_webhook = error_webhook
    save_global_settings(reader=reader, global_settings=global_settings)


@app.on_event("startup")
def startup() -> None:
    """This is called when the server starts.

    It adds missing tags and starts the scheduler.
    """
    setup_logger()
    add_missing_tags(reader=reader)

    scheduler: BackgroundScheduler = BackgroundScheduler()

    # Check for new entries every 5 minutes. They will be sent to Discord if they are new.
    # TODO: Make this configurable.
    scheduler.add_job(sched_func, "interval", minutes=5, next_run_time=datetime.now(tz=timezone.utc))
    scheduler.start()


def sched_func() -> None:
    """A function to be called by the scheduler."""
    send_to_discord(reader)
