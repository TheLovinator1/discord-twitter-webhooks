import re
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from bs4 import BeautifulSoup
from defusedxml import ElementTree
from discord_webhook import DiscordEmbed, DiscordWebhook
from loguru import logger
from moviepy.editor import VideoFileClip
from reader import Entry, Reader
from reader.types import EntryLike
from requests import request

from discord_twitter_webhooks._dataclasses import Group, get_app_settings, get_group
from discord_twitter_webhooks.reader_settings import get_reader
from discord_twitter_webhooks.tweet_text import get_tweet_text
from discord_twitter_webhooks.whitelist import check_word_in_string_regex

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
    webhook = DiscordWebhook(url="")
    tweet_text = get_tweet_text(entry, group)
    if not tweet_text:
        logger.debug("No text for {}", entry.link)
        tweet_text = "*Tweet has no text.*"

    entry_link = entry.link
    if group.link_destination == "Twitter":
        entry_link = entry_link.replace(get_app_settings(get_reader()).nitter_instance, "https://twitter.com")
        entry_link = entry_link.rstrip("#m")

    action = "tweeted"
    if entry.title.startswith("RT by "):
        action = "retweeted"
    elif entry.title.startswith("R to "):
        # TODO: Add the username of the person they replied to
        replied_to = re.search(r"R to @(\w+)", entry.title)
        action = f"replied to {replied_to.group(1)}"

    if group.send_as_text_username:
        tweet_text = f"[{entry.author}](<{entry_link}>) {action}:\n{tweet_text}"

    # Send the tweet text to Discord
    webhook.content = tweet_text

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


def create_image_embeds(entry_summary: str, entry_link: str) -> list[DiscordEmbed]:
    """Get the images from the entry and create embeds from them.

    We can unofficially have up to 4 images in an embed.
    https://github.com/lovvskillz/python-discord-webhook/issues/126

    Args:
        entry_summary: The tweet text from the RSS feed. This is HTML.
        entry_link: The link to the entry.

    Returns:
        A list of embeds.
    """
    if not entry_summary:
        return []

    embeds: list[DiscordEmbed] = []
    urls = re.findall('src="(https?://[^"]+)"', entry_summary)

    if not urls:
        return embeds

    for i in range(1, min(len(urls), 4) + 1):
        embed = DiscordEmbed(url=entry_link)
        embed.set_image(url=urls[i - 1])
        embeds.append(embed)

    return embeds


def send_embed(entry: Entry | EntryLike, group: Group) -> None:
    """Send an embed to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    tweet_text: str = get_tweet_text(entry, group)
    embed = DiscordEmbed(description=tweet_text, url=entry.link)
    name_username = entry.feed.title.split(" / @")

    entry_author = f"{name_username[0]} (@{name_username[1]})"
    author_avatar = get_avatar(entry.feed_url)

    # Replace Nitter links with Twitter links
    entry_link = entry.link
    if group.link_destination == "Twitter":
        entry_link = entry_link.replace(get_app_settings(get_reader()).nitter_instance, "https://twitter.com")
        entry_link = entry_link.rstrip("#m")

    embed.set_author(name=entry_author, url=entry_link, icon_url=author_avatar)
    embed.set_timestamp(timestamp=entry.published.timestamp())
    embed.set_color("1DA1F2")
    embed.set_footer(text="Twitter", icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")

    if embeds := create_image_embeds(entry.summary, entry_link):
        # Only do this if more than one image is found
        if len(embeds) > 1:
            embeds.insert(0, embed)
            webhook = DiscordWebhook(url=entry_link, embeds=embeds, rate_limit_retry=True)  # type: ignore  # noqa: PGH003, E501
        else:
            if embeds[0].image:
                image = embeds[0].image
                embed.set_image(image["url"])
            webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
            webhook.add_embed(embed)
    else:
        webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
        webhook.add_embed(embed)

    # Send a link to the mp4 if it's a video or gif
    soup: BeautifulSoup = BeautifulSoup(entry.summary, features="lxml")
    source = soup.find("source", attrs={"type": "video/mp4"})
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    if source:
        # Download the mp4
        response: Response = request("GET", source["src"], timeout=5)
        if response.ok:
            with Path.open(Path(temp_file.name), "wb") as f:
                f.write(response.content)

                # Convert the mp4 to a gif
                VideoFileClip(temp_file.name).write_gif(temp_file.name.replace(".mp4", ".gif"))

                # Add the gif to the webhook
                with Path.open(Path(temp_file.name.replace(".mp4", ".gif")), "rb") as g:
                    webhook.add_file(file=g.read(), filename="video.gif")
                embed.set_image(url="attachment://video.gif")

    send_webhook(webhook, entry, group)

    # Remove our temporary files
    if Path.exists(Path(temp_file.name)):
        temp_file.close()
        Path.unlink(Path(temp_file.name))


def send_link(entry: Entry | EntryLike, group: Group) -> None:
    """Send a link to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    # TODO: Change webhook username to the tweeter so we can see who posted it?
    # TODO: Append username and action (tweeted, retweeted, liked) to the webhook username or content?

    # Replace Nitter links with Twitter links
    entry_link = entry.link
    if group.link_destination == "Twitter":
        entry_link = entry_link.replace(get_app_settings(get_reader()).nitter_instance, "https://twitter.com")
        entry_link = entry_link.rstrip("#m")

    send_webhook(DiscordWebhook(url="", content=f"{entry_link}"), entry, group)


