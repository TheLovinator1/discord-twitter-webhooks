import html

from tweepy import Stream

from discord_twitter_webhooks.change_reddit_username_to_link import change_reddit_username_to_link
from discord_twitter_webhooks.change_subreddit_to_clickable_link import change_subreddit_to_clickable_link
from discord_twitter_webhooks.get_media_links_and_remove_url import get_media_links_and_remove_url
from discord_twitter_webhooks.get_meta_image import get_meta_image
from discord_twitter_webhooks.get_text import get_text
from discord_twitter_webhooks.get_urls import get_urls
from discord_twitter_webhooks.remote_utm_source import remove_utm_source
from discord_twitter_webhooks.remove_discord_link_previews import remove_discord_link_previews
from discord_twitter_webhooks.replace_hashtag_with_link import replace_hashtag_with_link
from discord_twitter_webhooks.replace_tco_url_link_with_real_link import replace_tco_url_link_with_real_link
from discord_twitter_webhooks.replace_username_with_link import replace_username_with_link
from discord_twitter_webhooks.send_embed_webhook import send_embed_webhook
from discord_twitter_webhooks.settings import (
    access_token,
    access_token_secret,
    consumer_key,
    consumer_secret,
    get_retweet_of_own_tweet,
    logger,
    user_list,
    user_list_replies_to_other_tweet_split,
    user_list_replies_to_our_tweet_split,
    user_list_retweeted_split,
    user_list_retweets_split,
)


def main(tweet) -> None:
    """Don't be afraid to contact me if you have any questions about something here."""
    logger.debug(f"Raw tweet before any modifications: {tweet}")

    text = get_text(tweet)

    media_links, text_media_links = get_media_links_and_remove_url(tweet, text)

    urls_found = get_urls(tweet)
    twitter_card_image = get_meta_image(urls_found[0])

    unescaped_text = html.unescape(text_media_links)

    text_url_links = replace_tco_url_link_with_real_link(tweet, unescaped_text)

    text_replace_username = replace_username_with_link(text_url_links)

    text_replace_hashtags = replace_hashtag_with_link(text_replace_username)

    text_discord_preview = remove_discord_link_previews(text_replace_hashtags)

    text_subreddit_to_link = change_subreddit_to_clickable_link(text_discord_preview)

    text_reddit_username_to_link = change_reddit_username_to_link(text_subreddit_to_link)

    text_remove_utm_source = remove_utm_source(text_reddit_username_to_link)

    send_embed_webhook(
        tweet=tweet, link_list=media_links, text=text_remove_utm_source, twitter_card_image=twitter_card_image
    )


class MyStreamListener(Stream):
    """https://docs.tweepy.org/en/latest/streaming.html

    Args:
        Stream ([type]): Stream tweets in realtime.
    """

    def on_status(self, status) -> None:
        """This is called when a new tweet is received.

        Args:
            status ([type]): Twitter status
        """
        # Tweet is retweet
        if hasattr(status, "retweeted_status"):
            logger.info("Tweet is retweet")
            if (
                status.user.id_str == status.retweeted_status.user.id_str
                and get_retweet_of_own_tweet.lower() == "true"  # noqa
            ):
                logger.info("We replied to our self")
                main(tweet=status)
                return
            if status.retweeted_status.user.id_str in user_list_retweeted_split:
                logger.info("Someone retweeted our tweet")
                main(tweet=status)
            elif status.user.id_str in user_list_retweets_split:
                logger.info("We retweeted a tweet")
                main(tweet=status)
            else:
                logger.info("Retweets and retweeted are not active in the environment variables.")
        elif status.in_reply_to_user_id is not None:
            # FIXME: If somebody else responds to their own reply in our tweet this activates.
            # We need to check who the original tweet author is.
            #
            # if tweet.user.id_str == tweet.in_reply_to_user_id_str:
            #     logger.info("We replied to our self")
            #     main(tweet=tweet)
            #     return
            #
            if status.user.id_str in user_list_replies_to_other_tweet_split:
                logger.info("We replied to someone")
                main(tweet=status)
            elif status.in_reply_to_user_id_str in user_list_replies_to_our_tweet_split:
                logger.info("Someone replied to us")
                main(tweet=status)
            else:
                logger.info(
                    "We didn't reply to our self, someone else or someone replied to us. "
                    "Or it is not active in the environment variables."
                )
        else:
            main(tweet=status)

        return


def start() -> None:
    """Authenticate to the Twitter API and start the filter."""
    stream = MyStreamListener(consumer_key, consumer_secret, access_token, access_token_secret)

    # Streams are only terminated if the connection is closed, blocking the thread.
    stream.filter(follow=user_list, stall_warnings=True)


if __name__ == "__main__":
    start()
