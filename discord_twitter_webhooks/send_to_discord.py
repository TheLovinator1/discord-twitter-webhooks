import re
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, cast
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup, Tag
from defusedxml import ElementTree
from discord_webhook import DiscordEmbed, DiscordWebhook
from loguru import logger
from moviepy.editor import VideoFileClip
from reader import Entry, Reader
from reader.types import EntryLike
from requests import request

from discord_twitter_webhooks._dataclasses import Group, get_app_settings, get_group
from discord_twitter_webhooks.reader_settings import get_reader
from discord_twitter_webhooks.tweet_text import convert_html_to_md, get_tweet_text
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


def get_entry_link(entry: Entry, group: Group) -> str:
    """Get the link to the entry.

    Args:
        entry (Entry): The entry to get the link for.
        group (Group): The settings to use. We use this to know if the link is to Twitter or Nitter.

    Returns:
        str: The link to the entry.
    """
    entry_link: str = entry.link or "#"
    if group.link_destination == "Twitter":
        entry_link = entry_link.replace(get_app_settings(get_reader()).nitter_instance, "https://twitter.com")
        entry_link = entry_link.rstrip("#m")
    return entry_link


def apply_video_to_embed(entry: Entry, embed: DiscordEmbed, webhook: DiscordWebhook):  # noqa: ANN201
    """Download and convert the video to a gif and add it to the embed.

    Only images and gifs are supported by Discord embeds.

    Args:
        entry (Entry): Get the HTML from the RSS feed.
        embed (DiscordEmbed): The embed to add the video to.
        webhook (DiscordWebhook): The webhook to add the video to.

    Returns:
        tempfile.NamedTemporaryFile: The temporary file the video was
        downloaded to. This is used to delete the file after it's uploaded.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    entry_summary: str = entry.summary or ""
    if not entry_summary:
        return temp_file

    # Download and convert the video to a gif and add it to the embed
    soup: BeautifulSoup = BeautifulSoup(entry_summary, features="lxml")
    if source := soup.find("source", attrs={"type": "video/mp4"}):
        # Download the mp4
        if not hasattr(source, "src"):
            logger.error("No src found for {}. Entry: {}", entry.feed_url, entry)
            return temp_file

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

    return temp_file


def send_embed(entry: Entry, group: Group) -> None:
    """Send an embed to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    entry_link: str = get_entry_link(entry, group)
    tweet_text: str = get_tweet_text(entry, group)
    embed = DiscordEmbed(description=tweet_text, url=entry_link)

    name_username: list[str] = ["Failed to", "get username"]
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
            webhook = DiscordWebhook(url=entry_link, embeds=embeds, rate_limit_retry=True)
        else:
            if embeds[0].image:
                image = embeds[0].image
                embed.set_image(str(image["url"]))
            webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
            webhook.add_embed(embed)
    else:
        webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
        webhook.add_embed(embed)

    temp_file = apply_video_to_embed(entry, embed, webhook)
    send_webhook(webhook, entry, group)

    # Remove our temporary files
    if temp_file and Path.exists(Path(temp_file.name)):
        temp_file.close()
        Path.unlink(Path(temp_file.name))


