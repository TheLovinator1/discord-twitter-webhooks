"""This file has only one function and that function helps with
embedding the tweet and sending it to Discord."""
import json

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook

from discord_twitter_webhooks import settings


def send_embed_webhook(
    tweet_id: int,
    link_list: list[str],
    text: str,
    twitter_card_image: str,
    avatar_url: str,
    screen_name: str,
    webhook: str = settings.webhook_url,
):
    """Send embed to Discord webhook.

    Args:
        avatar: Avatar URL
        tweet_id: Tweet id
        link_list: List of links from the tweet
        text: Text from the tweet
        webhook: Webhook URL. Defaults to environment variable WEBHOOK_URL.
        twitter_card_image: Twitter meta image.
    """
    settings.logger.debug(f"Tweet: {text}")

    hook = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(description=text)

    if twitter_card_image:
        embed.set_image(url=twitter_card_image)
        settings.logger.debug(f"twitter_card_image: {twitter_card_image}")

    # Only add image if there is one
    if len(link_list):
        if len(link_list) == 1:
            embed.set_image(url=link_list[0])

        elif len(link_list) > 1:
            # Send images to twitter-image-collage-maker
            # (e.g https://twitter.lovinator.space/) and get a collage back.
            response = requests.get(url=settings.collage_maker_url, params={"tweet_id": tweet_id})

            if response.status_code == 200:
                json_data = json.loads(response.text)
                settings.logger.debug(f"JSON data from twitter-image-collage-maker: {json_data}")
                embed.set_image(url=json_data["url"])
            else:
                settings.logger.error(f"Got {response.status_code} from {settings.collage_maker_url}")
                embed.set_image(url=link_list[0])

    settings.logger.debug(f"Avatar URL: {avatar_url}")

    embed.set_author(
        icon_url=avatar_url,
        name=screen_name,
        url=f"https://twitter.com/i/web/status/{tweet_id}",
    )

    # Add embed object to webhook
    hook.add_embed(embed)

    response = hook.execute()

    settings.logger.info(f"Webhook posted for tweet https://twitter.com/i/web/status/{tweet_id}")
    settings.logger.debug(f"Webhook response: {response}")


def send_normal_webhook(msg: str, webhook: str = settings.webhook_url):
    """Send normal message to Discord webhook.

    Args:
        msg: Message to send
        webhook: Webhook URL. Defaults to environment variable WEBHOOK_URL.
    """
    settings.logger.debug(f"Message: {msg}")

    hook = DiscordWebhook(url=webhook, content=msg)

    response = hook.execute()
    settings.logger.debug(f"Webhook response: {response}")
