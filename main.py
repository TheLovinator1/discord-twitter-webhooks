import html
import json
import logging
import re

import requests
import tweepy
from dhooks import Embed, Webhook
from tweepy import Stream

from settings import (
    access_token,
    access_token_secret,
    auth,
    consumer_key,
    consumer_secret,
    log_level,
    twitter_image_collage_maker,
    user_list_replies_to_other_tweet,
    user_list_replies_to_our_tweet,
    user_list_someone_retweets_our_tweet,
    user_list_we_retweet_someone_elses_tweet,
    get_retweet_of_own_tweet,
    users_to_follow,
    webhook_url,
)


def get_text(tweet) -> str:
    try:
        text = tweet.extended_tweet["full_text"]
        logger.debug(f"Tweet is extended: {text}")

    except AttributeError:
        text = tweet.text
        logger.debug(f"Tweet is not extended: {text}")
    return text


def get_media_links_and_remove_url(tweet, text: str) -> tuple:
    link_list = []

    logger.debug(f"Found image in: https://twitter.com/i/web/status/{tweet.id}")
    try:
        # Tweet is more than 140 characters
        for image in tweet.extended_tweet["extended_entities"]["media"]:
            link_list.append(image["media_url_https"])
            text = text.replace(image["url"], "")
    except KeyError:
        # Tweet has no links
        pass

    except AttributeError:
        # Tweet is less than 140 characters
        try:
            for image in tweet.extended_entities["media"]:
                link_list.append(image["media_url_https"])
                text = text.replace(image["url"], "")
        except AttributeError:
            # Tweet has no links
            pass

    return link_list, text


def get_avatar_url(tweet) -> str:
    avatar_url = tweet.user.profile_image_url_https
    logger.debug(f"Avatar URL: {avatar_url}")
    return avatar_url.replace("_normal.jpg", ".jpg")


def replace_tco_url_link_with_real_link(tweet, text: str) -> str:
    try:
        # Tweet is more than 140 characters
        for url in tweet.extended_tweet["entities"]["urls"]:
            text = text.replace(url["url"], url["expanded_url"])

    except AttributeError:
        # Tweet is less than 140 characters
        try:
            for url in tweet.entities["urls"]:
                text = text.replace(url["url"], url["expanded_url"])
        except AttributeError:
            # Tweet has no links
            pass
    return text


def _regex_substitutor(pattern: str, replacement: str, string: str) -> str:
    substitute = re.sub(
        r"{}".format(pattern), r"{}".format(replacement), string, flags=re.MULTILINE
    )
    return substitute


def twitter_regex(text: str) -> str:
    regex_dict = {  # I have no idea what I am doing so don't judge my regex lol
        # Replace @username with link
        r"@(\w*)": r"[\g<0>](https://twitter.com/\g<1>)",
        # Replace #hashtag with link
        r"#(\w*)": r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
        # Discord makes link previews, can fix this by changing to <url>
        r"(https://\S*)\)": r"<\g<1>>)",
        # Change /r/subreddit to clickable link
        r".*?(/r/)([^\s^\/]*)(/|)": r"[/r/\g<2>](https://reddit.com/r/\g<2>)",
        # Change /u/user to clickable link
        r".*?(/u/|/user/)([^\s^\/]*)(/|)": r"[/u/\g<2>](https://reddit.com/u/\g<2>)",
    }

    for pat, rep in regex_dict.items():
        text = _regex_substitutor(pattern=pat, replacement=rep, string=text)

    logger.debug(f"After we add links to tweet: {text}")
    return text


def send_text_webhook(text: str):
    logger.error(f"Webhook text: {text}")
    hook = Webhook(webhook_url)
    hook.send(text)


def send_embed_webhook(avatar: str, tweet, link_list, text: str):
    logger.debug(f"Tweet: {text}")
    hook = Webhook(webhook_url)

    embed = Embed(
        description=text,
        color=0x1E0F3,
        timestamp="now",
    )
    if link_list is not None:
        if len(link_list) == 1:
            logger.debug(f"Found one image: {link_list[0]}")
            embed.set_image(link_list[0])

        elif len(link_list) > 1:
            logger.debug("Found more than one image")
            response = requests.get(
                url=twitter_image_collage_maker, params={"tweet_id": tweet.id}
            )

            if response.status_code == 200:
                json_data = json.loads(response.text)
                print(f"json from {twitter_image_collage_maker}: {json_data}")
                embed.set_image(json_data["url"])
            else:
                logger.error(
                    f"Failed to get response from {twitter_image_collage_maker}. "
                    "Using first image instead."
                )
                embed.set_image(link_list[0])

    embed.set_author(
        icon_url=avatar,
        name=tweet.user.screen_name,
        url=f"https://twitter.com/i/web/status/{tweet.id}",
    )

    hook.send(embed=embed)

    logger.info("Webhook posted.")


def main(tweet):
    logger.debug(f"Raw tweet before any modifications: {tweet}")
    text = get_text(tweet)
    media_links, text_media_links = get_media_links_and_remove_url(tweet, text)
    avatar = get_avatar_url(tweet)

    unescaped_text = html.unescape(text_media_links)
    logger.debug(f"Safe HTML converted to unsafe HTML: {text}")

    text_url_links = replace_tco_url_link_with_real_link(tweet, unescaped_text)
    regex = twitter_regex(text_url_links)
    send_embed_webhook(avatar=avatar, tweet=tweet, link_list=media_links, text=regex)


