import asyncio
import html
import sys
from typing import Any

from tweepy.asynchronous import AsyncStreamingClient
from tweepy.streaming import StreamResponse

from discord_twitter_webhooks import get, reddit, remove, replace, settings
from discord_twitter_webhooks.get import (
    get_avatar_and_username,
    get_entities,
    get_text,
    get_webhook_url,
)
from discord_twitter_webhooks.rules import delete_old_rules, new_rule
from discord_twitter_webhooks.send_webhook import (
    send_embed_webhook,
    send_error_webhook,
    send_normal_webhook,
)
from discord_twitter_webhooks.settings import (
    disable_remove_copyright_symbols,
    disable_remove_discord_link_previews,
    disable_remove_tco_links,
    disable_remove_trailing_whitespace,
    disable_remove_utm_parameters,
    disable_replace_hashtag,
    disable_replace_reddit_username,
    disable_replace_subreddit,
    disable_replace_username,
    disable_unescape_text,
    no_embed,
)

# TODO: Add support for Twitter Spaces
# TODO: Add backfill so we get missed tweets?
# TODO: Add threading?
# TODO: Add polls?
# TODO: If tweet is deleted, remove it from Discord?
# TODO: If tweet is poll, update it in Discord, so we can see results?

rule_ids = {}


def main(response: StreamResponse) -> None:
    """The main function for the bot. This is where the magic happens."""
    settings.logger.debug("Response: %s", response)

    twitter_card_image: str = ""
    media_links: list[str] = []

    webhook_url: str = get_webhook_url(response)
    avatar, user_name = get_avatar_and_username(response)
    text: str = get_text(response)

    data = response.data

    if response.includes:
        includes: dict[str, list[Any]] = response.includes
        if "media" in includes:
            media_list: list[dict] = [media.data for media in response.includes["media"]]
            settings.logger.debug("Media list: %s", media_list)

            # Get the images from the tweet and remove the URLs from the text.
            media_links = get.media_links(media_list)

    if (entities := get_entities(response)) and "urls" in entities:
        text = remove.remove_media_links(entities, text)
        twitter_card_image = get.meta_image(entities)

        if disable_remove_tco_links != "True":
            # Replace Twitters shortened URLs with the original URL.
            text = replace.tco_url_link_with_real_link(entities, text)

    if disable_unescape_text != "True":
        # We coverts &gt; and &lt; to > and < to make the text look nicer.
        text = html.unescape(text)

    if disable_replace_username != "True":
        # Replace the @mentions with URLs.
        text = replace.username_with_link(text)

    if disable_replace_hashtag != "True":
        # Replace the hashtags with URLs.
        text = replace.hashtag_with_link(text)

    if disable_remove_discord_link_previews != "True":
        # Append < and > to disable Discords link previews.
        text = remove.discord_link_previews(text)

    if disable_replace_subreddit != "True":
        # Change /r/subreddit to the subreddit URL.
        text = reddit.subreddit_to_link(text)

    if disable_replace_reddit_username != "True":
        # Change /u/username to the user URL.
        text = reddit.username_to_link(text)

    if disable_remove_utm_parameters != "True":
        # Remove UTM parameters, this cleans up the URL.
        text = remove.utm_source(text)

    if disable_remove_trailing_whitespace != "True":
        # Remove trailing whitespace.
        text = text.rstrip()

    if disable_remove_copyright_symbols != "True":
        # Remove copyright symbols.
        text = remove.copyright_symbols(text)

    if no_embed == "True":
        send_normal_webhook(msg=text, webhook=webhook_url)

    else:
        send_embed_webhook(
            tweet_id=data.id,
            media_links=media_links,
            text=text,
            twitter_card_image=twitter_card_image,
            avatar_url=avatar,
            screen_name=user_name,
            webhook=webhook_url,
        )


class MyStreamListener(AsyncStreamingClient):
    """https://docs.tweepy.org/en/latest/streaming.html#using-streamingclient.

    Stream tweets in realtime.
    """

    async def on_exception(self, exception: Exception) -> None:  # noqa: ANN101
        """An unhandled exception was raised while streaming. Shutting down."""
        error_msg: str = f"discord-twitter-webhooks: An unhandled exception was raised while streaming. Shutting down\nException: {exception!r}"  # noqa: E501
        send_error_webhook(error_msg)

        self.disconnect()
        sys.exit(error_msg)

    async def on_response(self, response: StreamResponse) -> None:  # noqa: ANN101
        """This is called when a response is received."""
        if response.data:
            main(response)


async def start() -> None:
    """Authenticate to the Twitter API and start the filter."""
    # TODO: Add proxy support?
    stream: MyStreamListener = MyStreamListener(
        settings.bearer_token,
        wait_on_rate_limit=True,
    )

    # Delete old rules
    # TODO: We should only delete the rules we created and if they are changed.
    await delete_old_rules(stream=stream)

    # Create the rules
    rules: dict[int, str] = settings.rules
    for rule_num in rules:
        rule: str = str(rules[rule_num])
        rule_id: str = await new_rule(stream=stream, rule=rule, rule_tag=f"rule{rule_num}")
        settings.logger.info("Rule %s added to Twitter.com", rule_id)
        rule_ids[rule_num] = {rule_id}

    settings.logger.debug("Rule IDs: %s", rule_ids)

    # TODO: dry_run before to make sure everything works?
    try:
        await stream.filter(
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
    asyncio.run(start())
