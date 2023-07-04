from functools import lru_cache
from random import randint
from typing import TYPE_CHECKING

from defusedxml import ElementTree
from discord_webhook import DiscordEmbed
from reader import Reader
from requests import request

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from requests import Response
from typing import TYPE_CHECKING

from discord_webhook import DiscordWebhook
from loguru import logger
from reader import Entry

from discord_twitter_webhooks._dataclasses import Group
from discord_twitter_webhooks.tweet_text import get_tweet_text

if TYPE_CHECKING:
    from requests import Response


def send_webhook(webhook, entry, group) -> None:
    for _webhook in group.webhooks:
        logger.debug("Webhook URL: {}", _webhook)
        webhook.url = _webhook
        response: Response = webhook.execute()

        if response.ok:
            logger.info("Webhook posted for {}", entry.link)  # TODO: Double check me when Twitter works again
        else:
            logger.error(f"Got {response.status_code} from {webhook}. Response: {response.text}")


def send_text(entry: Entry, group: Group) -> None:
    """Send text to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    webhook = DiscordWebhook(url="")
    tweet_text = get_tweet_text(entry, group)

    # Send the tweet text to Discord
    webhook.content = tweet_text

    # Convert the text to a link if the user wants to
    if group.send_as_text_link:
        entry_link = group.send_as_text_link_url or entry.link
        webhook.content = f"[{tweet_text}]({entry_link})"  # TODO: Double check me when Twitter works again

    send_webhook(webhook, entry, group)


# TODO: Should we use requests-cache?
# TODO: Add a way to clear the cache in the web interface or on a timer?
@lru_cache(maxsize=128)
def get_avatar(rss_feed: str) -> str:
    """Get the avatar of the embed.

    Returns:
        The avatar of the embed as an int.
    """
    # Go to the rss feed and get the avatar
    response: Response = request("GET", rss_feed)
    default_avatar: str = "https://pbs.twimg.com/profile_images/1354479643882004483/Btnfm47p_400x400.jpg"
    if response.ok:
        # Parse XML and get the avatar
        xml_data: str = response.content.decode("utf-8")

        try:
            root: Element = ElementTree.fromstring(xml_data)
            found: Element | None = root.find("channel/image/url")
        except ElementTree.ParseError:
            logger.error("Unable to parse XML from {}", rss_feed)
            return default_avatar

        return found.text or default_avatar if found is not None else default_avatar

    logger.error(f"Got {response.status_code} from {rss_feed}. Response: {response.text}")
    return default_avatar


def send_embed(entry: Entry, group: Group) -> None:
    """Send an embed to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    logger.info(f"Sending {entry.title} as an embed to {group.webhooks}")

    # We will add the URL later, so we can send embeds to multiple webhooks.
    webhook = DiscordWebhook(url="")

    tweet_text: str = get_tweet_text(entry, group)
    embed = DiscordEmbed(description=tweet_text)
    entry_author = group.embed_author_name or entry.author
    author_avatar = group.embed_author_icon_url or get_avatar(entry.feed_url)

    # Show the tweeter as a title of the embed
    if group.embed_show_title:
        embed.set_title(entry_author)

    # Add an author to the embed, is name of tweeter and a small image of the avatar
    if group.embed_show_author:
        embed.set_author(  # TODO: Double check me when Twitter works again
            name=entry_author, url=entry.link, icon_url=author_avatar
        )

    # Show a timestamp at the bottom of the embed
    if group.embed_timestamp:
        embed.set_timestamp()

    # Embed color
    embed_color: str = group.embed_color
    if group.embed_color == "random":
        embed_color = hex(randint(0, 16777215))[2:]  # noqa: S311
    embed.set_color(embed_color)

    webhook.add_embed(embed)

    send_webhook(webhook, entry, group)


def send_link(entry: Entry, group: Group) -> None:
    """Send a link to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    webhook = DiscordWebhook(url="")

    what_to_send = f"{entry.title}"
    if group.send_as_link_preview:
        what_to_send = f"<{entry.title}>"

    webhook.content = what_to_send
    send_webhook(webhook, entry, group)


def send_to_discord(reader: Reader) -> None:
    """Send all new entries to Discord.

    This is called by the scheduler every 5 minutes. It will check for new entries and send them to Discord.

    Args:
        reader: The reader which contains the entries.
    """
    reader.update_feeds()

    # Loop through the unread (unsent) entries.
    entries = list(reader.get_entries(read=False))

    if not entries:
        logger.info("No new entries found.")
        return

    for entry in entries:
        group: Group = reader.get_tag(entry)
        if group.send_as_link:
            send_link(entry=entry, group=group)
        elif group.send_as_text:
            send_text(entry=entry, group=group)
        elif group.send_as_embed:
            send_embed(entry=entry, group=group)
        else:
            logger.warning(f"Unknown settings for tag {group.name}.")
