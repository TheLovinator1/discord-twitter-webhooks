import re
import tempfile
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, cast

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
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


def send_webhook(webhook: DiscordWebhook, entry: Entry, group: Group) -> str:
    """Send a webhook to Discord.

    Args:
        webhook: The webhook to send.
        entry: The entry to send.
        group: The settings to use.

    Returns:
        The response from Discord. Used for testing.
    """
    logger.debug("Webhook: {}", webhook)
    for _webhook in group.webhooks:
        logger.debug("Webhook URL: {}", _webhook)
        webhook.url = _webhook
        response: Response = webhook.execute()

        if response.ok:
            logger.info("Webhook posted for {}", entry.title)
        else:
            logger.error(f"Got {response.status_code} from {webhook}. Response: {response.text}")
    return str(webhook.content)


def send_text(entry: Entry, group: Group) -> str:
    """Send text to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.

    Returns:
        The text sent to Discord. Used for testing.
    """
    # TODO: Append images to the end of the text
    webhook = DiscordWebhook(url="")

    entry_link: str = entry.link or "#"
    if group.link_destination == "Twitter":
        entry_link = entry_link.replace(get_app_settings(get_reader()).nitter_instance, "https://twitter.com")
        entry_link = entry_link.rstrip("#m")

    tweet_text: str = get_tweet_text(entry, group)
    if group.send_as_text_username:
        # Append the username to the start of the tweet text
        # action is either tweeted, retweeted or replied to
        action: str = get_action(entry)
        tweet_text = f"[{entry.author}](<{entry_link}>) {action}:\n{tweet_text}"

    # Send the tweet text to Discord
    webhook.content = tweet_text

    send_webhook(webhook, entry, group)

    return tweet_text


def get_action(entry: Entry) -> str:
    """Get the action the user did.

    This is either tweeted, retweeted or replied to.

    Args:
        entry: The entry to send.

    Returns:
        The action the user did.
    """
    action: str = "tweeted"

    if not hasattr(entry, "title"):
        return action

    if not entry.title:
        return action

    if entry.title.startswith("RT by "):
        action = "retweeted"
    elif entry.title.startswith("R to ") and (replied_to := re.search(r"R to @(\w+)", entry.title)):
        action = f"replied to {replied_to[1]}"
    return action


