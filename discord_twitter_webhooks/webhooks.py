from typing import TYPE_CHECKING

from discord_webhook import DiscordEmbed, DiscordWebhook
from loguru import logger
from reader import Entry

if TYPE_CHECKING:
    import requests

DISCORD_WEBHOOK_URL = ""


def send_entry_to_discord(entry: Entry) -> None:
    """Sends an entry to Discord.

    Args:
        entry: The entry to send.
    """
    logger.info(f"Sending entry to Discord: {entry}")
    send_embed_to_discord(entry)


def send_embed_to_discord(entry: Entry) -> None:
    """Sends an entry to Discord as an embed.

    Args:
        entry: The entry to send.
    """
    embed: DiscordEmbed = DiscordEmbed(description=entry.title, url=entry.link)
    embed.set_author(name=entry.author or "Twitter", url=entry.link or "https://twitter.com")
    embed.set_footer(text=str(entry.published) or "Unknown Date")

    hook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
    hook.add_embed(embed)

    response: requests.Response = hook.execute()
    if not response.ok:
        logger.error("Failed to send entry to Discord: {}", response.text)
