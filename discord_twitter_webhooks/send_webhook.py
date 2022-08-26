""" Discord webhook stuff

send_embed_webhook - Send an embed to Discord webhook.
send_normal_webhook - Send a normal message to Discord webhook. We use this for sending errors.
"""
import json

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook

from discord_twitter_webhooks import settings


def customize_footer(embed: DiscordEmbed):
    """Customize the webhook footer."""
    footer_icon = settings.webhook_footer_icon
    footer_text = settings.webhook_footer_text

    if footer_icon and footer_text:
        settings.logger.debug(f"User has customized the footer icon: {footer_icon} and footer text: {footer_text}")
        embed.set_footer(icon_url=footer_icon, text=footer_text)

    elif footer_icon:
        settings.logger.debug(f"User has customized the footer icon: {footer_icon}")
        embed.set_footer(icon_url=footer_icon)

    elif footer_text:
        settings.logger.debug(f"User has customized the footer text: {footer_text}")
        embed.set_footer(text=footer_text)
    return embed


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
    tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"

    settings.logger.debug(f"send_normal_webhook() - Tweet ID: {tweet_id}")
    settings.logger.debug(f"send_normal_webhook() - Text: {text}")
    settings.logger.debug(f"send_normal_webhook() - Twitter card image: {twitter_card_image}")
    settings.logger.debug(f"send_normal_webhook() - Avatar URL: {avatar_url}")
    settings.logger.debug(f"send_normal_webhook() - Screen name: {screen_name}")
    settings.logger.debug(f"send_normal_webhook() - Webhook URL: {webhook}")
    settings.logger.debug(f"send_normal_webhook() - Tweet URL: {tweet_url}")
    for media_link in media_links:
        settings.logger.debug(f"send_normal_webhook() - Media link: {media_link}")

    if not webhook:
        settings.logger.error("No webhook URL found")
        send_error_webhook(f"No webhook URL found. Trying to send tweet embed for {tweet_id}")
        return

    hook = DiscordWebhook(url=webhook, rate_limit_retry=True)
    embed = DiscordEmbed(description=text)

    if twitter_card_image:
        embed.set_image(url=twitter_card_image)

    # Get image to add to the Discord embed.
    embed_image = get_embed_image(media_links, tweet_id)
    if embed_image:
        embed.set_image(url=embed_image)

    if settings.webhook_author_icon:
        settings.logger.debug(f"User has customized the author icon: {settings.webhook_author_icon}")
        avatar_url = settings.webhook_author_icon

    if settings.webhook_author_name:
        settings.logger.debug(f"User has customized the author name: {settings.webhook_author_name}")
        screen_name = settings.webhook_author_name

    if settings.webhook_author_url:
        settings.logger.debug(f"User has customized the author url: {settings.webhook_author_url}")
        tweet_url = settings.webhook_author_url

    embed.set_author(
        icon_url=avatar_url,
        name=screen_name,
        url=tweet_url,
    )

    webhook_image = settings.webhook_image
    if webhook_image:
        settings.logger.debug(f"User has customized the embedded image: {webhook_image}")
        embed.set_image(url=webhook_image)

    thumbnail = settings.webhook_thumbnail
    if thumbnail:
        settings.logger.debug(f"User has customized the thumbnail: {thumbnail}")
        embed.set_thumbnail(url=thumbnail)

    embed = customize_footer(embed)

    # Add embed to webhook.
    hook.add_embed(embed)

    response: requests.Response = hook.execute()
    if response.ok:
        settings.logger.info(f"Webhook posted for tweet https://twitter.com/i/web/status/{tweet_id}")
        settings.logger.debug(f"Webhook response: {response!r}")
    else:
        settings.logger.error(f"Got {response.status_code!r} from {webhook!r}")
        settings.logger.error(f"Response: {response.text!r}")
        send_error_webhook(f"Got {response.status_code!r} from {webhook!r}")


def get_embed_image(media_links, tweet_id) -> str:
    """Get the image that will be in the Discord embed.

    Args:
        media_links: List of media links from the tweet. This is used to add the images to the embed.
        tweet_id: Tweet ID of the tweet. This is used to link to the tweet on Twitter.

    Returns:
        The image that will be in the Discord embed.
    """
    embed_image = ""

    settings.logger.debug(f"get_embed_image() - media_links {media_links!r}")
    if len(media_links):
        if len(media_links) == 1:
            embed_image = media_links[0]

        elif len(media_links) > 1:
            # Send images to twitter-image-collage-maker
            # (e.g https://twitter.lovinator.space/) and get a collage back.
            response = requests.get(url=settings.collage_maker_url, params={"tweet_id": tweet_id})

            if response.ok:
                json_data = json.loads(response.text)
                settings.logger.debug(f"JSON data from twitter-image-collage-maker: {json_data}")
                embed_image = json_data["url"]

                # Check if image exists
                if_exists = requests.head(url=embed_image)
                if if_exists.ok:
                    settings.logger.debug(f"Image {embed_image!r} exists")
                else:
                    settings.logger.error(f"Image {embed_image!r} does not exist")
                    send_error_webhook(f"Image {embed_image!r} does not exist, but that is the URL we got from "
                                       f"{settings.collage_maker_url}. It looks like the collage maker is broken.")
                    embed_image = media_links[0]
            else:
                error_msg = f"Got {response.status_code!r} from {settings.collage_maker_url!r} for tweet {tweet_id!r}"
                settings.logger.error(error_msg)
                embed_image = media_links[0]
                send_error_webhook(error_msg)

    return embed_image


def send_normal_webhook(msg: str, webhook: str):
    """Send normal message to Discord webhook.

    Args:
        msg: Message to send
        webhook: Webhook URL. Defaults to environment variable WEBHOOK_URL.
    """
    _send_webhook(message=msg, webhook=webhook, func_name="send_normal_webhook()")


def _send_webhook(message: str, webhook: str, func_name: str):
    """Send the webhook to Discord.

    Args:
        message: Message to send
        webhook: Webhook URL.
        func_name: Name of the function that called this function. Used for logging.
    """
    settings.logger.debug(f"{func_name} - Message: {message}")
    settings.logger.debug(f"{func_name} - Webhook URL: {webhook}")

    if not webhook:
        settings.logger.error("No webhook URL found")
        send_error_webhook(f"No webhook URL found. Trying to send {message!r}")
        return

    hook = DiscordWebhook(url=webhook, content=message, rate_limit_retry=True)
    response: requests.Response = hook.execute()
    if response.ok:
        settings.logger.debug(f"Webhook response: {response!r}")
    else:
        settings.logger.error(f"Got {response.status_code!r} from {webhook!r}")
        settings.logger.error(f"Response: {response.text!r}")
        send_error_webhook(f"Got {response.status_code!r} from {webhook!r}")


def send_error_webhook(msg: str, webhook: str = settings.error_webhook):
    """Send error message to Discord webhook.

    Args:
        msg: Message to send
        webhook: Webhook URL. Defaults to environment variable ERROR_WEBHOOK.
    """
    settings.logger.error(f"Got an error: {msg}")

    if settings.send_errors == "True":
        _send_webhook(message=msg, webhook=webhook, func_name="send_error_webhook()")
    else:
        settings.logger.debug("Tried to send error webhook but send_errors is not set to True")
