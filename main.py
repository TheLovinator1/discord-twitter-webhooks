#!/usr/bin/env python3
import re

import pytz
import tweepy
from dhooks import Embed, Webhook
from tweepy import OAuthHandler, Stream

# Import settings from config.py
import config

# TODO: Make /u/user and /r/subreddit to a link
# TODO: Fix gifs
# TODO: Fix polls

# We need to be authenticated to use the Twitter API
auth = OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)

# Authenticate to the API
api = tweepy.API(auth)
print("API key belongs to " + api.me().screen_name)

print("---------------------------")
print("Following: ")
for twitter_id in config.users_to_follow:
    username = api.get_user(twitter_id)
    print(twitter_id + " - " + str(username.screen_name))
print("---------------------------")


class MyStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_status(self, tweet):
        link_list = []
        try:
            # Skip retweets
            if tweet.retweeted or "RT @" in tweet.text:
                print("Is retweet")
                return

            # Don't get replies
            if tweet.in_reply_to_screen_name is not None:
                print("Is reply")
                return

            # Skip PUBG tweets for Xbox
            if "Xbox players: " in tweet.text:
                print("Is for xbox")
                return

            print("Raw tweet: " + str(tweet))

            # Check if the tweet is extended and get content
            try:
                text = tweet.extended_tweet["full_text"]
                print("Tweet is extended", text)
            except AttributeError:
                text = tweet.text
                print("Tweet is not extended", text)
                
            # Get media link
            if 'media' in tweet.entities:
                for media in tweet.extended_entities['media']:
                    print("Media: " + media['media_url_https'])
                    link = media['media_url_https']
                    link_list.append(link)

            # Only print link list if not empty
            if link_list:
                print("Link List:")
                print(*link_list)

            # Remove the "_normal.jpg" part in url
            avatar_hd = tweet.user.profile_image_url_https[:-11]
            extension = tweet.user.profile_image_url_https[-4:]
            print("Avatar: ", avatar_hd + extension)

            tz = pytz.timezone("Europe/Stockholm")  # TODO: Add to config file
            tweet_time = pytz.utc.localize(tweet.created_at, is_dst=None).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")
            print("Time: ", tweet_time)

            # Replace username with link
            text_profile_link = re.sub(r"@(\w*)", "[\g<0>](https://twitter.com/\g<1>/)", text, flags=re.MULTILINE)
            print("Text - profile links: ", text_profile_link)

            # Replace hashtag with link
            text_hashtag_link = re.sub(r"#(\w*)", "[\g<0>](https://twitter.com/hashtag/\g<1>/)", text_profile_link,
                                       flags=re.MULTILINE)
            print("Text - hashtags: ", text_hashtag_link)

            # Discord makes link previews from URLs, we can hide those with < and > before and after URLs
            # We do that with https://t.co/[a-zA-Z0-9]*
            # \g<0>	- Insert entire match
            # text_link_preview = re.sub(r'https://t.co/[a-zA-Z0-9]*', '<\g<0>>', text_hashtag_link, flags=re.MULTILINE)
            text_link_preview = re.sub(r"(https://\S*[^\s^.)])", "<\g<0>>", text_hashtag_link, flags=re.MULTILINE)
            print("Text - link preview: ", text_link_preview)

            # Append media so Discords link preview picks them up
            links = '\n'.join([str(v) for v in link_list])
            print("Links: ", links)

            message = text_link_preview + "\n\n" + "[" + str(tweet_time) + "](https://twitter.com/statuses/" + str(
                    tweet.id) + ")\n" + links + "\n"
            print("\nMessage: " + str(message) + "\n")

            # Make webhook embed
            hook = Webhook(config.url)

            embed = Embed(
                    description=message,
                    color=0x1e0f3,
                    timestamp=True  # Set the timestamp to current time
            )

            # Change webhook avatar to twitter avatar and replace webhook username with Twitter username
            embed.set_author(icon_url=str(avatar_hd) + extension, name=tweet.user.screen_name)

            first_image = link_list[0]
            embed.set_image(first_image)  # TODO: Change to highest quality
            print("First image: ", first_image)

            # Post to channel
            hook.send(embeds=embed)

            print("Posted.")
            print("-----------------")
        except Exception as e:
            print("Error: " + str(e))
            hook = Webhook(config.error_url)
            hook.send("<@126462229892694018> I'm broken again <:PepeHands:461899012136632320>\n" + str(e))

    def on_error(self, error_code):

        if error_code == 420:
            print("420 Enhance Your Calm - We are being rate limited.\n"
                  "Possible reasons: Too many login attempts or running too many copies of the same "
                  "application authenticating with the same credentials")
            return False  # returning False in on_error disconnects the stream

        print("Error: " + str(error_code))
        hook = Webhook(config.error_url)
        hook.send("<@126462229892694018> I'm broken again <:PepeHands:461899012136632320>\n" + str(error_code))


listener = MyStreamListener()
stream = Stream(auth, listener)

# Streams are only terminated if the connection is closed, blocking the thread.
# The async parameter makes the stream run on a new thread.
stream.filter(follow=config.users_to_follow, async=True)
