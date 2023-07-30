from html import unescape

from bs4 import BeautifulSoup
from loguru import logger
from reader import Entry

from discord_twitter_webhooks._dataclasses import Group, get_app_settings
from discord_twitter_webhooks.reader_settings import get_reader
from discord_twitter_webhooks.translate import translate_html


def convert_html_to_md(html: str, group: Group) -> str:
    """Convert HTML to markdown.

    Args:
        html: The HTML to convert.
        group: The group to get settings from.

    Returns:
        Our markdown.
    """
    soup: BeautifulSoup = BeautifulSoup(html, features="lxml")

    # Used for photos, videos, gifs and tweet cards
    image: BeautifulSoup
    for image in soup.find_all("img"):
        image.decompose()

    for link in soup.find_all("a") + soup.find_all("link"):
        link: BeautifulSoup
        if not link.get_text().strip():
            link.decompose()
        else:
            # TODO: This breaks for https://nitter.lovinator.space/Steam/status/1679694708761669634#m
            #  and https://nitter.lovinator.space/SteamDB/status/1677217359487021056#m

            # Replace Nitter links with Twitter links
            if group.link_destination == "Twitter":
                if link.text.startswith("#") and hasattr(link, "href"):
                    link["href"] = f"https://twitter.com/hashtag/{link.text[1:]}"
                elif link.text.startswith("@") and hasattr(link, "href"):
                    link["href"] = f"https://twitter.com/{link.text[1:]}"

            # Remove the link preview
            link.replace_with(f"[{link.text}](<{link.get('href')}>)")

    clean_soup: BeautifulSoup = BeautifulSoup(str(soup).replace("</p>", "</p>\n"), features="lxml")

    # Remove all other tags
    tag: BeautifulSoup
    for tag in clean_soup.find_all():
        tag.replace_with(tag.text)

    return clean_soup.text.strip()


def get_tweet_text(entry: Entry, group: Group) -> str:
    """Get the text to send in the embed.

    Args:
        entry: The entry to send.
        group: The settings to use.

    Returns:
        The text to send in the embed.
    """
    # TODO: We should replace "<p><a href="https://nitter.lovinator.space/User/status/1234#m">nitter.lovinator.space/User/status/1234#m</a></p>" # noqa: E501
    #  in entry.summary with the text from the tweet if it is a retweet or quote tweet.

    # entry.summary has text and HTML tags, entry.title has only text
    tweet_text: str = entry.summary or entry.title or f"Failed to get tweet text for <{entry.link}>"

    # You can tweet without text if you have an image or video attached
    if not tweet_text:
        logger.warning("Tweet has no text: {}", entry.link)
        return "*Tweet has no text.*"

    # Translate the tweet text
    if group.translate:
        # TODO: Maybe send the original text as a field or something?
        tweet_text = translate_html(tweet_text, group.translate_from, group.translate_to)

    # Convert HTML to markdown
    tweet_text = convert_html_to_md(tweet_text, group)

    # Teddit/Libreddit
    teddit_instance: str = get_app_settings(get_reader()).teddit_instance
    if not group.replace_reddit:
        tweet_text = tweet_text.replace("https://teddit.net", "https://reddit.com")
        tweet_text = tweet_text.replace("[teddit.net", "[reddit.com")
    if group.replace_reddit:
        tweet_text = tweet_text.replace("https://reddit.com", teddit_instance)
        tweet_text = tweet_text.replace("https://teddit.net", teddit_instance)

    # Piped/Invidious
    piped_instance: str = get_app_settings(get_reader()).piped_instance
    if not group.replace_youtube:
        tweet_text = tweet_text.replace("https://piped.video", "https://youtube.com")
        tweet_text = tweet_text.replace("[piped.video", "[youtube.com")
    if group.replace_youtube:
        tweet_text = tweet_text.replace("https://youtube.com", piped_instance)
        tweet_text = tweet_text.replace("https://piped.video", piped_instance)

    # Copyright symbols are bloat and adds nothing.
    if group.remove_copyright:
        tweet_text = tweet_text.replace("©", "")
        tweet_text = tweet_text.replace("®", "")
        tweet_text = tweet_text.replace("™", "")

    # Convert HTML entities to their corresponding characters. For example, "&amp;" becomes "&".
    if group.unescape_html:
        tweet_text = unescape(tweet_text)

    return tweet_text
