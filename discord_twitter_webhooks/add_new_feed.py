from reader import Feed, Reader

from discord_twitter_webhooks.name_already_exists import name_already_exists
from discord_twitter_webhooks.send_text import set_send_text
from discord_twitter_webhooks.set_settings.append_usernames import set_append_usernames
from discord_twitter_webhooks.set_settings.blacklist import (
    set_blacklist_active,
    set_blacklist_words,
)
from discord_twitter_webhooks.set_settings.embed import (
    set_embed_author_icon_url,
    set_embed_author_name,
    set_embed_author_url,
    set_embed_color,
    set_embed_footer_icon_url,
    set_embed_footer_text,
    set_embed_image,
    set_embed_show_author,
    set_embed_show_title,
    set_embed_timestamp,
    set_embed_url,
    set_send_embed,
)
from discord_twitter_webhooks.set_settings.hashtag_link import (
    set_hashtag_link,
    set_hashtag_link_destination,
)
from discord_twitter_webhooks.set_settings.include_retweets import set_include_retweets
from discord_twitter_webhooks.set_settings.includes_replies import set_include_replies
from discord_twitter_webhooks.set_settings.make_text_a_link import (
    set_make_text_a_link,
    set_make_text_a_link_preview,
    set_make_text_a_link_url,
)
from discord_twitter_webhooks.set_settings.remove_copyright_symbols import (
    set_remove_copyright_symbols,
)
from discord_twitter_webhooks.set_settings.remove_utm import set_remove_utm
from discord_twitter_webhooks.set_settings.send_only_link import (
    set_send_only_link,
    set_send_only_link_preview,
)
from discord_twitter_webhooks.set_settings.set_webhook_url import set_webhook_url
from discord_twitter_webhooks.set_settings.translate import (
    set_translate,
    set_translate_from,
    set_translate_to,
)
from discord_twitter_webhooks.set_settings.unescape_html import set_unescape_html
from discord_twitter_webhooks.set_settings.upload_media import set_upload_media
from discord_twitter_webhooks.set_settings.username_link import (
    set_username_link,
    set_username_link_destination,
)
from discord_twitter_webhooks.set_settings.whitelist import (
    set_whitelist_active,
    set_whitelist_words,
)


