import html

from tweepy import Stream

from discord_twitter_webhooks import get, reddit, remove, replace, settings
from discord_twitter_webhooks.send_embed_webhook import send_embed_webhook


def main(tweet) -> None:
    twitter_card_image = ""

    # Get the text from the tweet
    text = get.tweet_text(tweet)
    settings.logger.debug(f"Tweet: {text}")

    # Get the images from the tweet and remove the URLs from the text
    media_links, text_media_links = get.media_links_and_remove_url(tweet, text)
    settings.logger.debug(f"Media links: {media_links}")
    settings.logger.debug(f"Text media links: {text_media_links}")

    if urls_found := get.tweet_urls(tweet):
        twitter_card_image = get.meta_image(urls_found[0])
        settings.logger.debug(f"Twitter card image: {twitter_card_image}")

    # We coverts &gt; and &lt; to > and < to make the text look nicer
    text_unescaped = html.unescape(text_media_links)
    settings.logger.debug(f"Text unescaped: {text_unescaped}")

    # Replace Twitters shortened URLs with the original URL
    text_url_links = replace.tco_url_link_with_real_link(tweet, text_unescaped)
    settings.logger.debug(f"Text url links: {text_url_links}")

    # Replace the @mentions with URLs
    text_replace_username = replace.username_with_link(text_url_links)
    settings.logger.debug(f"Text replace username: {text_replace_username}")

    # Replace the #hashtags with URLs
    text_replace_hashtags = replace.hashtag_with_link(text_replace_username)
    settings.logger.debug(f"Text replace hashtags: {text_replace_hashtags}")

    # Append < and > to disable Discords link previews
    text_discord_preview = remove.discord_link_previews(text_replace_hashtags)
    settings.logger.debug(f"Text discord preview: {text_discord_preview}")

    # Change /r/subreddit to the subreddit URL
    text_subreddit_to_link = reddit.subreddit_to_link(text_discord_preview)
    settings.logger.debug(f"Text subreddit to link: {text_subreddit_to_link}")

    # Change /u/username to the user URL
    text_reddit_username_to_link = reddit.username_to_link(text_subreddit_to_link)  # noqa: E501, pylint: disable=line-too-long
    settings.logger.debug(f"Text reddit username to link: {text_reddit_username_to_link}")  # noqa: E501, pylint: disable=line-too-long

    # Remove UTM parameters, this cleans up the URL
    text_remove_utm_source = remove.utm_source(text_reddit_username_to_link)
    settings.logger.debug(f"Text remove utm source: {text_remove_utm_source}")

    # Remove trailing whitespace
    text_remove_whitespace = text_remove_utm_source.rstrip()
    settings.logger.debug(f"Text remove whitespace: {text_remove_whitespace}")

    # Remove copyright symbols
    text_remove_copyright = remove.copyright_symbols(text_remove_whitespace)
    settings.logger.debug(f"Text remove copyright: {text_remove_copyright}")

    send_embed_webhook(
        tweet=tweet,
        link_list=media_links,
        text=text_remove_copyright,
        twitter_card_image=twitter_card_image,
    )


class MyStreamListener(Stream):
    """https://docs.tweepy.org/en/latest/streaming.html

    Stream tweets in realtime.
    """

    def on_status(self, status) -> None:
        """This is called when a new tweet is received.

        Args:
            status ([type]): Twitter status
        """
        # Tweet is retweet
        if hasattr(status, "retweeted_status"):
            settings.logger.info("Tweet is retweet")
            retweeted_user = status.retweeted_status.user.id_str

            if retweeted_user in settings.user_list_retweeted_split:
                if status.user.id_str in settings.user_list_retweets_split:
                    settings.logger.info("Retweet is in user list")
                    main(tweet=status)

        elif status.in_reply_to_user_id is not None:
            if status.user.id_str in settings.user_list_replies_to_other_tweet_split:  # noqa: E501, pylint: disable=line-too-long
                if status.in_reply_to_user_id_str in settings.user_list_replies_to_our_tweet_split:  # noqa: E501, pylint: disable=line-too-long
                    main(tweet=status)
        else:
            main(tweet=status)


def start() -> None:
    """Authenticate to the Twitter API and start the filter."""
    stream = MyStreamListener(
        settings.consumer_key,
        settings.consumer_secret,
        settings.access_token,
        settings.access_token_secret,
    )

    # Streams are only terminated if the connection is closed, blocking
    # the thread.
    stream.filter(follow=settings.user_list, stall_warnings=True)


if __name__ == "__main__":
    start()
