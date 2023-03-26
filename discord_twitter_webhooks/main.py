import asyncio
import html
import sys
from typing import Any

from loguru import logger
from tweepy.asynchronous import AsyncStreamingClient
from tweepy.streaming import StreamResponse

from discord_twitter_webhooks import get, reddit, remove, replace, settings
from discord_twitter_webhooks.get import (
    UserInformation,
    get_entities,
    get_text,
    get_user_information,
    get_webhook_url,
)
from discord_twitter_webhooks.rules import delete_old_rules, new_rule
from discord_twitter_webhooks.send_webhook import (
    send_embed_webhook,
    send_error_webhook,
    send_hook_and_files,
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
    logger.debug("Response: {}", response)

    text: str = get_text(response)

    media_links: list[str] = get_media_links(response)

    twitter_card_image: str = ""
    if (entities := get_entities(response)) and "urls" in entities:
        text = remove.remove_media_links(entities, text)
        twitter_card_image = get.meta_image(entities)

        # Replace Twitters shortened URLs with the original URL.
        if disable_remove_tco_links:
            text = replace.tco_url_link_with_real_link(entities, text)

    # We coverts &gt; and &lt; to > and < to make the text look nicer.
    if disable_unescape_text:
        text = html.unescape(text)

    # Replace the @mentions with URLs.
    if disable_replace_username:
        text = replace.username_with_link(text)

    # Replace the hashtags with URLs.
    if disable_replace_hashtag:
        text = replace.hashtag_with_link(text)

    # Append < and > to disable Discords link previews.
    if disable_remove_discord_link_previews:
        text = remove.discord_link_previews(text)

    # Change /r/subreddit to the subreddit URL.
    if disable_replace_subreddit:
        text = reddit.subreddit_to_link(text)

    # Change /u/username to the user URL.
    if disable_replace_reddit_username:
        text = reddit.username_to_link(text)

    # Remove UTM parameters, this cleans up the URL.
    if disable_remove_utm_parameters:
        text = remove.utm_source(text)

    # Remove trailing whitespace.
    if disable_remove_trailing_whitespace:
        text = text.rstrip()

    # Remove copyright symbols.
    if disable_remove_copyright_symbols:
        text = remove.copyright_symbols(text)

    user_info: UserInformation = get_user_information(response)
    webhook_url: str = get_webhook_url(response)
    data = response.data

    # If we should only send the link to the tweet.
    if settings.only_link:
        if settings.only_link_preview:
            msg: str = f"https://twitter.com/{user_info.username}/status/{data.id}"
        else:
            msg = f"<https://twitter.com/{user_info.username}/status/{data.id}>"
        send_hook_and_files(media_links, msg, webhook_url)

    elif settings.no_embed:
        if msg := no_embed_stuff(
            media_links,
            user_info,
            text,
            data.id,
        ):
            send_hook_and_files(media_links, msg, webhook_url)
    else:
        send_embed_webhook(
            tweet_id=data.id,
            media_links=media_links,
            text=text,
            twitter_card_image=twitter_card_image,
            avatar_url=user_info.avatar_url,
            display_name=user_info.display_name,
            webhook=webhook_url,
            username=user_info.username,
        )


def get_media_links(response: StreamResponse) -> list[str]:
    """Get the media links from the tweet.

    Media links can be images, videos or gifs.

    Args:
        response: The response from the Twitter API.

    Returns:
        A list of media links.
    """
    # TODO: Add actual .mp4 or add play button overlay so you can see that it's a video
    media_links: list[str] = []
    if response.includes:
        includes: dict[str, list[Any]] = response.includes
        if "media" in includes:
            media_list: list[dict] = [media.data for media in response.includes["media"]]
            logger.debug("Media list: {}", media_list)

            for image in media_list:
                if image["type"] == "photo":
                    media_links.append(image["url"])
                elif image["type"] in ["animated_gif", "video"]:
                    media_links.append(image["preview_image_url"])

                logger.debug("Image added: {}", image)
    return media_links


def no_embed_stuff(
    media_links: list[str],
    user_information: UserInformation,
    text: str,
    tweet_id: int,
) -> str:
    """Send a webhook with the tweet text or as a link to the tweet.

    You can also append the media links to the message.

    Args:
        media_links: A list of media links.
        user_information: The user information.
        text: The tweet text.
        tweet_id: The tweet ID.

    Returns:
        The message to send.
    """
    if settings.make_text_link:
        if settings.make_text_link_twitter_preview:
            url: str = f"https://twitter.com/{user_information.username}/status/{tweet_id}"
        else:
            url: str = f"<https://twitter.com/{user_information.username}/status/{tweet_id}>"

        # If we should use a custom URL instead of the tweet URL.
        if settings.make_text_link_custom_url:
            url = settings.make_text_link_custom_url

        # Create the message.
        msg: str = f"[{text}]({url})"

        # If we should append the media links.
        if settings.append_image_links:
            for media_link in media_links:
                msg += f"\n{media_link}"

        # Send only the link.
        return msg
    return text


class MyStreamListener(AsyncStreamingClient):
    """https://docs.tweepy.org/en/latest/streaming.html#using-streamingclient.

    Stream tweets in realtime.
    """

    async def on_exception(self, exception: Exception) -> None:  # noqa: ANN101
        """An unhandled exception was raised while streaming. Shutting down."""
        error_msg: str = f"discord-twitter-webhooks: An unhandled exception was raised while streaming. Shutting down\nException: {exception}"  # noqa: E501
        send_error_webhook(error_msg)

        self.disconnect()
        sys.exit(error_msg)

    async def on_response(self, response: StreamResponse) -> None:  # noqa: ANN101
        """This is called when a response is received."""
        if response.data:
            main(response)


async def start_bot() -> None:
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
        rule_ids[rule_num] = {rule_id}

    logger.debug("Rule IDs: {}", rule_ids)

    # TODO: dry_run before to make sure everything works?
    # TODO: We should remove everything that is not needed.
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
        logger.info("Bye!")
        stream.disconnect()
        sys.exit(0)


def start() -> None:
    """Start the bot."""
    asyncio.run(start_bot())


if __name__ == "__main__":
    start()
