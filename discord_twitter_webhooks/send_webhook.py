import json

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook

from discord_twitter_webhooks import settings


def customize_footer(embed: DiscordEmbed) -> DiscordEmbed:
    """Customize the webhook footer."""
    footer_icon: str = settings.webhook_footer_icon
    footer_text: str = settings.webhook_footer_text

    if footer_icon and footer_text:
        settings.logger.debug(
            "User has customized the footer icon: %s and footer text: %s" % (footer_icon, footer_text),
        )
        embed.set_footer(icon_url=footer_icon, text=footer_text)

    elif footer_icon:
        settings.logger.debug("User has customized the footer icon: %s", footer_icon)
        embed.set_footer(icon_url=footer_icon)

    elif footer_text:
        settings.logger.debug("User has customized the footer text: %s", footer_text)
        embed.set_footer(text=footer_text)
    return embed


def send_embed_webhook(
    tweet_id: int,
    media_links: list[str],
    text: str,
    twitter_card_image: str,
    avatar_url: str,
    display_name: str,
    webhook: str,
    username: str,
) -> None:
    """Send an embed to Discord webhook.

    Args:
        avatar_url: Avatar URL of the user. Will be used as the avatar for the embed.
        display_name: Display name of the user. Will be used as the name for the embed.
        tweet_id: Tweet ID of the tweet. This is used to link to the tweet on Twitter.
        media_links: List of media links from the tweet. This is used to add the images to the embed.
        text: Text from the tweet to send in the embed.
        webhook: Webhook URL. Defaults to environment variable WEBHOOK_URL.
        twitter_card_image: Twitter card image from the tweet.
        username: Username of the user.
    """
    tweet_url: str = f"https://twitter.com/{username}/status/{tweet_id}"

    settings.logger.debug("send_normal_webhook() - Tweet ID: %s", tweet_id)
    settings.logger.debug("send_normal_webhook() - Text: %s", text)
    settings.logger.debug("send_normal_webhook() - Twitter card image: %s", twitter_card_image)
    settings.logger.debug("send_normal_webhook() - Avatar URL: %s", avatar_url)
    settings.logger.debug("send_normal_webhook() - Screen name: %s", display_name)
    settings.logger.debug("send_normal_webhook() - Webhook URL: %s", webhook)
    settings.logger.debug("send_normal_webhook() - Tweet URL: %s", tweet_url)
    for _media_link in media_links:
        settings.logger.debug("send_normal_webhook() - Media link: %s", _media_link)

    if not webhook:
        settings.logger.error("No webhook URL found")
        send_error_webhook(f"No webhook URL found. Trying to send tweet embed for {tweet_id}")
        return

    # We will add the webhook when we send it. This is so we can have several webhooks for each tweet.
    hook: DiscordWebhook = DiscordWebhook(url="", rate_limit_retry=True)
    embed: DiscordEmbed = DiscordEmbed(description=text)

    if twitter_card_image:
        embed.set_image(url=twitter_card_image)

    if embed_image := get_embed_image(media_links, tweet_id):
        embed.set_image(url=embed_image)

    if settings.webhook_author_icon:
        settings.logger.debug("User has customized the author icon: %s", settings.webhook_author_icon)
        avatar_url = settings.webhook_author_icon

    if settings.webhook_author_name:
        settings.logger.debug("User has customized the author name: %s", settings.webhook_author_name)
        display_name = settings.webhook_author_name

    if settings.webhook_author_url:
        settings.logger.debug("User has customized the author url: %s", settings.webhook_author_url)
        tweet_url = settings.webhook_author_url

    if webhook_image := settings.webhook_image:
        settings.logger.debug("User has customized the embedded image: %s", webhook_image)
        embed.set_image(url=webhook_image)

    if thumbnail := settings.webhook_thumbnail:
        settings.logger.debug("User has customized the thumbnail: %s", thumbnail)
        embed.set_thumbnail(url=thumbnail)

    if show_timestamp := settings.webhook_show_timestamp:
        settings.logger.debug("User has customized the timestamp: %s", show_timestamp)
        embed.set_timestamp()

    # If the user has customized the footer, we will use that instead of the default which is nothing.
    embed = customize_footer(embed)

    if settings.use_title:
        embed.set_title(display_name)

    if settings.use_author.lower() == "true":
        # Show the tweeters display name, username and avatar on top of the embed. This defaults to True.
        embed.set_author(f"{display_name} (@{username})", url=tweet_url, icon_url=avatar_url)

    # Add embed to webhook.
    hook.add_embed(embed)

    # Split the webhook URL into a list if it contains multiple webhooks.
    webhook_list: list[str] = webhook.split(",")
    for _webhook in webhook_list:
        settings.logger.debug("Webhook URL: %s", _webhook)
        hook.url = _webhook
        response: requests.Response = hook.execute()

        if response.ok:
            settings.logger.info("Webhook posted for tweet https://twitter.com/i/status/%s", tweet_id)
            settings.logger.debug("Webhook response: %s", response.text)
        else:
            settings.logger.error("Got %s from %s" % (response.status_code, webhook))
            settings.logger.error("Response: %s", response.text)
            send_error_webhook(f"Got {response.status_code} from {webhook}")


