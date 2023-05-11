from html import unescape

from reader import Entry

from discord_twitter_webhooks.dataclasses import Settings
from discord_twitter_webhooks.remove_copyright import remove_copyright
from discord_twitter_webhooks.remove_utm import remove_utm
from discord_twitter_webhooks.set_settings.markdown import convert_html_to_md


def get_tweet_text(entry: Entry, settings: Settings) -> str:
    """Get the text to send in the embed.

    Args:
        entry: The entry to send.
        settings: The settings to use.
        reader: The reader to use.

    Returns:
        The text to send in the embed.
    """
    tweet_text: str = entry.summary or "Failed to get tweet text"
    tweet_text = convert_html_to_md(tweet_text)

    if settings.remove_copyright:
        tweet_text = remove_copyright(tweet_text)
    if settings.remove_utm:
        tweet_text = remove_utm(tweet_text)
    if settings.unescape_html:
        tweet_text = unescape(tweet_text)

    return tweet_text