def create_group(
    name: str,
    webhook_value: str,
    usernames_value: str,
    reader: Reader,
    include_replies: bool,  # noqa: FBT001
    include_retweets: bool,  # noqa: FBT001
    send_text: bool,  # noqa: FBT001
    send_embed: bool,  # noqa: FBT001
    embed_color: str,
    embed_author_name: str,
    embed_author_url: str,
    embed_author_icon_url: str,
    embed_url: str,
    embed_timestamp: str,
    embed_image: str,
    embed_footer_text: str,
    embed_footer_icon_url: str,
    embed_show_title: bool,  # noqa: FBT001
    embed_show_author: bool,  # noqa: FBT001
    send_only_link: bool,  # noqa: FBT001
    send_only_link_preview: bool,  # noqa: FBT001
    make_text_a_link: bool,  # noqa: FBT001
    make_text_a_link_preview: bool,  # noqa: FBT001
    make_text_a_link_url: str,
    upload_media: bool,  # noqa: FBT001
    append_usernames: bool,  # noqa: FBT001
    translate: bool,  # noqa: FBT001
    translate_to: str,
    translate_from: str,
    whitelist_words: str,
    whitelist_active: bool,  # noqa: FBT001
    blacklist_words: str,
    blacklist_active: bool,  # noqa: FBT001
    unescape_html: bool,  # noqa: FBT001
    remove_utm: bool,  # noqa: FBT001
    remove_copyright: bool,  # noqa: FBT001
    convert_usernames_to_links: bool,  # noqa: FBT001
    username_link_destination: str,
    convert_hashtags_to_links: bool,  # noqa: FBT001
    hashtag_link_destination: str,
) -> str:
    """Create a new group. A group is a collection of feeds that are sent to the same Discord webhook.

    Each group has a name, a webhook URL, and a list of usernames. The list of usernames is a newline separated list.
    You can also choose whether or not to include replies and retweets.

    Args:
        name: The name of the group.
        webhook_value: What the webhook URL should be set to.
        usernames_value: What usernames we should be following. This is a newline separated list.
        reader: What reader we should be using.
        include_replies: Whether or not we should send replies to Discord.
        include_retweets: Whether or not we should send retweets to Discord.
        send_text: Whether or not we should send the text of the tweet to Discord.

    Returns:
        A string that can be returned to the user.
    """
    # Check if name contains a semicolon
    if ";" in name:
        # TODO: Return our previous values
        return (
            f"Error, name cannot contain a semicolon.\n\nPlease go back and try again.\nName: '{name}'\n"
            f"Webhook: '{webhook_value}'\nUsernames: '{usernames_value}'"
        )

    if name_already_exists(reader=reader, name=name):
        return (
            f"Error, name already exists.\n\nPlease go back and try again.\nName: '{name}'\n"
            f"Webhook: '{webhook_value}'\nUsernames: '{usernames_value}'"
        )

    # Add our new global tags
    set_webhook_url(reader, name, webhook_value)
    set_include_retweets(reader, name, include_retweets)
    set_include_replies(reader, name, include_replies)

    set_send_text(reader, name, send_text)

    set_send_embed(reader, name, send_embed)
    set_embed_color(reader, name, embed_color)
    set_embed_author_name(reader, name, embed_author_name)
    set_embed_author_url(reader, name, embed_author_url)
    set_embed_author_icon_url(reader, name, embed_author_icon_url)
    set_embed_url(reader, name, embed_url)
    set_embed_timestamp(reader, name, embed_timestamp)
    set_embed_image(reader, name, embed_image)
    set_embed_footer_text(reader, name, embed_footer_text)
    set_embed_footer_icon_url(reader, name, embed_footer_icon_url)

    set_embed_show_title(reader, name, embed_show_title)
    set_embed_show_author(reader, name, embed_show_author)

    set_send_only_link(reader, name, send_only_link)
    set_send_only_link_preview(reader, name, send_only_link_preview)
    set_make_text_a_link(reader, name, make_text_a_link)
    set_make_text_a_link_preview(reader, name, make_text_a_link_preview)
    set_make_text_a_link_url(reader, name, make_text_a_link_url)

    set_upload_media(reader, name, upload_media)
    set_append_usernames(reader, name, append_usernames)

    set_translate(reader, name, translate)
    set_translate_to(reader, name, translate_to)
    set_translate_from(reader, name, translate_from)

    set_whitelist_words(reader, name, whitelist_words)
    set_whitelist_active(reader, name, whitelist_active)
    set_blacklist_words(reader, name, blacklist_words)
    set_blacklist_active(reader, name, blacklist_active)

    set_unescape_html(reader, name, unescape_html)
    set_remove_utm(reader, name, remove_utm)
    set_remove_copyright_symbols(reader, name, remove_copyright)

    set_username_link(reader, name, convert_usernames_to_links)
    set_username_link_destination(reader, name, username_link_destination)
    set_hashtag_link(reader, name, convert_hashtags_to_links)
    set_hashtag_link_destination(reader, name, hashtag_link_destination)

    # Get all usernames and add them to the reader if they don't exist, or add the new name to the existing feed.
    # Names can be separated by a space to add multiple feeds at once.

    # Check what type of newline is used
    usernames: list[str] = usernames_value.split("\r\n") if "\r\n" in usernames_value else usernames_value.split("\n")

    for username in usernames:
        # Create the Nitter RSS feed URL
        feed_url: str = f"https://nitter.lovinator.space/{username}/rss"

        # Check if the feed already exists
        for feed in reader.get_feeds():
            # Each feed has a name tag, webhooks and include_retweets and include_replies will be added
            # as global tag named "name_webhook", "name_include_retweets" and "name_include_replies
            # For example, if the name is "TheLovinator", the webhook will be "TheLovinator_webhook", the
            # include_retweets will be "TheLovinator_include_retweets" and the include_replies will
            # be "TheLovinator_include_replies"
            if feed.url == feed_url:
                # Get the old name and append the new name to it, this will be used when getting the global tags
                old_name: str | None = str(reader.get_tag(feed, "name"))
                if old_name is None:
                    # TODO: Make this better, we should return a template with a message instead of just a string
                    return (
                        f"Error, failed to get old name when adding new name to it.\n\nFeed URL: '{feed_url}'\nOld"
                        f" name: '{old_name}'\nNew name: '{name}'"
                    )

                # Add the new name to the old name. For example, if the old name is "TheLovinator" and the new name is
                # "TheLovinator2", the new name will be "TheLovinator;TheLovinator2"
                new_name: str = f"{old_name};{name}"

                # Set the names as the tag
                # We will use this to get the webhooks and include_retweets and include_replies later when sending
                # the feed to Discord
                reader.set_tag(feed, "name", new_name)  # type: ignore  # noqa: PGH003

                # Update the feed
                reader.update_feed(feed)

                # Mark all old entries as read so we don't send them to Discord
                for entry in reader.get_entries(feed=feed):
                    reader.mark_entry_as_read(entry)

                # TODO: Make this better, we should return a template with a message instead of just a string
                return (
                    f"Added '{name}' to the existing feed for '{username}'. Before it was '{old_name}'. Now it is"
                    f" '{new_name}'."
                )

        # If the feed doesn't exist, add it
        reader.add_feed(feed_url, exist_ok=True)

        feed: Feed = reader.get_feed(feed_url)

        # Add the name as a tag
        reader.set_tag(feed, "name", name)  # type: ignore  # noqa: PGH003

        # TODO: Make this better, we should return a template with a message instead of just a string
        if name is None:
            return (
                f"Error, name was None.\n\nPlease go back and try again.\nName: '{name}'\n"
                f"Webhook: '{webhook_value}'\nUsernames: '{usernames_value}'"
            )

        # Update the feed
        reader.update_feed(feed)

        # Mark all old entries as read so we don't send them to Discord
        for entry in reader.get_entries(feed=feed):
            reader.mark_entry_as_read(entry)

    # TODO: Make this better, we should return a template with a message instead of just a string
    return (
        f"Added new group '{name}' with usernames '{usernames_value}'.\n\nWebhook: '{webhook_value}'\nInclude retweets:"
        f" '{include_retweets}'\nInclude replies: '{include_replies}'"
    )
