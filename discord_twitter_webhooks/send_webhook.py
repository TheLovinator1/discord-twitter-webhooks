import tempfile
from pathlib import Path
from random import randint

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook
from loguru import logger

from discord_twitter_webhooks import settings


def customize_footer(embed: DiscordEmbed) -> DiscordEmbed:
    """Customize the webhook footer."""
    footer_icon: str = settings.webhook_footer_icon
    footer_text: str = settings.webhook_footer_text

    if footer_icon and footer_text:
        embed.set_footer(icon_url=footer_icon, text=footer_text)
    elif footer_icon:
        embed.set_footer(icon_url=footer_icon)
    elif footer_text:
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
    embed: DiscordEmbed = DiscordEmbed(description=text, url=tweet_url)

    if not webhook:
        send_error_webhook(f"No webhook URL found. Tried to send tweet embed for {tweet_id}")
        return

    if twitter_card_image:
        # TODO: Add support for local images.
        # TODO: Add support for changing the height and width of the image.
        embed.set_image(url=twitter_card_image)

    image_embeds: list[DiscordEmbed] = create_image_embeds(media_links=media_links, tweet_url=tweet_url)

    avatar_url = settings.webhook_author_icon or avatar_url
    display_name = settings.webhook_author_name or display_name
    tweet_url = settings.webhook_author_url or tweet_url

    # If we should use a custom image.
    if webhook_image := settings.webhook_image:
        # TODO: Add support for local images.
        embed.set_image(url=webhook_image)

    # If we should use a custom thumbnail.
    if thumbnail := settings.webhook_thumbnail:
        # TODO: Add support for local images.
        # TODO: Add support for changing the height and width of the image.
        embed.set_thumbnail(url=thumbnail)

    # If we should show the timestamp. Defaults to True.
    if settings.webhook_show_timestamp:
        embed.set_timestamp()

    # If the user has customized the footer, we will use that instead of the default which is nothing.
    embed = customize_footer(embed)

    if settings.use_title:
        # TODO: Truncate title if it's too long.
        embed.set_title(f"{display_name} (@{username})")

    if settings.use_author:
        # TODO: Truncate author if it's too long.
        # TODO: Add support for local images.
        embed.set_author(f"{display_name} (@{username})", url=tweet_url, icon_url=avatar_url)

    # Set the color of the embed.
    set_color(embed)

    # Add embed to image_embeds as the first element.
    image_embeds.insert(0, embed)

    # TODO: Check if embed is working before adding it to the webhook.
    if image_embeds:
        hook: DiscordWebhook = DiscordWebhook(url="", rate_limit_retry=True, embeds=image_embeds)  # type: ignore
    else:
        hook: DiscordWebhook = DiscordWebhook(url="", rate_limit_retry=True)

    # Split the webhook URL into a list if it contains multiple webhooks.
    webhook_list: list[str] = webhook.split(",")
    for _webhook in webhook_list:
        logger.debug("Webhook URL: {}", _webhook)
        hook.url = _webhook
        response: requests.Response = hook.execute()

        if response.ok:
            logger.info("Webhook posted for tweet https://twitter.com/i/status/{}", tweet_id)
        else:
            send_error_webhook(f"Got {response.status_code} from {webhook}. Response: {response.text}")


def create_image_embeds(
    media_links: list[str],
    tweet_url: str,
) -> list[DiscordEmbed]:
    """Create a list of embeds with the images.

    Args:
        media_links: List of media links from the tweet.
        tweet_url: URL to the tweet.

    Returns:
        A list of embeds with the images.
    """
    embed_list: list[DiscordEmbed] = []
    for media_link in media_links:
        embed = DiscordEmbed(url=tweet_url)
        embed.set_image(url=media_link)
        embed_list.append(embed)
    return embed_list


def set_color(embed: DiscordEmbed) -> None:
    """Set the color of the embed.

    Args:
        embed: The embed to set the color of.
    """
    twitter_blue = "#1DA1F2"
    if webhook_embed_color := settings.webhook_embed_color:
        hex_color_length: int = 7  # 6 hex characters + 1 for the #
        if len(webhook_embed_color) == hex_color_length and webhook_embed_color[0] == "#":
            embed_color: str = webhook_embed_color
        else:
            logger.error("Invalid webhook embed color {}. Using default color.", webhook_embed_color)
            embed_color: str = twitter_blue
    elif settings.webhook_randomize_embed_color:
        embed_color = hex(randint(0, 16777215))[2:]  # noqa: S311
    else:
        embed_color: str = twitter_blue

    # Convert hex color to int.
    embed.set_color(int(embed_color[1:], 16))


