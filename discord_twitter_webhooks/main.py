import html
import sys
from time import sleep

import tweepy
from tweepy.streaming import StreamResponse

from discord_twitter_webhooks import get, reddit, remove, replace, settings
from discord_twitter_webhooks.rules import delete_old_rules, new_rule
from discord_twitter_webhooks.send_webhook import (
    send_embed_webhook,
    send_normal_webhook,
)
from discord_twitter_webhooks.v1_message import MESSAGE, check_if_we_used_v1


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
    settings.logger.debug(f"Matching rule: {response.matching_rules}")

    matching_rules = response.matching_rules
    settings.logger.debug(f"Matching rules: {matching_rules}")

    matching_rule_error = (f"discord-twitter-webhooks error: Failed to find matching rule for {matching_rules[0].tag!r}"
                           f"\nTweet was: <https://twitter.com/i/web/status/{data.id}>"
                           "\nContact TheLovinator#9276 if this keeps happening.")

    new_webhook_url = settings.webhook_url
    if matching_rules:
        if matching_rules[0].tag == "Rule1":
            new_webhook_url = settings.webhook_url
        elif matching_rules[0].tag == "Rule2":
            new_webhook_url = settings.webhook_url2
        elif matching_rules[0].tag == "Rule3":
            new_webhook_url = settings.webhook_url3
        elif matching_rules[0].tag == "Rule4":
            new_webhook_url = settings.webhook_url4
        elif matching_rules[0].tag == "Rule5":
            new_webhook_url = settings.webhook_url5
        else:
            send_normal_webhook(matching_rule_error)
    else:
        send_normal_webhook(matching_rule_error)

    media = []
    if response.includes:
        if "media" in response.includes:
            media = [media.data for media in response.includes["media"]]
            settings.logger.debug(f"Media: {media}")

    # Get avatar and username, this is used for the embed avatar and name.
    avatar = ""
    user_name = ""
    if "users" in response.includes:
        users = [users.data for users in response.includes["users"]]
        settings.logger.debug(f"Users: {users}")
        avatar = users[0]["profile_image_url"]
        user_name = users[0]["name"]

    twitter_card_image = ""

    # Get the text from the tweet.
    try:
        text = data.text
    except AttributeError:
        text = "*Failed to get text from tweet*"
        settings.logger.error("No text found for tweet")

    settings.logger.debug(f"Text: {text}")

    # Get the images from the tweet and remove the URLs from the text.
    media_links = get.media_links(media) if media else []

    # Get entities from the tweet.
    entities = {}
    try:
        if data.entities:
            entities = data.entities
            settings.logger.debug(f"Entities: {entities}")
    except AttributeError:
        settings.logger.error("No entities found for tweet")
        entities = {}

    # Remove media links from the text.
    if "urls" in entities:
        text = remove.remove_media_links(entities, text)

        if urls_found := get.tweet_urls(entities):
            twitter_card_image = get.meta_image(urls_found[0])

        # Replace Twitters shortened URLs with the original URL.
        text = replace.tco_url_link_with_real_link(entities, text)

    # We coverts &gt; and &lt; to > and < to make the text look nicer.
    text = html.unescape(text)

    # Replace the @mentions with URLs.
    text = replace.username_with_link(text)

    # Replace the #hashtags with URLs.
    text = replace.hashtag_with_link(text)

    # Append < and > to disable Discords link previews.
    text = remove.discord_link_previews(text)

    # Change /r/subreddit to the subreddit URL.
    text = reddit.subreddit_to_link(text)

    # Change /u/username to the user URL.
    text = reddit.username_to_link(text)

    # Remove UTM parameters, this cleans up the URL.
    text = remove.utm_source(text)

    # Remove trailing whitespace.
    text = text.rstrip()

    # Remove copyright symbols.
    text = remove.copyright_symbols(text)

    send_embed_webhook(
        tweet_id=data.id,
        link_list=media_links,
        text=text,
        twitter_card_image=twitter_card_image,
        avatar_url=avatar,
        screen_name=user_name,
        webhook=new_webhook_url,
    )


class MyStreamListener(tweepy.StreamingClient):
    """https://docs.tweepy.org/en/latest/streaming.html#using-streamingclient

    Stream tweets in realtime.
    """

    def on_response(self, response: StreamResponse):
        """This is called when a response is received."""
        main(response)


def start() -> None:
    """Authenticate to the Twitter API and start the filter."""

    # Check if we have used the v1 bot before
    if check_if_we_used_v1():
        send_normal_webhook(msg=MESSAGE)

        # Sleep for 4 hours to avoid spamming the channel
        sleep(4 * 60 * 60)

    # TODO: Add proxy support?
    stream = MyStreamListener(
        settings.bearer_token,
        wait_on_rate_limit=True,
    )

    # Delete old rules
    delete_old_rules(stream=stream)

    rule_id = new_rule(rule=settings.rule, rule_tag="Rule1", stream=stream)
    rule2_id = new_rule(rule=settings.rule2, rule_tag="Rule2", stream=stream)
    rule3_id = new_rule(rule=settings.rule3, rule_tag="Rule3", stream=stream)
    rule4_id = new_rule(rule=settings.rule4, rule_tag="Rule4", stream=stream)
    rule5_id = new_rule(rule=settings.rule5, rule_tag="Rule5", stream=stream)

    if rule_id:
        settings.logger.info(f"Rule {rule_id} added")
    if rule2_id:
        settings.logger.info(f"Rule {rule2_id} added")
    if rule3_id:
        settings.logger.info(f"Rule {rule3_id} added")
    if rule4_id:
        settings.logger.info(f"Rule {rule4_id} added")
    if rule5_id:
        settings.logger.info(f"Rule {rule5_id} added")

    # TODO: dry_run before to make sure everything works?
    try:
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
