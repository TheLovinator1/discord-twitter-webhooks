import re
from html import unescape

from bs4 import BeautifulSoup
from reader import Entry

from discord_twitter_webhooks._dataclasses import Group
from translate import translate_html


def convert_html_to_md(html: str) -> str:
    """Convert HTML to markdown.

    Args:
        html: The HTML to convert.

    Returns:
        Our markdown.
    """
    soup: BeautifulSoup = BeautifulSoup(html, features="lxml")

    for bold in soup.find_all("b") + soup.find_all("strong"):
        bold.replace_with(f"**{bold.text}**")

    for italic in soup.find_all("i") + soup.find_all("em"):
        italic.replace_with(f"*{italic.text}*")

    for blockquote in soup.find_all("blockquote") + soup.find_all("q"):
        blockquote.replace_with(f">>> {blockquote.text}")

    for code in soup.find_all("code") + soup.find_all("pre"):
        code.replace_with(f"`{code.text}`")

    for image in soup.find_all("img"):
        image.decompose()

    for link in soup.find_all("a") + soup.find_all("link"):
        if not link.get_text().strip():
            link.decompose()
        else:
            link_text: str = link.text or link.get("href")
            link.replace_with(f"[{link_text}]({link.get('href')})")

    for strikethrough in soup.find_all("s") + soup.find_all("del") + soup.find_all("strike"):
        strikethrough.replace_with(f"~~{strikethrough.text}~~")

    for br in soup.find_all("br"):
        br.replace_with("\n")

    clean_soup: BeautifulSoup = BeautifulSoup(str(soup).replace("</p>", "</p>\n"), features="lxml")

    # Remove all other tags
    for tag in clean_soup.find_all(True):
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
    # TODO: Replace Nitter links with Twitter links, add group.use_nitter_links to the group settings or something.
    # TODO: We should replace "<p><a href="https://nitter.lovinator.space/User/status/1234#m">nitter.lovinator.space/User/status/1234#m</a></p>"
    #  in entry.summary with the text from the tweet if it is a retweet or quote tweet.

    # entry.summary has text and HTML tags, entry.title has only text
    tweet_text: str = entry.summary or entry.title or f"Failed to get tweet text for <{entry.link}>"

    # Translate the tweet text
    if group.translate:
        # TODO: Maybe send the original text as a field or something?
        tweet_text = translate_html(tweet_text, group.translate_from, group.translate_to)

    tweet_text = convert_html_to_md(tweet_text)

    if group.remove_copyright:
        # Copyright symbols are bloat and adds nothing.
        tweet_text = tweet_text.replace("©", "")
        tweet_text = tweet_text.replace("®", "")
        tweet_text = tweet_text.replace("™", "")
    if group.remove_utm:
        # Remove the utm_source parameter from the url. https://en.wikipedia.org/wiki/UTM_parameters
        tweet_text = re.sub(r"([?&])utm_source=[^&]*", "", tweet_text)
        tweet_text = re.sub(r"([?&])utm_campaign=[^&]*", "", tweet_text)
        tweet_text = re.sub(r"([?&])utm_medium=[^&]*", "", tweet_text)
        tweet_text = re.sub(r"([?&])utm_term=[^&]*", "", tweet_text)
        tweet_text = re.sub(r"([?&])utm_content=[^&]*", "", tweet_text)
    if group.unescape_html:
        # Convert HTML entities to their corresponding characters. For example, "&amp;" becomes "&".
        tweet_text = unescape(tweet_text)

    return tweet_text
