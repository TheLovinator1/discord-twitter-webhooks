import html
import os
import sys
from time import sleep

import tweepy
from tweepy.streaming import StreamResponse

from discord_twitter_webhooks import get, reddit, remove, replace, settings
from discord_twitter_webhooks.send_webhook import (
    send_embed_webhook,
    send_normal_webhook,
)

# TODO: Add support for Twitter Spaces
# TODO: Add backfill so we get missed tweets?
# TODO: Add threading?
# TODO: Add polls?
# TODO: If tweet is deleted, remove it from Discord?
# TODO: If tweet is poll, update it in Discord so we can see results?


def main(response: StreamResponse) -> None:
    settings.logger.debug(f"Response: {response}")
    data = response.data

    settings.logger.debug(f"Data: {data}")
    settings.logger.debug(f"Includes: {response.includes}")

    media = []
    if "media" in response.includes:
        media = [media.data for media in response.includes["media"]]
        settings.logger.debug(f"Media: {media}")

    # Get avatar and username, this is used for the embed avatar and name
    avatar = ""
    user_name = ""
    if "users" in response.includes:
        users = [users.data for users in response.includes["users"]]
        settings.logger.debug(f"Users: {users}")
        avatar = users[0]["profile_image_url"]
        user_name = users[0]["name"]

    twitter_card_image = ""

    # Get the text from the tweet
    text = data.text
    settings.logger.debug(f"Text: {text}")

    # Get the images from the tweet and remove the URLs from the text
    media_links = get.media_links(media) if media else []

    # Get entities from the tweet
    entities = {}
    if data.entities:
        entities = data.entities
        settings.logger.debug(f"Entities: {entities}")

    # Remove media links from the text
    if "urls" in entities:
        text = remove.remove_media_links(entities, text)

        if urls_found := get.tweet_urls(entities):
            twitter_card_image = get.meta_image(urls_found[0])

        # Replace Twitters shortened URLs with the original URL
        text = replace.tco_url_link_with_real_link(entities, text)

    # We coverts &gt; and &lt; to > and < to make the text look nicer
    text = html.unescape(text)

    # Replace the @mentions with URLs
    text = replace.username_with_link(text)

    # Replace the #hashtags with URLs
    text = replace.hashtag_with_link(text)

    # Append < and > to disable Discords link previews
    text = remove.discord_link_previews(text)

    # Change /r/subreddit to the subreddit URL
    text = reddit.subreddit_to_link(text)

    # Change /u/username to the user URL
    text = reddit.username_to_link(text)

    # Remove UTM parameters, this cleans up the URL
    text = remove.utm_source(text)

    # Remove trailing whitespace
    text = text.rstrip()

    # Remove copyright symbols
    text = remove.copyright_symbols(text)

    send_embed_webhook(
        tweet_id=data.id,
        link_list=media_links,
        text=text,
        twitter_card_image=twitter_card_image,
        avatar_url=avatar,
        screen_name=user_name,
    )


class MyStreamListener(tweepy.StreamingClient):
    """https://docs.tweepy.org/en/latest/streaming.html

    Stream tweets in realtime.
    """

    def on_response(self, response: StreamResponse):
        main(response)


def start() -> None:
    """Authenticate to the Twitter API and start the filter."""
    MESSAGE = """Hello!

[discord-twitter-webhooks](https://github.com/TheLovinator1/discord-twitter-webhooks) has been updated to version 2.0.0.
There have been a few breaking changes, and it looks like you were using
the old version.

You will need to update your environment/configuration file to get
discord-twitter-webhooks working again.

The bot is now using the V2 version of the Twitter API, which means that you
will need to update your configuration file to use a bearer token
instead of API keys.

Rules are also used instead of user ids. It's now possible to
have more granular control over what tweets get sent to Discord.
You can now filter specific words, only get tweets with images, and much more instead
of getting all the tweets from a specific user.

You can find more information in the [README.md](https://github.com/TheLovinator1/discord-twitter-webhooks).


The bot will now sleep for 4 hours before restarting to avoid spamming
this channel due to Docker/Systemd restarting the bot every time it
shuts down. You will have to remove USERS_TO_FOLLOW from your
environment/configuration file to stop this message from appearing.


Feel free to contact me on Discord, make an [issue on GitHub](https://github.com/TheLovinator1/discord-twitter-webhooks), or email me
at tlovinator@gmail.com if you have any questions.

Thanks,
TheLovinator#9276"""  # noqa: E501, pylint: disable=line-too-long

    if "USERS_TO_FOLLOW" in os.environ:
        # Send a message to the channel to let the user know that the
        # configuration file has been updated
        send_normal_webhook(msg=MESSAGE)
        settings.logger.critical(MESSAGE)
        # Sleep for 4 hours to avoid spamming the channel
        try:
            sleep(4 * 60 * 60)
        except KeyboardInterrupt:
            sys.exit(1)

    if not settings.bearer_token:
        settings.logger.critical("No bearer token found, exiting")
        sys.exit(1)

    if not settings.rule:
        settings.logger.critical("No rule found, exiting")
        sys.exit(1)

    else:
        # TODO: Add proxy support?
        stream = MyStreamListener(
            settings.bearer_token,
            wait_on_rate_limit=True,
        )

        # Check Twitter app for rules that already have been created
        old_rules = stream.get_rules()

        # Get rules and add to list so we can delete them later
        rules_to_delete = []
        if old_rules.data and len(old_rules.data) > 0:
            for old_rule in old_rules.data:
                settings.logger.debug(
                    f"Added {old_rule.value} - {old_rule.id} for deletion",
                )
                rules_to_delete.append(old_rule.id)

        # TODO: Only remove rule if the user list has changed?
        # If the app already has rules, delete them first before adding our own
        if rules_to_delete:
            settings.logger.info(f"Deleting rules: {rules_to_delete}")
            stream.delete_rules(rules_to_delete)
        else:
            settings.logger.info("App had no rules to delete")

        # TODO: dry_run before to make sure everything works?
        try:
            rule_response = stream.add_rules(
                add=tweepy.StreamRule(value=settings.rule),
            )

            if rule_response.errors:
                for error in rule_response.errors:
                    settings.logger.error(f"\nFound error for: {error['value']}")
                    settings.logger.error(
                        f"{error['title']} - Error details: {error['details'][0]}",
                    )
                sys.exit(1)

            settings.logger.info("Starting stream!")

            stream.filter(
                expansions=[
                    "author_id",
                    "referenced_tweets.id",
                    "in_reply_to_user_id",
                    "attachments.media_keys",
                    "attachments.poll_ids",
                    "entities.mentions.username",
                    "referenced_tweets.id.author_id",
                ],
                media_fields=[
                    "url",
                    "preview_image_url",
                ],
                tweet_fields=[
                    "attachments",
                    "author_id",
                    "entities",
                    "in_reply_to_user_id",
                    "referenced_tweets",
                ],
                user_fields=[
                    "profile_image_url",
                ],
            )

        except KeyboardInterrupt:
            stream.disconnect()
            sys.exit(0)


if __name__ == "__main__":
    start()
