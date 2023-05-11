from random import randint
from typing import TYPE_CHECKING

from discord_webhook import DiscordEmbed, DiscordWebhook
from loguru import logger
from reader import Entry

from discord_twitter_webhooks.dataclasses import Settings
from discord_twitter_webhooks.get_tweet_text import get_tweet_text

if TYPE_CHECKING:
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

    if settings.embed_show_title:
        embed.set_title(entry.title or "Untitled")

    if settings.embed_show_author:
        embed.set_author(name=entry.title or "Unknown")

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
