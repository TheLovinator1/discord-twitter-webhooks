"""This file has only one function and that function helps with
embedding the tweet and sending it to Discord."""
import json

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook

from discord_twitter_webhooks import settings


def send_embed_webhook(
    tweet,
    link_list: list[str],
    text: str,
    twitter_card_image: str,
    webhook: str = settings.webhook_url,
):
    """Send embed to Discord webhook.

    Args:
        avatar (str): Avatar URL
        tweet ([type]): Tweet object
        link_list (list[str]): List of links from the tweet
        text (str): Text from the tweet
        webhook (str, optional): Webhook URL. Defaults to environment
        variable WEBHOOK_URL.
        twitter_card_image (str, optional): Twitter meta image.
    """
    settings.logger.debug(f"Tweet: {text}")

    hook = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(description=text)

    if twitter_card_image:
        embed.set_image(url=twitter_card_image)
        settings.logger.debug(f"Tweet: {text}")

    # Only add image if there is one
    if len(link_list):
        if len(link_list) == 1:
            embed.set_image(url=link_list[0])

        elif len(link_list) > 1:
            # Send images to twitter-image-collage-maker
            # (e.g https://twitter.lovinator.space/) and get a collage back.
            response = requests.get(url=settings.collage_maker_url, params={"tweet_id": tweet.id})  # noqa: E501, pylint: disable=line-too-long

            if response.status_code == 200:
                json_data = json.loads(response.text)
                embed.set_image(url=json_data["url"])
            else:
                settings.logger.error(f"Failed to get response from {settings.collage_maker_url}. Using first image instead.")  # noqa: E501, pylint: disable=line-too-long
                embed.set_image(url=link_list[0])

    avatar_url = tweet.user.profile_image_url_https
    avatar_url = avatar_url.replace("_normal.jpg", ".jpg")

    embed.set_author(
        icon_url=avatar_url,
        name=tweet.user.screen_name,
        url=f"https://twitter.com/i/web/status/{tweet.id}",
    )

    # Add embed object to webhook
    hook.add_embed(embed)

    response = hook.execute()

    settings.logger.info(f"Webhook posted for tweet https://twitter.com/i/web/status/{tweet.id}")  # noqa: E501, pylint: disable=line-too-long
    settings.logger.debug(f"Webhook response: {response}")
