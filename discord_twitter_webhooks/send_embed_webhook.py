import json

import requests
from dhooks import Embed, Webhook

from discord_twitter_webhooks.settings import (
    logger,
    twitter_image_collage_maker,
    webhook_url,
)


def send_embed_webhook(
    tweet, link_list: list[str], text: str, twitter_card_image: str, webhook: str = webhook_url
) -> None:
    """Send embed to Discord webhook.

    Args:
        avatar (str): Avatar URL
        tweet ([type]): Tweet object
        link_list (list[str]): List of links from the tweet
        text (str): Text from the tweet
        webhook (str, optional): Webhook URL. Defaults to environment variable WEBHOOK_URL.
        twitter_card_image (str, optional): Twitter meta image.
    """
    logger.debug(f"Tweet: {text}")
    hook = Webhook(webhook)

    embed = Embed(
        description=text,
        color=0x1E0F3,
        timestamp="now",
    )

    if twitter_card_image:
        embed.set_image(twitter_card_image)

    # Only add image if there is one
    if len(link_list):
        if len(link_list) == 1:
            logger.debug(f"Found one image: {link_list[0]}")
            embed.set_image(link_list[0])

        elif len(link_list) > 1:
            # Send images to twitter-image-collage-maker(e.g https://twitter.lovinator.space/) and get a collage back.
            response = requests.get(url=collage_maker_url, params={"tweet_id": tweet.id})

            if response.status_code == 200:
                json_data = json.loads(response.text)
                embed.set_image(json_data["url"])
            else:
                logger.error(f"Failed to get response from {collage_maker_url}. Using first image instead.")
                embed.set_image(link_list[0])

    avatar_url = tweet.user.profile_image_url_https
    logger.debug(f"Avatar URL: {avatar_url}")
    avatar_url = avatar_url.replace("_normal.jpg", ".jpg")

    embed.set_author(
        icon_url=avatar_url,
        name=tweet.user.screen_name,
        url=f"https://twitter.com/i/web/status/{tweet.id}",
    )

    hook.send(embed=embed)

    logger.info(f"Webhook posted for tweet https://twitter.com/i/web/status/{tweet.id}")
