from reader import Feed, Reader

from discord_twitter_webhooks.include_replies import set_include_replies
from discord_twitter_webhooks.include_retweets import set_include_retweets
from discord_twitter_webhooks.name_already_exists import name_already_exists
from discord_twitter_webhooks.webhook_url import set_webhook_url


def add_new_feed(  # noqa: PLR0913
    name: str,
    webhook_value: str,
    usernames_value: str,
    reader: Reader,
    include_replies: bool,  # noqa: FBT001
    include_retweets: bool,  # noqa: FBT001
) -> str:
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

    # Get all usernames and add them to the reader if they don't exist, or add the new name to the existing feed.
    # Names can be separated by a space to add multiple feeds at once.
    for username in usernames_value.split(" "):
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
