from functools import lru_cache
from random import randint
from typing import TYPE_CHECKING

from defusedxml import ElementTree
from discord_webhook import DiscordEmbed, DiscordWebhook
from loguru import logger
from reader import Entry
from requests import request

from discord_twitter_webhooks.dataclasses import Settings
from discord_twitter_webhooks.get_tweet_text import get_tweet_text

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from requests import Response


def get_color(settings: Settings) -> int:
    """Get the color of the embed.

    Returns:
        The color of the embed as an int.
    """
    twitter_blue = "#1DA1F2"
    embed_color: str = twitter_blue
    if webhook_embed_color := settings.embed_color:
        if settings.embed_color_random:
            embed_color = hex(randint(0, 16777215))[2:]  # noqa: S311
        elif len(webhook_embed_color) == 7 and webhook_embed_color[0] == "#":  # noqa: PLR2004
            embed_color: str = webhook_embed_color
        else:
            logger.error("Invalid webhook embed color {}. Using default color.", webhook_embed_color)
            embed_color: str = twitter_blue

    # Convert hex color to int.
    return int(embed_color[1:], 16)


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


def send_embed(entry: Entry, settings: Settings) -> None:
    """Send an embed to Discord.

    Args:
        entry: The entry to send.
        settings: The settings to use.
        reader: The reader to use.
    """
    logger.info(f"Sending {entry.title} as an embed to {settings.webhooks}")

    if not settings.webhooks:
        logger.error(f"No webhooks set for {entry.title}, skipping")
        return

    # We will add the URL later, so we can send embeds to multiple webhooks.
    webhook = DiscordWebhook(url="")

    tweet_text: str = get_tweet_text(entry, settings)
    embed = DiscordEmbed(description=tweet_text)
    entry_link: str = entry.link or ""

    if settings.embed_show_title:
        if entry.title:
            embed.set_title(entry.title)
        else:
            logger.error("No title for {}", entry_link)

    if settings.embed_show_author:
        if entry.author:
            avatar: str = get_avatar(entry.feed_url)
            embed.set_author(name=entry.author, url=entry_link, icon_url=avatar)
        else:
            logger.error("No author for {}", entry_link)

    if settings.embed_timestamp:
        embed.set_timestamp()

    embed.set_color(get_color(settings))

    webhook.add_embed(embed)

    for _webhook in settings.webhooks.split(","):
        logger.debug("Webhook URL: {}", _webhook)
        webhook.url = _webhook
        response: Response = webhook.execute()

        if response.ok:
            logger.info("Webhook posted for tweet https://twitter.com/i/status/{}", entry.link)
        else:
            logger.error(f"Got {response.status_code} from {webhook}. Response: {response.text}")
            logger.error(f"Got {response.status_code} from {webhook}. Response: {response.text}")