@lru_cache(maxsize=128)
def get_avatar(rss_feed: str) -> str:
    """Get the avatar of the embed.

    Returns:
        The avatar of the embed as an image URL.
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


def send_embed(entry: Entry, group: Group) -> None:  # noqa: C901, PLR0915, PLR0912
    """Send an embed to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    # Replace Nitter links with Twitter links
    entry_link: str = entry.link or "#"
    if group.link_destination == "Twitter":
        entry_link = entry_link.replace(get_app_settings(get_reader()).nitter_instance, "https://twitter.com")
        entry_link = entry_link.rstrip("#m")

    tweet_text: str = get_tweet_text(entry, group)
    embed = DiscordEmbed(description=tweet_text, url=entry_link)

    name_username: list[str] = ["Failed to", " get username"]
    if entry.feed.title:
        name_username: list[str] = entry.feed.title.split(" / @")

    entry_author: str = f"{name_username[0]} (@{name_username[1]})"
    author_avatar: str = get_avatar(entry.feed_url)

    embed.set_author(name=entry_author, url=entry_link, icon_url=author_avatar)

    # Set the timestamp to when the tweet was tweeted
    if entry.published:
        timestamp: float = entry.published.timestamp() or datetime.now(tz=timezone.utc).timestamp()
        embed.set_timestamp(timestamp=timestamp)

    embed.set_color("1DA1F2")
    embed.set_footer(text="Twitter", icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")

    if not entry.summary:
        logger.error("No summary found for {}. Entry: {}", entry.feed_url, entry)
        return

    if embeds := create_image_embeds(entry.summary, entry_link):
        # Only do this if more than one image is found
        if len(embeds) > 1:
            embeds.insert(0, embed)
            webhook = DiscordWebhook(url=entry_link, embeds=embeds, rate_limit_retry=True)  # type: ignore  # noqa: PGH003, E501
        else:
            if embeds[0].image:
                image = embeds[0].image
                embed.set_image(str(image["url"]))
            webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
            webhook.add_embed(embed)
    else:
        webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
        webhook.add_embed(embed)

    # Send a link to the mp4 if it's a video or gif
    soup: BeautifulSoup = BeautifulSoup(entry.summary, features="lxml")
    source: Tag | NavigableString | None = soup.find("source", attrs={"type": "video/mp4"})
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    if source:
        # Download the mp4
        if not hasattr(source, "src"):
            logger.error("No src found for {}. Entry: {}", entry.feed_url, entry)
            return

        source = cast(Tag, source)
        video_url: str | list[str] = source["src"]

        if isinstance(video_url, list):
            video_url = video_url[0]

        response: Response = request("GET", video_url, timeout=5)
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

    Todo:
        TODO: Change webhook username to the tweeter so we can see who posted it?
        TODO: Append username and action (tweeted, retweeted, liked) to the webhook username or content?

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    # entry is a EntryLike but Pylance would complain if it wasn't a Entry
    entry = cast(Entry, entry)

    # Replace Nitter links with Twitter links
    entry_link: str = entry.link or "#"
    if group.link_destination == "Twitter":
        entry_link = entry_link.replace(get_app_settings(get_reader()).nitter_instance, "https://twitter.com")

        # Nitter URLs end with #m, remove it
        entry_link = entry_link.rstrip("#m")

    send_webhook(DiscordWebhook(url="", content=f"{entry_link}"), entry, group)


def has_media(entry: Entry | EntryLike) -> bool:
    """Check if the entry has media.

    Args:
        entry: The entry to check.

    Returns:
        True if the entry has media, False otherwise.
    """
    # entry is a EntryLike but Pylance would complain if it wasn't a Entry
    entry = cast(Entry, entry)

    if not hasattr(entry, "summary"):
        logger.error("No summary found for {}. Entry: {}", entry.feed_url, entry)
        return False

    entry_summary: str = entry.summary or ""
    soup: BeautifulSoup = BeautifulSoup(entry_summary, features="lxml")
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
    # entry is a EntryLike but Pylance would complain if it wasn't a Entry
    entry = cast(Entry, entry)

    if not hasattr(entry, "title"):
        logger.error("No title found for {}. Entry: {}", entry.feed_url, entry)
        return False

    # Check if the entry title contains any of the whitelisted words
    entry_title: str = entry.title or ""
    for word in group.whitelist:
        if word.lower() in entry_title.lower():
            return True

    # Check if the entry title matches any of the whitelisted regex patterns
    return any(check_word_in_string_regex(entry_title, regex_pattern) for regex_pattern in group.whitelist_regex)


def blacklisted(group: Group, entry: Entry | EntryLike) -> bool:
    """Check if the entry is blacklisted.

    Args:
        group: The group to check.
        entry: The entry to check.

    Returns:
        True if the entry is blacklisted, False otherwise.
    """
    # entry is a EntryLike but Pylance would complain if it wasn't a Entry
    entry = cast(Entry, entry)

    if not hasattr(entry, "title"):
        logger.error("No title found for {}. Entry: {}", entry.feed_url, entry)
        return False

    # Check if the entry title contains any of the blacklisted words
    entry_title: str = entry.title or ""
    for word in group.blacklist:
        if word.lower() in entry_title.lower():
            return True

    # Check if the entry title matches any of the blacklisted regex patterns
    return any(check_word_in_string_regex(entry_title, regex_pattern) for regex_pattern in group.blacklist_regex)


def too_old(entry: Entry | EntryLike, reader: Reader) -> bool:
    """Check if the entry is too old.

    Args:
        entry: The entry to check.
        reader: The reader which contains the entries.

    Returns:
        True if the entry is too old, False otherwise.
    """
    # entry is a EntryLike but Pylance would complain if it wasn't a Entry
    entry = cast(Entry, entry)
    entry_title: str = entry.title or ""

    if not hasattr(entry, "published") or not entry.published or not entry_title:
        logger.error("No published date or title found for {}. Entry: {}", entry.feed_url, entry)
        reader.mark_entry_as_read(entry)
        return False

    if entry_title.startswith("RT by "):
        # Retweets have the original tweet date, so if somebody retweets
        # something old, it will be older than the max age.
        return False

    # Check if the entry is older than the max age
    tweet_age_in_hours: float = (time.time() - entry.published.timestamp()) / 3600
    if entry.published and tweet_age_in_hours > get_app_settings(reader).max_age_hours:
        logger.info(f"Entry {entry.title} is older than {get_app_settings(reader).max_age_hours} hours")
        reader.mark_entry_as_read(entry)
        return True

    reader.mark_entry_as_read(entry)
    return False


def send_to_discord(reader: Reader) -> None:  # noqa: C901, PLR0912
    """Send all new entries to Discord.

    This is called by the scheduler every 15 minutes. It will check for new entries and send them to Discord.

    Args:
        reader: The reader which contains the entries.
    """
    reader.update_feeds(workers=4)

    # Loop through the unread (unsent) entries.
    unread_entries = list(reader.get_entries(read=False))

    if not unread_entries:
        logger.info("No new entries found")
        return

    entry: Entry | EntryLike
    for entry in unread_entries:
        if not hasattr(entry, "published"):
            logger.error("No published date found for {}. Entry: {}", entry.feed_url, entry)
            continue

        if not entry.published:
            logger.error("No published date found for {}. Entry: {}", entry.feed_url, entry)
            continue

        if too_old(entry, reader):
            continue

        for _group in list(reader.get_tag((), "groups", [])):
            group: Group = get_group(reader, str(_group))
            if not group:
                logger.error("Group {} not found", _group)
                continue

            for feed in group.rss_feeds:
                # Loop through the RSS feeds that the group has and check if the entry is from one of them.
                if entry.feed_url == feed:
                    entry_title: str = entry.title or ""

                    if not entry_title:
                        logger.error("No title found for {}. Entry: {}", entry.feed_url, entry)
                        continue

                    if group.whitelist_enabled and not whitelisted(group, entry):
                        logger.info(f"Skipping entry {entry.link} as it is not whitelisted")
                        reader.mark_entry_as_read(entry)
                        continue

                    if group.blacklist_enabled and blacklisted(group, entry):
                        logger.info(f"Skipping entry {entry.link} as it is blacklisted")
                        reader.mark_entry_as_read(entry)
                        continue

                    if not group.send_retweets and entry_title.startswith("RT by "):
                        logger.info(f"Skipping entry {entry.link} as it is a retweet")
                        reader.mark_entry_as_read(entry)
                        continue

                    if not group.send_replies and entry_title.startswith("R to "):
                        logger.info(f"Skipping entry {entry.link} as it is a reply")
                        reader.mark_entry_as_read(entry)
                        continue

                    if group.only_send_if_media and not has_media(entry):
                        logger.info(f"Skipping entry {entry.link} as it has no media attached")
                        reader.mark_entry_as_read(entry)
                        continue

                    if group.send_as_link:
                        send_link(entry=entry, group=group)
                    if group.send_as_text:
                        send_text(entry=entry, group=group)
                    if group.send_as_embed:
                        send_embed(entry=entry, group=group)

                    # Mark the entry as read (sent)
                    reader.mark_entry_as_read(entry)
