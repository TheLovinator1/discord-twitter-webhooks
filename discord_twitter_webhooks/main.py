"""The main file for discord-twitter-webhooks. Run this file to run the bot."""
import html
import sys

from tweepy.streaming import StreamResponse, StreamingClient

from discord_twitter_webhooks import get, reddit, remove, replace, settings
from discord_twitter_webhooks.get import get_avatar_and_username, get_entities, get_text, get_webhook_url
from discord_twitter_webhooks.rules import delete_old_rules, new_rule
from discord_twitter_webhooks.send_webhook import (
    send_embed_webhook,
    send_error_webhook, )

# TODO: Add support for Twitter Spaces
# TODO: Add backfill so we get missed tweets?
# TODO: Add threading?
# TODO: Add polls?
# TODO: If tweet is deleted, remove it from Discord?
# TODO: If tweet is poll, update it in Discord, so we can see results?

rule_ids = {}


def main(response: StreamResponse) -> None:
    """The main function for the bot. This is where the magic happens."""
    settings.logger.debug(f"Response: {response}")

    twitter_card_image = ""
    media_links: list[str] = []

    webhook_url = get_webhook_url(response)
    avatar, user_name = get_avatar_and_username(response)
    text = get_text(response)

    data = response.data

    if response.includes:
        includes = response.includes
        if "media" in includes:
            media_list: list[dict] = [media.data for media in response.includes["media"]]
            settings.logger.debug(f"Media list: {media_list}")

            # Get the images from the tweet and remove the URLs from the text.
            media_links = get.media_links(media_list)

    entities = get_entities(response)
    if entities:
        if "urls" in entities:
            text = remove.remove_media_links(entities, text)
            twitter_card_image = get.meta_image(entities)

            # Replace Twitters shortened URLs with the original URL.
            text = replace.tco_url_link_with_real_link(entities, text)

    # We coverts &gt; and &lt; to > and < to make the text look nicer.
    text = html.unescape(text)

    # Replace the @mentions with URLs.
    text = replace.username_with_link(text)

    # Replace the hashtags with URLs.
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
        media_links=media_links,
        text=text,
        twitter_card_image=twitter_card_image,
        avatar_url=avatar,
        screen_name=user_name,
        webhook=webhook_url,
    )


class MyStreamListener(StreamingClient):
    """https://docs.tweepy.org/en/latest/streaming.html#using-streamingclient

    Stream tweets in realtime.
    """

    def on_exception(self, exception: Exception) -> None:
        """An unhandled exception was raised while streaming. Shutting down."""
        error_msg = (f"discord-twitter-webhooks: An unhandled exception was raised while streaming. Shutting down"
                     f"\nException: {exception!r}")
        send_error_webhook(error_msg)

        self.disconnect()
        sys.exit(error_msg)

    def on_response(self, response: StreamResponse) -> None:
        """This is called when a response is received."""
        if response.data:
            main(response)


def start() -> None:
    """Authenticate to the Twitter API and start the filter."""
    # TODO: Add proxy support?
    stream = MyStreamListener(
        settings.bearer_token,
        wait_on_rate_limit=True,
    )

    # Delete old rules
    # TODO: We should only delete the rules we created and if they are changed.
    delete_old_rules(stream=stream)

    # Create the rules
    rules = settings.rules
    for rule_num in rules:
        rule = str(rules[rule_num])
        rule_id = new_rule(stream=stream, rule=rule, rule_tag=f"rule{rule_num}")
        settings.logger.info(f"Rule {rule_id!r} added to Twitter.com")
        rule_ids[rule_num] = {rule_id}

    settings.logger.debug(f"Rule IDs: {rule_ids}")

    # TODO: dry_run before to make sure everything works?
    try:
        settings.logger.info("Starting stream! (Press CTRL+C to stop, it will take 20 seconds to stop, because we have"
                             " to wait for the next signal to be sent from the Twitter API)")
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
