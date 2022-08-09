""" Discord webhook stuff

send_embed_webhook - Send an embed to Discord webhook.
send_normal_webhook - Send a normal message to Discord webhook. We use this for sending errors.
"""
import json

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook

from discord_twitter_webhooks import settings


def send_embed_webhook(
        tweet_id: int,
        media_links: list[str],
        text: str,
        twitter_card_image: str,
        avatar_url: str,
        screen_name: str,
        webhook: str,
):
    """Send an embed to Discord webhook.

    Args:
        avatar_url: Avatar URL of the user. Will be used as the avatar for the embed.
        screen_name: The username, we use this to show who the tweet is from in the embed.
        tweet_id: Tweet ID of the tweet. This is used to link to the tweet on Twitter.
        media_links: List of media links from the tweet. This is used to add the images to the embed.
        text: Text from the tweet to send in the embed.
        webhook: Webhook URL. Defaults to environment variable WEBHOOK_URL.
        twitter_card_image: Twitter card image from the tweet.
    """

    settings.logger.debug(f"send_normal_webhook() - Tweet ID: {tweet_id}")
    settings.logger.debug(f"send_normal_webhook() - Text: {text}")
    settings.logger.debug(f"send_normal_webhook() - Twitter card image: {twitter_card_image}")
    settings.logger.debug(f"send_normal_webhook() - Avatar URL: {avatar_url}")
    settings.logger.debug(f"send_normal_webhook() - Screen name: {screen_name}")
    settings.logger.debug(f"send_normal_webhook() - Webhook URL: {webhook}")
    for media_link in media_links:
        settings.logger.debug(f"send_normal_webhook() - Media link: {media_link}")

    if not webhook:
        settings.logger.error("No webhook URL found")
        if settings.send_errors == "True":
            send_normal_webhook(f"No webhook URL found. Trying to send tweet embed for {tweet_id}",
                                settings.error_webhook)
        return

    hook = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(description=text)

    if twitter_card_image:
        embed.set_image(url=twitter_card_image)

    # Only add image if one
    if len(media_links):
        if len(media_links) == 1:
            embed.set_image(url=media_links[0])

        elif len(media_links) > 1:
            # Send images to twitter-image-collage-maker
            # (e.g https://twitter.lovinator.space/) and get a collage back.
            response = requests.get(url=settings.collage_maker_url, params={"tweet_id": tweet_id})

            if response.ok:
                json_data = json.loads(response.text)
                settings.logger.debug(f"JSON data from twitter-image-collage-maker: {json_data}")
                embed.set_image(url=json_data["url"])
            else:
                error_msg = f"Got {response.status_code!r} from {settings.collage_maker_url!r} for tweet {tweet_id!r}"
                settings.logger.error(error_msg)
                embed.set_image(url=media_links[0])
                if settings.send_errors == "True":
                    send_normal_webhook(error_msg, settings.error_webhook)

    settings.logger.debug(f"Avatar URL: {avatar_url}")

    embed.set_author(
        icon_url=avatar_url,
        name=screen_name,
        url=f"https://twitter.com/i/web/status/{tweet_id}",
    )

    # Add embed to webhook.
    hook.add_embed(embed)

    response: requests.Response = hook.execute()
    if response.ok:
        settings.logger.info(f"Webhook posted for tweet https://twitter.com/i/web/status/{tweet_id}")
        settings.logger.debug(f"Webhook response: {response!r}")
    else:
        settings.logger.error(f"Got {response.status_code!r} from {webhook!r}")
        settings.logger.error(f"Response: {response.text!r}")
        if settings.send_errors == "True":
            send_normal_webhook(f"Got {response.status_code!r} from {webhook!r}", settings.error_webhook)


def send_normal_webhook(msg: str, webhook: str = settings.webhook_url):
    """Send normal message to Discord webhook.

    Args:
        msg: Message to send
        webhook: Webhook URL. Defaults to environment variable WEBHOOK_URL.
    """
    settings.logger.debug(f"send_normal_webhook() - Message: {msg}")
    settings.logger.debug(f"send_normal_webhook() - Webhook URL: {webhook}")

    if not webhook:
        settings.logger.error("No webhook URL found")
        if settings.send_errors == "True":
            send_normal_webhook(f"No webhook URL found. Trying to send {msg!r}", settings.error_webhook)
        return

    hook = DiscordWebhook(url=webhook, content=msg)

    response: requests.Response = hook.execute()
    if response.ok:
        settings.logger.debug(f"Webhook response: {response!r}")
    else:
        settings.logger.error(f"Got {response.status_code!r} from {webhook!r}")
        settings.logger.error(f"Response: {response.text!r}")
        if settings.send_errors == "True":
            send_normal_webhook(f"Got {response.status_code!r} from {webhook!r}", settings.error_webhook)