def send_embed_reply(entry: Entry, group: Group) -> None:
    """Send an embed to Discord.

    Args:
        entry: The entry to send.
        group: The settings to use.
    """
    # Check if tweet is a reply
    reply = None
    if entry.title and entry.title.startswith("R to "):
        reply: ReplyTweet | None = get_reply_from_nitter(entry)

    entry_link: str = get_entry_link(entry, group)
    tweet_text: str = get_tweet_text(entry, group)
    embed = DiscordEmbed(url=entry_link)

    name_username: list[str] = ["Failed to", "get username"]
    if entry.feed.title:
        name_username: list[str] = entry.feed.title.split(" / @")

    # Set the timestamp to when the tweet was tweeted
    if entry.published:
        timestamp: float = entry.published.timestamp() or datetime.now(tz=timezone.utc).timestamp()
        embed.set_timestamp(timestamp=timestamp)

    embed.set_color("1DA1F2")
    embed.set_footer(text="Twitter", icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")

    if not reply:
        logger.error("No reply found for {}. Entry: {}", entry.feed_url, entry)
        send_embed(entry, group)
        reader: Reader = get_reader()
        reader.mark_entry_as_read(entry)
        return

    embed.set_author(name=reply.username, url=entry_link, icon_url=reply.avatar)
    embed.set_description(reply.text)
    embed.add_embed_field(name=f"Reply from @{name_username[1]}", value=tweet_text, inline=False)

    if not entry.summary:
        logger.error("No summary found for {}. Entry: {}", entry.feed_url, entry)
        return

    if embeds := create_image_embeds(entry.summary, entry_link):
        # Only do this if more than one image is found
        if len(embeds) > 1:
            embeds.insert(0, embed)
            webhook = DiscordWebhook(url=entry_link, embeds=embeds, rate_limit_retry=True)
        else:
            if embeds[0].image:
                image = embeds[0].image
                embed.set_image(str(image["url"]))
            webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
            webhook.add_embed(embed)
    else:
        webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
        webhook.add_embed(embed)

    temp_file = apply_video_to_embed(entry, embed, webhook)
    send_webhook(webhook, entry, group)

    # Remove our temporary files
    if temp_file and Path.exists(Path(temp_file.name)):
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


def if_entry_above_is_too_old(entry: Entry | EntryLike, reader: Reader) -> bool:
    """Check if the entry above is too old.

    Args:
        entry: The entry to check.
        reader: The reader which contains the entries.

    Returns:
        True if the entry above is too old, False otherwise.
    """
    # Cast entry to Entry instead of EntryLike
    entry = cast(Entry, entry)

    # Get the entries for that feed
    entries = list(reader.get_entries(feed=entry.feed))

    # Remove every retweet that is not the original tweet
    for _entry in entries:
        # If it is our entry, skip it
        if _entry.id == entry.id:
            continue

        if not hasattr(_entry, "title") or not _entry.title:
            logger.error("No title found for {}. Entry: {}", _entry.feed_url, _entry)
            continue

        if _entry.title.startswith("RT by "):
            entries.remove(_entry)

    # Get our entry index
    entry_index: int = entries.index(entry)
    logger.debug(f"Entry {entry.id} is at index {entry_index}.")

    # Check if the entry is the first entry
    if entry_index == 0:
        logger.debug(f"Entry {entry.id} is the first entry, checking it the next entry is too old.")
        return False

    # The tweet above
    tweet_above: Entry = entries[entry_index - 1]

    # Check if the entry above has a published date
    if not hasattr(tweet_above, "published") or not tweet_above.published:
        logger.error("No published date or title found for {}. Entry: {}", tweet_above.feed_url, tweet_above)
        return True

    # Check if the entry above is too old
    tweet_age_in_hours: float = (time.time() - tweet_above.published.timestamp()) / 3600
    if tweet_age_in_hours > get_app_settings(reader).max_age_hours:
        logger.debug("The tweet above is older than the max age so our retweet is also too old.")
        return True

    logger.debug(f"The entry above {entry.id} is not too old, so we need to check the entry below")
    return False


def if_below_is_young(entry: Entry | EntryLike, reader: Reader) -> bool:
    """If the entry below is young enough.

    Args:
        entry: The entry to check.
        reader: The reader which contains the entries.

    Returns:
        True if the entry below is young enough, False otherwise.
    """
    # Cast entry to Entry instead of EntryLike
    entry = cast(Entry, entry)

    # Get the entries for that feed
    entries = list(reader.get_entries(feed=entry.feed))

    # Get our entry index
    try:
        entry_index: int = entries.index(entry)
    except ValueError:
        logger.error("Entry {} not found in entries.", entry.id)
        return False

    # The tweet below
    tweet_below: Entry = entries[entry_index + 1]

    # Check if the entry below has a published date
    if not hasattr(tweet_below, "published") or not tweet_below.published:
        logger.error("No published date or title found for {}. Entry: {}", tweet_below.feed_url, tweet_below)
        return False

    # Check if the entry below is younger than the max age
    tweet_age_in_hours: float = (time.time() - tweet_below.published.timestamp()) / 3600
    if tweet_age_in_hours < get_app_settings(reader).max_age_hours:
        logger.debug(
            "Entry below is younger than the max age, so the entry above is probably younger than the max age too.",
        )
        reader.mark_entry_as_read(tweet_below)
        return True

    return False


def too_old(entry: Entry | EntryLike, reader: Reader) -> bool:
    """Check if the entry is too old.

    Args:
        entry: The entry to check.
        reader: The reader which contains the entries.

    Returns:
        True if the entry is too old, False otherwise.
    """
    entry = cast(Entry, entry)
    entry_title: str = entry.title or ""

    if not hasattr(entry, "published") or not entry.published or not entry_title:
        logger.error("No published date or title found for {}. Entry: {}", entry.feed_url, entry)
        reader.mark_entry_as_read(entry)
        return False

    if entry_title.startswith("RT by "):
        return check_if_retweet_is_too_old(reader, entry)

    # Check if the entry is older than the max age
    tweet_age_in_hours: float = (time.time() - entry.published.timestamp()) / 3600
    if entry.published and tweet_age_in_hours > get_app_settings(reader).max_age_hours:
        logger.info(f"Entry {entry.id} is older than {get_app_settings(reader).max_age_hours} hours")
        reader.mark_entry_as_read(entry)
        return True

    reader.mark_entry_as_read(entry)
    return False


def check_if_retweet_is_too_old(reader: Reader, entry: Entry) -> bool:
    """Check if the retweet is too old.

    Args:
        reader: The reader which contains the entries.
        entry: The entry to check.

    Returns:
        True if the retweet is too old, False otherwise.
    """
    above_too_old: bool = if_entry_above_is_too_old(entry, reader)
    if above_too_old:
        # The tweet above is too old, so this tweet is probably too old too
        reader.mark_entry_as_read(entry)
        return True

    below_is_young: bool = if_below_is_young(entry, reader)
    if below_is_young:
        # If the tweet before this one is not too old, then this tweet is probably not too old either
        reader.mark_entry_as_read(entry)
        return False

    logger.debug("Entry {} is a retweet, but the tweet above and below are not too old.", entry.id)
    return False


def mark_new_feed_as_read(reader: Reader) -> None:
    """Mark all entries from new feeds as read.

    Args:
        reader: The reader which contains the entries.
    """
    # Loop through the new feeds and mark all entries as read
    for feed in reader.get_feeds(new=True):
        reader.update_feed(feed)
        logger.info(f"Found a new feed: {feed.url}, added {feed.added}")
        for entry in reader.get_entries(feed=feed):
            reader.mark_entry_as_read(entry)
            logger.info(f"Marked {entry.link} as unread because it's from a new feed")


@dataclass
class ReplyTweet:
    """A reply tweet."""

    text: str
    username: str
    fullname: str
    avatar: str


def get_reply_from_nitter(entry: Entry) -> ReplyTweet | None:
    """Get the reply from Nitter.

    Args:
        entry: The entry to check.
        group: The settings to use.

    Returns:
        The reply if found, an empty string otherwise.
    """
    entry_link: str = entry.link or ""
    if not entry_link:
        logger.error("No link found for {}. Entry: {}", entry.feed_url, entry)
        return None

    response: Response = requests.get(entry_link, timeout=10)
    if not response.ok:
        logger.error("Could not get {} from Nitter. Status code: {}", entry_link, response.status_code)
        return None

    soup = BeautifulSoup(response.text, features="lxml")

    tweet_text = ""
    if tweet_content := soup.find("div", class_="tweet-content"):
        tweet_text: str = tweet_content.get_text()

    avatar_url = ""
    if avatar_tag := soup.find("img", class_="avatar"):
        avatar_tag = cast(Tag, avatar_tag)
        avatar_url: str = avatar_tag.attrs["src"]

        # Replace /pic/ with https://pbs.twimg.com/
        avatar_url = avatar_url.replace("/pic/", "https://pbs.twimg.com/")

        # Decode the URL
        avatar_url = unquote(avatar_url)

        # Replace _bigger.jpg with .jpg
        avatar_url = avatar_url.replace("_bigger.jpg", ".jpg")

    username = ""
    if username_tag := soup.find("a", class_="username"):
        username: str = username_tag.get_text(strip=True)

    fullname = ""
    if fullname_tag := soup.find("a", class_="fullname"):
        fullname: str = fullname_tag.get_text(strip=True)

    return ReplyTweet(text=tweet_text, username=username, fullname=fullname, avatar=avatar_url)


def check_if_quoted_tweet(entry: Entry) -> bool:
    """Check if the entry is a quoted tweet.

    Args:
        entry: The entry to check.

    Returns:
        True if the entry is a quoted tweet, False otherwise.
    """
    # Check if tweet ends with a link to the original tweet
    entry_summary: str = entry.summary or ""
    group = Group(link_destination="Nitter")
    entry_summary = convert_html_to_md(entry_summary, group)

    entry_link: str = entry.link or ""

    if not entry_summary:
        return False

    lines: list[str] = entry_summary.splitlines()
    if not lines:
        logger.error("No lines found for {}. Entry: {}", entry.feed_url, entry)
        return False

    last_line: str = lines[-1]

    # Check if last_line starts with our Nitter instance and ends with #m
    reader: Reader = get_reader()
    nitter_instance: str = get_app_settings(reader).nitter_instance
    nitter_instance = nitter_instance.replace("https://", "[")

    if not last_line.startswith(nitter_instance) or not last_line.endswith("#m>)"):
        return False

    if not entry_link:
        logger.error("No link found for {}. Entry: {}", entry.feed_url, entry)
        return False

    response: Response = requests.get(entry_link, timeout=10)
    if not response.ok:
        logger.error("Could not get {} from Nitter. Status code: {}", entry_link, response.status_code)
        return False

    soup = BeautifulSoup(response.text, features="lxml")

    # Check if the entry is a quoted tweet
    return bool(soup.find("div", class_="quote"))


@dataclass
class QuotedTweet:
    """A quoted tweet."""

    text: str
    username: str
    fullname: str
    avatar: str


def get_quoted_tweet(entry: Entry) -> QuotedTweet | None:
    """Get the quoted tweet.

    Args:
        entry: The entry to check.

    Returns:
        The quoted tweet if found, None otherwise.
    """
    entry_link: str = entry.link or ""
    if not entry_link:
        logger.error("No link found for {}. Entry: {}", entry.feed_url, entry)
        return None

    response: Response = requests.get(entry_link, timeout=10)
    if not response.ok:
        logger.error("Could not get {} from Nitter. Status code: {}", entry_link, response.status_code)
        return None

    soup = BeautifulSoup(response.text, features="lxml")

    tweet_text = ""
    if quote_text := soup.find("div", class_="quote-text"):
        tweet_text: str = quote_text.get_text()

    avatar_url = ""
    if avatar_tag := soup.find("img", class_="avatar"):
        avatar_tag = cast(Tag, avatar_tag)
        avatar_url: str = avatar_tag.attrs["src"]

        # Replace /pic/ with https://pbs.twimg.com/
        avatar_url = avatar_url.replace("/pic/", "https://pbs.twimg.com/")

        # Decode the URL
        avatar_url = unquote(avatar_url)

        # Replace _bigger.jpg with .jpg
        avatar_url = avatar_url.replace("_bigger.jpg", ".jpg")

    username = ""
    if username_tag := soup.find("a", class_="username"):
        username: str = username_tag.get_text(strip=True)

    fullname = ""
    if fullname_tag := soup.find("a", class_="fullname"):
        fullname: str = fullname_tag.get_text(strip=True)

    return QuotedTweet(text=tweet_text, username=username, fullname=fullname, avatar=avatar_url)


def send_embed_quoted_tweet(entry: Entry, group: Group) -> None:
    """Send an embed for a quoted tweet.

    Args:
        entry: The entry to send.
        group: The group to send the entry to.
    """
    # Check if tweet is a reply
    quote = None
    if entry.title:
        quote: QuotedTweet | None = get_quoted_tweet(entry)

    entry_link: str = get_entry_link(entry, group)
    tweet_text: str = get_tweet_text(entry, group)
    # Remove the last line from the tweet text
    tweet_text = "\n".join(tweet_text.splitlines()[:-1])

    embed = DiscordEmbed(url=entry_link)

    name_username: list[str] = ["Failed to", "get username"]
    if entry.feed.title:
        name_username: list[str] = entry.feed.title.split(" / @")

    # Set the timestamp to when the tweet was tweeted
    if entry.published:
        timestamp: float = entry.published.timestamp() or datetime.now(tz=timezone.utc).timestamp()
        embed.set_timestamp(timestamp=timestamp)

    embed.set_color("1DA1F2")
    embed.set_footer(text="Twitter", icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")

    if not quote:
        logger.error("No quote found for {}. Entry: {}", entry.feed_url, entry)
        send_embed(entry, group)
        reader: Reader = get_reader()
        reader.mark_entry_as_read(entry)
        return

    embed.set_author(name=quote.username, url=entry_link, icon_url=quote.avatar)
    embed.set_description(quote.text)
    embed.add_embed_field(name=f"Reply from @{name_username[1]}", value=tweet_text, inline=False)

    if not entry.summary:
        logger.error("No summary found for {}. Entry: {}", entry.feed_url, entry)
        return

    if embeds := create_image_embeds(entry.summary, entry_link):
        # Only do this if more than one image is found
        if len(embeds) > 1:
            embeds.insert(0, embed)
            webhook = DiscordWebhook(url=entry_link, embeds=embeds, rate_limit_retry=True)
        else:
            if embeds[0].image:
                image = embeds[0].image
                embed.set_image(str(image["url"]))
            webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
            webhook.add_embed(embed)
    else:
        webhook = DiscordWebhook(url=entry_link, rate_limit_retry=True)
        webhook.add_embed(embed)

    temp_file = apply_video_to_embed(entry, embed, webhook)
    send_webhook(webhook, entry, group)

    # Remove our temporary files
    if temp_file and Path.exists(Path(temp_file.name)):
        temp_file.close()
        Path.unlink(Path(temp_file.name))


def send_to_discord(reader: Reader) -> None:  # noqa: C901, PLR0912
    """Send all new entries to Discord.

    This is called by the scheduler every 15 minutes. It will check for new entries and send them to Discord.

    Args:
        reader: The reader which contains the entries.
    """
    # Mark newly added feeds as read so we don't send old entries
    mark_new_feed_as_read(reader)

    # Get the new entries from the RSS feeds
    reader.update_feeds(workers=4)

    # Loop through the unread (unsent) entries.
    unread_entries = list(reader.get_entries(read=False))
    if not unread_entries:
        logger.info("No new entries found")
        return

    entry: Entry | EntryLike
    for entry in unread_entries:
        # Check if the tweet is too old
        if too_old(entry, reader):
            logger.info(f"Skipping entry {entry.link} as it is too old, it was published {entry.published}")
            reader.mark_entry_as_read(entry)
            continue

        for _group in list(reader.get_tag((), "groups", [])):
            group: Group = get_group(reader, str(_group))
            for feed in group.rss_feeds:
                # Loop through the RSS feeds that the group has and check if the entry is from one of them.
                if entry.feed_url == feed:
                    tweet_text: str = entry.title or ""

                    if group.whitelist_enabled and not whitelisted(group, entry):
                        logger.info(f"Skipping entry {entry.link} as it is not whitelisted")
                        reader.mark_entry_as_read(entry)
                        continue

                    if group.blacklist_enabled and blacklisted(group, entry):
                        logger.info(f"Skipping entry {entry.link} as it is blacklisted")
                        reader.mark_entry_as_read(entry)
                        continue

                    if not group.send_retweets and tweet_text.startswith("RT by "):
                        logger.info(f"Skipping entry {entry.link} as it is a retweet")
                        reader.mark_entry_as_read(entry)
                        continue

                    if not group.send_replies and tweet_text.startswith("R to "):
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
                        if tweet_text.startswith("R to "):
                            send_embed_reply(entry=entry, group=group)
                        elif check_if_quoted_tweet(entry):
                            send_embed_quoted_tweet(entry=entry, group=group)
                        else:
                            send_embed(entry=entry, group=group)

                    # Mark the entry as read (sent)
                    reader.mark_entry_as_read(entry)
