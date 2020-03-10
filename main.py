"""This program fetches tweets and writes them in Discord."""

import re

import tweepy
from dhooks import Embed, Webhook
from tweepy import OAuthHandler, Stream

import config
import log

# TODO: Fix gifs and polls

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
                return

            # Don't get replies
            if tweet.in_reply_to_screen_name is not None:
                return

            # Check if the tweet is truncated and get full tweet
            try:
                text = tweet.extended_tweet["full_text"]
                log.logger.debug(f"Tweet is extended:\n{text}")
            except AttributeError:
                text = tweet.text
                log.logger.debug(f"Tweet is not extended:\n{text}")

            # Get media link
            if "media" in tweet.entities:
                for media in tweet.extended_entities["media"]:
                    log.logger.debug(f"Media: {media['media_url_https']}")
                    link = media["media_url_https"]
                    link_list.append(link)
                    log.logger.debug(f"Media link: {link}")

            # Only print link list if not empty
            if link_list:
                log.logger.debug("Link List:")
                log.logger.debug(*link_list)

            # Remove the "_normal.jpg" part in url to get higher quality
            avatar_hd = tweet.user.profile_image_url_https[:-11]
            extension = tweet.user.profile_image_url_https[-4:]
            log.logger.debug(f"Avatar: {avatar_hd}{extension}")

            # Replace t.co url with real url
            try:
                for url in tweet.extended_tweet["entities"]["urls"]:
                    text = text.replace(url["url"], url["expanded_url"])

            except AttributeError:
                for url in tweet.entities["urls"]:
                    text = text.replace(url["url"], url["expanded_url"])

            regex_dict = {  # I have no idea what I am doing so don't judge my regex lol
                # Replace @username with link
                r"@(\w*)": r"[\g<0>](https://twitter.com/\g<1>)",
                # Replace #hashtag with link
                r"#(\w*)": r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
                # Discord makes link previews, can fix this by changing to <url>
                r"(https://\S*)\)": r"<\g<1>>)",
                # Change /r/subreddit to clickable link # FIXME: Broken.
                # r"/?r/(\S{3,21})": r"[/r/\g<1>](https://reddit.com/r/\g<1>)",
                # Change /u/user to clickable link      # FIXME: Broken.
                # r"/?u/(\S{3,20})": r"[/u/\g<1>](https://reddit.com/u/\g<1>)",
            }

            for pat, rep in regex_dict.items():
                text = self.regex_substitutor(pattern=pat, replacement=rep, string=text)

            # Append media so Discord link preview picks them up
            links = "\n".join([str(v) for v in link_list])
            log.logger.debug(f"Links: {links}")

            # Final message that we send
            message = text + " " + links + "\n"
            log.logger.debug(f"Message: {message}")

            # Make webhook embed
            hook = Webhook(config.webhook_url)
            embed = Embed(
                description=message,
                color=0x1E0F3,  # Light blue
                timestamp="now",  # Set the timestamp to current time
            )

            # Change webhook avatar to Twitter avatar and replace
            # webhook username with Twitter username
            embed.set_author(
                icon_url=str(avatar_hd) + extension,
                name=tweet.user.screen_name,
                url="https://twitter.com/statuses/" + str(tweet.id),
            )

            if link_list:
                first_image = link_list[0]
                embed.set_image(first_image)  # TODO: Change to highest quality
                log.logger.debug(f"First image: {first_image}")

            # Post to channel
            hook.send(embed=embed)

            log.logger.info("Posted.")

        except Exception as e:  # TODO: Write what we did before the error
            log.logger.error(f"Error: {e}")
            hook = Webhook(config.webhook_error_url)
            hook.send(
                f"<@126462229892694018> I'm broken again "
                f"<:PepeHands:461899012136632320>\n{e}"
            )

    # TODO: Write information about the error instead of just the error
    # number
    def on_error(self, error_code):
        if error_code == 420:
            log.logger.error(
                "We are being rate limited. Too many login attempts or "
                "running too many copies of the same credentials"
            )
            return False  # returning False in on_error disconnects the stream

        log.logger.error(f"Error: {error_code}")
        hook = Webhook(config.webhook_error_url)
        hook.send(
            f"<@126462229892694018> I'm broken again "
            f"<:PepeHands:461899012136632320>\n{error_code}"
        )
        return False

    def regex_substitutor(self, pattern: str, replacement: str, string: str) -> str:
        substitute = re.sub(
            r"{}".format(pattern), r"{}".format(replacement), string, flags=re.MULTILINE
        )
        return substitute


listener = MyStreamListener()
stream = Stream(auth, listener)

# Streams are only terminated if the connection is closed, blocking the
# thread. The async parameter makes the stream run on a new thread.
stream.filter(follow=config.user_list, is_async=True)
