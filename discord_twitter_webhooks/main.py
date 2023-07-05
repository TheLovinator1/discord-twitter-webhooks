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
from starlette import status

from discord_twitter_webhooks._dataclasses import (
    ApplicationSettings,
    Group,
    get_group,
    get_app_settings,
    set_app_settings,
)
from discord_twitter_webhooks.reader_settings import get_reader
from discord_twitter_webhooks.send_to_discord import send_to_discord

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

reader: Reader = get_reader()


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
        "add.html",
        {
            "request": request,
            "settings": Group(),
            "modifying": False,
            "group_name": None,
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
        "modify.html",
        {
            "request": request,
            "settings": group,
            "modifying": True,
        },
    )


@app.post("/add")
@app.post("/modify")
async def add_post(
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
) -> RedirectResponse:
    """Create a new group.

    Returns:
        str: The add page.
    """
    # Check if we are modifying and if no uuid
    if not uuid and "modify" in request.url.path:
        return "Failed to modify group. No UUID provided."

    if not uuid:
        uuid = str(uuid4())

    webhooks_split = webhooks.splitlines()
    usernames_split = usernames.splitlines()

    if embed_color_random:
        embed_color = "random"

    group = Group(
        uuid=uuid,
        name=name,
        webhooks=webhooks_split,
        usernames=usernames_split,
        rss_feeds=[],
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
        groups = set(groups)  # Remove duplicates
        reader.set_tag(our_feed, "groups", list(groups))  # type: ignore
        logger.info(f"Added group {group.uuid} to feed {name_url}")

        rss_feeds.append(name_url)

    # Add the group to the groups list
    groups = reader.get_tag((), "groups", [])
    groups.append(uuid)
    groups = set(groups)  # Remove duplicates
    reader.set_tag((), "groups", list(groups))  # type: ignore
    logger.info(f"Added group {group.uuid} to groups list")
    logger.info(f"Group list is now {groups}")

    # Redirect to the index page.
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)  # TODO: What status code should this be?


@app.post("/remove_group")
async def remove_group_post(uuid: Annotated[str, Form()]) -> RedirectResponse:
    """Remove a group.

    Returns:
        str: The index page.
    """
    # TODO: We should also remove the rss feed if it was the last group using it.
    group: Group = reader.get_tag((), uuid)  # type: ignore
    logger.info(f"Removing group {group}")

    reader.delete_tag((), uuid)

    groups = reader.get_tag((), "groups", [])
    logger.info(f"Group list is {groups}")
    groups.remove(uuid)
    reader.set_tag((), "groups", groups)
    logger.info(f"Group list is now {groups}")

    # Redirect to the index page.
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)  # TODO: What status code should this be?


@app.get("/mark_as_unread/{uuid}")
async def mark_as_unread(uuid: str) -> RedirectResponse:
    """Mark a feed as unread.

    Args:
        uuid: The uuid of the feed to mark as unread.

    Returns:
        str: The index page.
    """
    # TODO: Mark feed as unread and send to Discord.
    logger.info(f"Marking feed {uuid} as unread")

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


@app.post("/settings")
async def settings_post(
    request: Request,
    nitter_instance: Annotated[str, Form(title="Nitter instance")] = "",
    error_webhook: Annotated[str, Form(title="Error webhook")] = "",
    send_errors_to_discord: Annotated[bool, Form(title="Send errors to Discord?")] = False,
) -> Response:
    """Save the settings.

    Args:
        request: The request object.
        nitter_instance: The Nitter instance to use.
        send_errors_to_discord: Whether to send errors to Discord.
        error_webhook: The webhook to send errors to.
    """
    if send_errors_to_discord and not error_webhook:
        logger.warning("You have enabled sending errors to Discord, but have not set a webhook. Disabling.")
        send_errors_to_discord = False

    app_settings = ApplicationSettings(
        nitter_instance=nitter_instance,
        send_errors_to_discord=send_errors_to_discord,
        error_webhook=error_webhook,
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
    """A function to be called by the scheduler."""
    send_to_discord(reader)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
