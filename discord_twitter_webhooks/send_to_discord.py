import re
from functools import lru_cache
from random import randint
from typing import TYPE_CHECKING

import requests
from defusedxml import ElementTree
from discord_webhook import DiscordEmbed, DiscordWebhook
from loguru import logger
from reader import Entry, Reader
from reader.types import EntryLike
from requests import request

from discord_twitter_webhooks._dataclasses import Group, get_group
from discord_twitter_webhooks.tweet_text import get_tweet_text

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from requests import Response


def send_webhook(webhook: DiscordWebhook, entry: Entry | EntryLike, group: Group) -> None:
    """Send a webhook to Discord.

    Args:
        webhook: The webhook to send.
        entry: The entry to send.
        group: The settings to use.
    """
    for _webhook in group.webhooks:
        logger.debug("Webhook URL: {}", _webhook)
        webhook.url = _webhook
        response: Response = webhook.execute()

        if response.ok:
            logger.info("Webhook posted for {}", entry.link)
        else:
            logger.error(f"Got {response.status_code} from {webhook}. Response: {response.text}")


def send_text(entry: Entry | EntryLike, group: Group) -> None:
    """Send text to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    # TODO: Append images to the end of the text
    # TODO: Append username before the text
    # TODO: Remove the Discord embeds to hashtags and @s
    webhook = DiscordWebhook(url="")
    tweet_text = get_tweet_text(entry, group)
    if not tweet_text:
        logger.debug("No text for {}", entry.link)
        tweet_text = "*No text*"

    # Send the tweet text to Discord
    webhook.content = tweet_text

    # Convert the text to a link if the user wants to
    if group.send_as_text_link:
        entry_link = group.send_as_text_link_url or entry.link
        webhook.content = f"[{tweet_text}]({entry_link})"  # TODO: Double check me when Twitter works again

    send_webhook(webhook, entry, group)


@lru_cache(maxsize=128)
def get_avatar(rss_feed: str) -> str:
    """Get the avatar of the embed.

    Returns:
        The avatar of the embed as an int.
    """
    default_avatar: str = "https://pbs.twimg.com/profile_images/1354479643882004483/Btnfm47p_400x400.jpg"
    # Go to the RSS feed and get the avatar
    try:
        response: Response = request("GET", rss_feed, timeout=5)
    except requests.exceptions.ReadTimeout as e:
        logger.error("Read timeout for {} - {}", rss_feed, e)
        return default_avatar

    if not response.ok:
        logger.error(f"Got {response.status_code} from {rss_feed}. Response: {response.text}")
        return default_avatar

    # Parse XML and get the avatar
    xml_data: str = response.content.decode("utf-8")

    try:
        root: Element = ElementTree.fromstring(xml_data)
        found: Element | None = root.find("channel/image/url")
    except ElementTree.ParseError:
        logger.error("Unable to parse XML from {}", rss_feed)
        return default_avatar

    return found.text or default_avatar if found is not None else default_avatar


def create_image_embeds(entry: Entry | EntryLike) -> list[DiscordEmbed]:
    """Get the images from the entry and create embeds from them.

    We can unofficially have up to 4 images in an embed.
    https://github.com/lovvskillz/python-discord-webhook/issues/126

    Args:
        entry: The entry to get the images from.

    Returns:
        A list of embeds.
    """
    embeds: list[DiscordEmbed] = []
    entry_summary: str = str(entry.summary) or ""
    urls = re.findall('src="(https?://[^"]+)"', entry_summary)

    if not urls:
        logger.debug("No images found in {}", entry.link or "entry.link is None")
        return embeds

    logger.debug("Found {} images in {}", len(urls), entry.link or "entry.link is None")
    for i in range(1, min(len(urls), 4) + 1):
        embed = DiscordEmbed(url=entry.link)
        embed.set_image(url=urls[i - 1])
        embeds.append(embed)
        logger.debug("Added image {} to embeds", i)

    logger.debug("We have {} embeds", len(embeds))
    return embeds


def send_embed(entry: Entry | EntryLike, group: Group) -> None:
    """Send an embed to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    tweet_text: str = get_tweet_text(entry, group)
    embed = DiscordEmbed(description=tweet_text, url=entry.link)

    entry_author = group.embed_author_name or entry.author
    author_avatar = group.embed_author_icon_url or get_avatar(entry.feed_url)

    # Show the tweeter as a title of the embed
    if group.embed_show_title:
        embed.set_title(entry_author)

    # Add an author to the embed, is name of tweeter and a small image of the avatar
    if group.embed_show_author:
        embed.set_author(name=entry_author, url=entry.link, icon_url=author_avatar)

    # Show a timestamp at the bottom of the embed
    if group.embed_timestamp:
        embed.set_timestamp()

    # Embed color
    embed_color: str = group.embed_color
    if group.embed_color == "random":
        embed_color = hex(randint(0, 16777215))[2:]  # noqa: S311
    embed.set_color(embed_color.lstrip("#"))

    if embeds := create_image_embeds(entry):
        # Only do this if more than one image is found
        if len(embeds) > 1:
            embeds.insert(0, embed)
            webhook = DiscordWebhook(url=entry.link, embeds=embeds, rate_limit_retry=True)  # type: ignore  # noqa: PGH003, E501
        else:
            if embeds[0].image:
                image = embeds[0].image
                embed.set_image(image["url"])
            webhook = DiscordWebhook(url=entry.link, rate_limit_retry=True)
            webhook.add_embed(embed)
    else:
        webhook = DiscordWebhook(url="", rate_limit_retry=True)
        webhook.add_embed(embed)

    send_webhook(webhook, entry, group)


def send_link(entry: Entry | EntryLike, group: Group) -> None:
    """Send a link to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    # TODO: Change webhook username to the tweeter so we can see who posted it?
    # TODO: Append username and action (tweeted, retweeted, liked) to the webhook username or content?
    # TODO: Add support for changing the Nitter link to the original Twitter link
    what_to_send = f"{entry.link}"
    if not group.send_as_link_preview:
        what_to_send = f"<{entry.link}>"

    send_webhook(DiscordWebhook(url="", content=what_to_send), entry, group)


def send_to_discord(reader: Reader) -> None:
    """Send all new entries to Discord.

    This is called by the scheduler every 5 minutes. It will check for new entries and send them to Discord.

    Args:
        reader: The reader which contains the entries.
    """
    reader.update_feeds()

    # Loop through the unread (unsent) entries.
    entries = list(reader.get_entries(read=False))

    if not entries:
        logger.info("No new entries found.")
        return

    entry: Entry | EntryLike
    for entry in entries:
        for _group in reader.get_tag((), "groups", []):
            group = get_group(reader, str(_group))
            for feeds in group.rss_feeds:
                if entry.feed_url == feeds:
                    if group.send_as_link:
                        send_link(entry=entry, group=group)
                    if group.send_as_text:
                        send_text(entry=entry, group=group)
                    if group.send_as_embed:
                        send_embed(entry=entry, group=group)

                    # Mark the entry as read (sent)
                    reader.mark_entry_as_read(entry)