def has_media(entry: Entry | EntryLike) -> bool:
    """Check if the entry has media.

    Args:
        entry: The entry to check.

    Returns:
        True if the entry has media, False otherwise.
    """
    soup: BeautifulSoup = BeautifulSoup(entry.summary, features="lxml")
    video_files = bool(soup.find("source", attrs={"type": "video/mp4"}))
    images = bool(soup.find("img"))
    return video_files or images


def whitelisted(group: Group, entry: Entry | EntryLike) -> bool:
    """Check if the entry is whitelisted.

    Args:
        group: The group to check.
        entry: The entry to check.

    Returns:
        True if the entry is whitelisted, False otherwise.
    """
    for word in group.whitelist:
        if word.lower() in entry.title.lower():
            return True

    return any(check_word_in_string_regex(entry.title, regex_pattern) for regex_pattern in group.whitelist_regex)


def blacklisted(group: Group, entry: Entry | EntryLike) -> bool:
    """Check if the entry is blacklisted.

    Args:
        group: The group to check.
        entry: The entry to check.

    Returns:
        True if the entry is blacklisted, False otherwise.
    """
    for word in group.blacklist:
        if word.lower() in entry.title.lower():
            return True

    return any(check_word_in_string_regex(entry.title, regex_pattern) for regex_pattern in group.blacklist_regex)


def send_to_discord(reader: Reader) -> None:  # noqa: C901, PLR0912
    """Send all new entries to Discord.

    This is called by the scheduler every 15 minutes. It will check for new entries and send them to Discord.

    Args:
        reader: The reader which contains the entries.
    """
    reader.update_feeds(workers=4)

    # Loop through the unread (unsent) entries.
    entries = list(reader.get_entries(read=False))

    if not entries:
        logger.info("No new entries found.")
        return

    entry: Entry | EntryLike
    for entry in entries:
        # Don't send tweets that are older than the oldest tweet we have
        the_oldest_tweet = reader.get_entries(read=True)

        if not the_oldest_tweet:
            # Related: https://github.com/TheLovinator1/discord-twitter-webhooks/issues/132
            # Get and mark every entry as read
            _entry: Entry | EntryLike
            for _entry in reader.get_entries(read=False):
                reader.mark_entry_as_read(_entry)
            continue

        # Sort the tweets by date
        the_oldest_tweet = sorted(the_oldest_tweet, key=lambda x: x.published)

        # Check if the entry is older than the oldest tweet we have
        if entry.published < the_oldest_tweet[-1].published:
            # Related: https://github.com/TheLovinator1/discord-twitter-webhooks/issues/129#issuecomment-1646086754
            logger.info("Skipping entry {} as it is older than the oldest tweet we have", entry)
            reader.mark_entry_as_read(entry)
            continue

        for _group in reader.get_tag((), "groups", []):
            group = get_group(reader, str(_group))
            if not group:
                logger.error("Group {} not found", _group)
                continue

            for feeds in group.rss_feeds:
                if group.whitelist_enabled and not whitelisted(group, entry):
                    logger.info(f"Skipping entry {entry} as it is not whitelisted")
                    reader.mark_entry_as_read(entry)
                    continue

                if group.blacklist_enabled and blacklisted(group, entry):
                    logger.info(f"Skipping entry {entry} as it is blacklisted")
                    reader.mark_entry_as_read(entry)
                    continue

                if not group.send_retweets and entry.title.startswith("RT by "):
                    logger.info(f"Skipping entry {entry} as it is a retweet")
                    reader.mark_entry_as_read(entry)
                    continue

                if not group.send_replies and entry.title.startswith("R to "):
                    logger.info(f"Skipping entry {entry} as it is a reply")
                    reader.mark_entry_as_read(entry)
                    continue

                if group.only_send_if_media and not has_media(entry):
                    logger.info(f"Skipping entry {entry} as it has no media attached")
                    reader.mark_entry_as_read(entry)
                    continue

                if entry.feed_url == feeds:
                    if group.send_as_link:
                        send_link(entry=entry, group=group)
                    if group.send_as_text:
                        send_text(entry=entry, group=group)
                    if group.send_as_embed:
                        send_embed(entry=entry, group=group)

                    # Mark the entry as read (sent)
                    reader.mark_entry_as_read(entry)
