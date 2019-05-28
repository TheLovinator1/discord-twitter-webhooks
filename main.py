#!/usr/bin/env python3
import re
import log
import config
import tweepy
from dhooks import Embed, Webhook
from tweepy import OAuthHandler, Stream

# TODO: Fix gifs
# TODO: Fix polls

# We need to be authenticated to use the Twitter API
auth = OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)

# Authenticate to the API
api = tweepy.API(auth)
log.logger.info("API key belongs to " + api.me().screen_name)

# Print users we follow
for twitter_id in config.user_list:
    username = api.get_user(twitter_id)
    print(twitter_id + " - " + str(username.screen_name))


class MyStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_status(self, tweet):
        link_list = []
        try:
            log.logger.debug("Raw tweet: " + str(tweet))
            # Skip retweets
            if tweet.retweeted or "RT @" in tweet.text:
                # logger.debug("Tweet is retweet")
                return

            # Don't get replies
            if tweet.in_reply_to_screen_name is not None:
                # logger.debug("Tweet is reply")
                return

            # Skip PUBG tweets for Xbox
            if "Xbox players: " in tweet.text:
                # logger.debug("Tweet is for xbox")
                return

            # Check if the tweet is extended and get content
            try:
                text = tweet.extended_tweet["full_text"]
                log.logger.debug(f"Tweet is extended:")
                log.logger.debug(f"{text}")
            except AttributeError:
                text = tweet.text
                log.logger.debug(f"Tweet is not extended:")
                log.logger.debug(f"{text}")

            # Get media link
            if 'media' in tweet.entities:
                for media in tweet.extended_entities['media']:
                    log.logger.debug(f"Media: {media['media_url_https']}")
                    link = media['media_url_https']
                    link_list.append(link)
                    log.logger.debug(f"Media link: {link}")

            # Only print link list if not empty
            if link_list:
                log.logger.debug("Link List:")
                log.logger.debug(*link_list)

            # Remove the "_normal.jpg" part in url
            avatar_hd = tweet.user.profile_image_url_https[:-11]
            extension = tweet.user.profile_image_url_https[-4:]
            log.logger.debug(f"Avatar: {avatar_hd}{extension}")

            # Replace username with link
            text_profile_link = re.sub(r"@(\w*)", "[\g<0>](https://twitter.com/\g<1>/)", text, flags=re.MULTILINE)
            log.logger.debug(f"Text - profile links: {text_profile_link}")

            # Replace hashtag with link
            text_hashtag_link = re.sub(r"#(\w*)", "[\g<0>](https://twitter.com/hashtag/\g<1>/)", text_profile_link,
                                       flags=re.MULTILINE)
            log.logger.debug(f"Text - hashtags: {text_hashtag_link}")

            # Discord makes link previews from URLs, we can hide those with < and > before and after URLs
            text_link_preview = re.sub(r"(https://\S*[^\s^.)])", "<\g<0>>", text_hashtag_link, flags=re.MULTILINE)
            log.logger.debug(f"Text - link preview: {text_link_preview}")

            # Change /r/subreddit to clickable link
            text_reddit_subreddit_link = re.sub(r"/?r/(\S{3,21})", "[/r/\g<1>](https://www.reddit.com/r/\g<1>)",
                                                text_link_preview, flags=re.MULTILINE)
            log.logger.debug(f"Text - reddit subreddit: {text_reddit_subreddit_link}")

            # Change /u/user to clickable link
            text_reddit_user_link = re.sub(r"/?u/(\S{3,20})", "[/u/\g<1>](https://www.reddit.com/user/\g<1>)",
                                           text_reddit_subreddit_link, flags=re.MULTILINE)
            log.logger.debug(f"Text - reddit user: {text_reddit_user_link}")

            # Append media so Discords link preview picks them up
            links = '\n'.join([str(v) for v in link_list])
            log.logger.debug(f"Links: {links}")

            # Final message that we send
            message = text_reddit_user_link + links + "\n"
            log.logger.debug(f"Message: {message}")

            # Make webhook embed
            hook = Webhook(config.webhook_url)

            embed = Embed(
                description=message,
                color=0x1e0f3,  # Light blue
                timestamp="now"  # Set the timestamp to current time
            )

            # Change webhook avatar to twitter avatar and replace webhook username with Twitter username
            embed.set_author(icon_url=str(avatar_hd) + extension,
                             name=tweet.user.screen_name,
                             url="https://twitter.com/statuses/" + str(tweet.id))

            if link_list:
                first_image = link_list[0]
                embed.set_image(first_image)  # TODO: Change to highest quality
                log.logger.debug(f"First image: {first_image}")

            # Post to channel
            hook.send(embed=embed)

            log.logger.info("Posted.")

        except Exception as e:
            log.logger.error(f"Error: {e}")
            hook = Webhook(config.webhook_error_url)
            hook.send(f"<@126462229892694018> I'm broken again <:PepeHands:461899012136632320>\n{e}")

    def on_error(self, error_code):
        if error_code == 420:
            log.logger.error("420 Enhance Your Calm - We are being rate limited."
                             "Possible reasons: Too many login attempts or running too many copies of the same "
                             "application authenticating with the same credentials")
            return False  # returning False in on_error disconnects the stream

        log.logger.error(f"Error: {error_code}")
        hook = Webhook(config.webhook_error_url)
        hook.send(f"<@126462229892694018> I'm broken again <:PepeHands:461899012136632320>\n{error_code}")


listener = MyStreamListener()
stream = Stream(auth, listener)

# Streams are only terminated if the connection is closed, blocking the thread.
# The async parameter makes the stream run on a new thread.
stream.filter(follow=config.user_list, is_async=True)
