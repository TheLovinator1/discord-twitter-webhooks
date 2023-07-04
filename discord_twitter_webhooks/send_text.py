from typing import TYPE_CHECKING

from discord_webhook import DiscordWebhook
from loguru import logger
from reader import Entry

from discord_twitter_webhooks._dataclasses import Group
from discord_twitter_webhooks.tweet_text import get_tweet_text

if TYPE_CHECKING:
    from requests import Response


def send_text(entry: Entry, group: Group) -> None:
    """Send text to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    logger.debug(f"Sending {entry.title} to {group.webhooks} as text")

    if not group.webhooks:
        logger.error(f"No webhooks set for {entry.title}, skipping")
        return

    # We will add the URL later, so we can send embeds to multiple webhooks.
    webhook = DiscordWebhook(url="")

    # The text that will be sent to Discord.
    webhook.content = get_tweet_text(entry, group)

    for _webhook in group.webhooks:
        logger.debug("Webhook URL: {}", _webhook)
        webhook.url = _webhook
        response: Response = webhook.execute()

        if response.ok:
            logger.info("Webhook posted for tweet https://twitter.com/i/status/{}", entry.link)
        else:
            logger.error(f"Got {response.status_code} from {webhook}. Response: {response.text}")