def get_embed_image(media_links, tweet_id) -> str:
    """Get the image that will be in the Discord embed.

    Args:
        media_links: List of media links from the tweet. This is used to add the images to the embed.
        tweet_id: Tweet ID of the tweet. This is used to link to the tweet on Twitter.

    Returns:
        The image that will be in the Discord embed.
    """
    embed_image: str = ""

    settings.logger.debug("get_embed_image() - media_links %s", media_links)
    if len(media_links):
        if len(media_links) == 1:
            embed_image = media_links[0]

        elif len(media_links) > 1:
            # Send images to twitter-image-collage-maker
            # (e.g https://twitter.lovinator.space/) and get a collage back.
            response: requests.Response = requests.get(
                url=settings.collage_maker_url,
                params={"tweet_id": tweet_id},
                timeout=5,
            )

            if response.ok:
                json_data = json.loads(response.text)
                settings.logger.debug("JSON data from twitter-image-collage-maker: %s", json_data)
                embed_image = json_data["url"]

                # Check if image exists
                if_exists: requests.Response = requests.head(url=embed_image, timeout=5)
                if if_exists.ok:
                    settings.logger.debug("Image %s exists", embed_image)
                else:
                    settings.logger.error("Image %s does not exist", embed_image)
                    send_error_webhook(
                        (
                            f"Image {embed_image} does not exist, but that is the URL we got from "
                            f"{settings.collage_maker_url}. It looks like the collage maker is broken."
                        ),
                    )
                    embed_image = media_links[0]
            else:
                error_msg: str = f"Got {response.status_code} from {settings.collage_maker_url} for tweet {tweet_id}"
                settings.logger.error(error_msg)
                embed_image = media_links[0]
                send_error_webhook(error_msg)

    return embed_image


def send_normal_webhook(msg: str, webhook: str) -> None:
    """Send normal message to Discord webhook.

    Args:
        msg: Message to send
        webhook: Webhook URL. Defaults to environment variable WEBHOOK_URL.
    """
    _send_webhook(message=msg, webhook=webhook, func_name="send_normal_webhook()")


def _send_webhook(message: str, webhook: str, func_name: str) -> None:
    """Send the webhook to Discord.

    Args:
        message: Message to send
        webhook: Webhook URL.
        func_name: Name of the function that called this function. Used for logging.
    """
    settings.logger.debug("%s - Message: %s" % (func_name, message))
    settings.logger.debug("%s - Webhook URL: %s" % (func_name, webhook))

    if not webhook:
        settings.logger.error("No webhook URL found")
        send_error_webhook(f"No webhook URL found. Trying to send {message}")
        return

    webhook_list: list[str] = webhook.split(",")
    for _webhook in webhook_list:
        settings.logger.debug("Webhook URL: %s", _webhook)
        hook: DiscordWebhook = DiscordWebhook(url=_webhook, content=message, rate_limit_retry=True)

        response: requests.Response = hook.execute()
        if response.ok:
            settings.logger.debug("Webhook response: %s", response.text)
        else:
            settings.logger.error("Got %s from %s" % (response.status_code, webhook))
            settings.logger.error("Response: %s" % response.text)
            send_error_webhook(f"Got {response.status_code} from {webhook}")


def send_error_webhook(msg: str, webhook: str = settings.error_webhook) -> None:
    """Send error message to Discord webhook.

    Args:
        msg: Message to send
        webhook: Webhook URL. Defaults to environment variable ERROR_WEBHOOK.
    """
    # TODO: Split webhook into multiple webhooks if it contains multiple webhooks.
    settings.logger.error("Got an error: %s", msg)

    if settings.send_errors == "True":
        _send_webhook(message=msg, webhook=webhook, func_name="send_error_webhook()")
    else:
        settings.logger.debug("Tried to send error webhook but send_errors is not set to True")