def send_normal_webhook(msg: str, webhook: str, files: list[str] | None = None) -> None:
    """Send normal message to Discord webhook.

    Args:
        msg: Message to send
        webhook: Webhook URL. Defaults to environment variable WEBHOOK_URL.
        files: List of files to send.
    """
    _send_webhook(message=msg, webhook=webhook, func_name="send_normal_webhook()", files=files)


def _send_webhook(message: str, webhook: str, func_name: str, files: list[str] | None = None) -> None:
    """Send the webhook to Discord.

    Args:
        message: Message to send
        webhook: Webhook URL.
        func_name: Name of the function that called this function. Used for logging.
        files: List of files to send.
    """
    logger.debug("{} - Message: {}", func_name, message)
    logger.debug("{} - Webhook URL: {}", func_name, webhook)

    if not webhook:
        send_error_webhook(f"No webhook URL found. Trying to send {message}")
        return

    webhook_list: list[str] = webhook.split(",")
    for _webhook in webhook_list:
        logger.debug("Webhook URL: {}", _webhook)
        hook: DiscordWebhook = DiscordWebhook(url=_webhook, content=message, rate_limit_retry=True)

        if files:
            for file in files:
                with Path.open(Path(file), "rb") as f:
                    hook.add_file(file=f.read(), filename=Path(file).name)

        response: requests.Response = hook.execute()
        if not response.ok:
            send_error_webhook(f"Got {response.status_code} from {webhook}, response: {response.text}")


def send_error_webhook(msg: str, webhook: str = settings.error_webhook) -> None:
    """Send error message to Discord webhook.

    Args:
        msg: Message to send
        webhook: Webhook URL. Defaults to environment variable ERROR_WEBHOOK.
    """
    # TODO: Split webhook into multiple webhooks if it contains multiple webhooks.
    logger.error("Got an error: {}", msg)

    if settings.send_errors == "True":
        _send_webhook(message=msg, webhook=webhook, func_name="send_error_webhook()")
    else:
        logger.debug("Tried to send error webhook but send_errors is not set to True")


def send_hook_and_files(media_links: list[str], msg: str, webhook_url: str, user_info) -> None:
    """Send the webhook and check if we should upload images.

    Args:
        media_links: A list of media links.
        msg: The message to send.
        webhook_url: The webhook URL to send the message to.
        user_info: The user info.
    """
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    images: list[str] = []
    if settings.upload_images:
        # Download the images from the tweet and upload them to Discord.
        images, temp_dir = download_images(media_links)

    # If we should append the username to the message.
    if settings.append_username:
        msg += f"\n@{user_info.username}"

    # If we should append the image links to the message.
    if settings.append_image_links:
        for media_link in media_links:
            msg += f"\n{media_link}"

    send_normal_webhook(msg=msg, webhook=webhook_url, files=images)

    if temp_dir:
        temp_dir.cleanup()


def download_images(media_links: list[str]) -> tuple[list[str], tempfile.TemporaryDirectory[str]]:
    """Download the images from the tweet.

    The temporary directory is returned so we can delete it after we have uploaded the images to Discord.

    Args:
        media_links: A list of media links.

    Returns:
        A tuple of a list of images and a temporary directory.
    """
    temp_dir = tempfile.TemporaryDirectory()

    # Add the images to a list so we can upload them to Discord.
    images: list[str] = []
    for media_link in media_links:
        res: requests.Response = requests.get(url=media_link, stream=True, timeout=5)
        if res.ok:
            with Path.open(Path(f"{temp_dir.name}/{media_link.split('/')[-1]}"), "wb") as f:
                for chunk in res.iter_content(1024):
                    f.write(chunk)
                images.append(f"{temp_dir.name}/{media_link.split('/')[-1]}")
        else:
            logger.error("Failed to download image: {}", media_link)
    return images, temp_dir