class MyStreamListener(Stream):
    def on_status(self, tweet):
        print(f"on_status: {tweet}")
        """Called when a new status arrives"""

        # Tweet is retweet
        if hasattr(tweet, "retweeted_status"):
            logger.info("Tweet is retweet")
            if tweet.user.id_str == tweet.retweeted_status.user.id_str:
                if get_retweet_of_own_tweet.lower() == "true":
                    logger.info("We replied to our self")
                    main(tweet=tweet)
                    return
            if tweet.retweeted_status.user.id_str in user_list_retweeted_split:
                logger.info("Someone retweeted our tweet")
                main(tweet=tweet)
                return
            elif tweet.user.id_str in user_list_retweets_split:
                logger.info("We retweeted a tweet")
                main(tweet=tweet)
                return
            else:
                logger.info(
                    "Retweets and retweeted are not active in the environment variables."
                )
                return
        # Tweet is a reply
        elif tweet.in_reply_to_user_id is not None:
            # FIXME: If somebody else responds to their own reply in our tweet this activates.
            # We need to check who the original tweet author is.
            #
            # if tweet.user.id_str == tweet.in_reply_to_user_id_str:
            #     logger.info("We replied to our self")
            #     main(tweet=tweet)
            #     return
            #
            if tweet.user.id_str in user_list_replies_to_other_tweet_split:
                logger.info("We replied to someone")
                main(tweet=tweet)
                return
            elif tweet.in_reply_to_user_id_str in user_list_replies_to_our_tweet_split:
                logger.info("Someone replied to us")
                main(tweet=tweet)
                return
            else:
                logger.info(
                    "We didn't reply to our self, someone else or someone replied to us. "
                    "Or it is not active in the environment variables."
                )
                return
        else:
            main(tweet=tweet)
            return


if __name__ == "__main__":
    user_list_retweets_split = []
    user_list_retweeted_split = []
    user_list_replies_to_our_tweet_split = []
    user_list_replies_to_other_tweet_split = []
    logger = logging
    logger.basicConfig(format="%(asctime)s - %(message)s", level=log_level)

    level = logging.getLevelName(log_level)

    logger.debug(f"Consumer key: {consumer_key}")
    logger.debug(f"Consumer secret: {consumer_secret}")
    logger.debug(f"Access Token: {access_token}")
    logger.debug(f"Access Token Secret: {access_token_secret}")
    logger.debug(f"Users we follow: {users_to_follow}")
    logger.debug(f"Users replies to our tweet: {user_list_replies_to_our_tweet}")
    logger.debug(f"Users replies to other tweet: {user_list_replies_to_other_tweet}")
    logger.debug(f"Webhook url: {webhook_url}")
    logger.debug(f"Twitter collage maker: {twitter_image_collage_maker}")

    # Authenticate to the Twitter API
    api = tweepy.API(auth)
    stream = MyStreamListener(
        consumer_key, consumer_secret, access_token, access_token_secret
    )

    if users_to_follow is not None:
        logger.info("Users - Tweets:")
        user_list = [x.strip() for x in str(users_to_follow).split(",")]
        for twitter_id in user_list:
            username = api.get_user(user_id=twitter_id)
            print(f"{twitter_id} - {username.screen_name}")
    else:
        print("It looks like USERS_TO_FOLLOW is empty. Did you forget to fill it out?")

    if user_list_replies_to_our_tweet is not None:
        logger.info("Users - Comment to us from other:")
        user_list_replies_to_our_tweet_split = [
            x.strip() for x in str(user_list_replies_to_our_tweet).split(",")
        ]
        for twitter_id in user_list_replies_to_our_tweet_split:
            username_reply = api.get_user(user_id=twitter_id)
            logger.info(f"{twitter_id} - {username_reply.screen_name}")
    else:
        logger.info("Found no users to get replies from.")

    if user_list_replies_to_other_tweet is not None:
        logger.info("Users - Comment from us to other:")
        user_list_replies_to_other_tweet_split = [
            x.strip() for x in str(user_list_replies_to_other_tweet).split(",")
        ]
        for twitter_id in user_list_replies_to_other_tweet_split:
            username_reply = api.get_user(user_id=twitter_id)
            logger.info(f"{twitter_id} - {username_reply.screen_name}")
    else:
        logger.info("Found no users to get replies to.")

    if user_list_we_retweet_someone_elses_tweet is not None:
        logger.info("Users - We retweet others tweet:")
        user_list_retweets_split = [
            x.strip() for x in str(user_list_we_retweet_someone_elses_tweet).split(",")
        ]
        for twitter_id in user_list_retweets_split:
            username_reply = api.get_user(user_id=twitter_id)
            logger.info(f"{twitter_id} - {username_reply.screen_name}")
    else:
        logger.info("Found no users were we track retweets.")

    if user_list_someone_retweets_our_tweet is not None:
        logger.info("Users - Other retweets our tweet:")
        user_list_retweeted_split = [
            x.strip() for x in str(user_list_someone_retweets_our_tweet).split(",")
        ]
        for twitter_id in user_list_retweeted_split:
            username_reply = api.get_user(user_id=twitter_id)
            logger.info(f"{twitter_id} - {username_reply.screen_name}")
    else:
        logger.info("Found no users were we track tweets that get retweeted.")
    # Streams are only terminated if the connection is closed, blocking the thread.
    stream.filter(follow=user_list, stall_warnings=True)
