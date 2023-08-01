from loguru import logger
from reader import FeedExistsError, FeedNotFoundError, InvalidFeedURLError, Reader

from discord_twitter_webhooks._dataclasses import Group, get_app_settings, get_group
from discord_twitter_webhooks.reader_settings import get_reader


def replace_nitter_instance(new_nitter_instance: str) -> str:  # noqa: C901
    """Replace the Nitter instance.

    Args:
        new_nitter_instance: The new Nitter instance.

    Returns:
        str: Empty string if successful, otherwise an error message.
    """

    def log_and_return(_feed: str, _msg: str) -> str:
        msg: str = f"Feed {_feed}{_msg}"
        logger.info(msg)
        return msg

    reader: Reader = get_reader()

    # Replace the Nitter instance if it has changed
    old_nitter_instance: str = get_app_settings(reader).nitter_instance
    if old_nitter_instance != new_nitter_instance:
        logger.info(f"Nitter instance changed from {old_nitter_instance} to {new_nitter_instance}")

        # Change the URL of a feed.
        for _feed in reader.get_feeds():
            try:
                reader.change_feed_url(_feed, _feed.url.replace(old_nitter_instance, new_nitter_instance))
                logger.info(f"Changed feed {_feed.url} to use new Nitter instance")
            except FeedNotFoundError:
                return log_and_return(_feed.url, " not found, skipping")
            except FeedExistsError:
                return log_and_return(_feed.url, " already exists, skipping")
            except InvalidFeedURLError:
                return log_and_return(_feed.url, " has an invalid URL, skipping")

        # Change group.rss_feeds to use the new Nitter instance.
        for _group in list(reader.get_tag((), "groups", [])):
            group: Group = get_group(reader, str(_group))
            if not group:
                logger.error("Group {} not found", _group)
                continue

            for group_feed in group.rss_feeds:
                if not group_feed:
                    logger.warning("Group {} has an empty feed", _group)
                    continue

                # Replace the Nitter instance if it has changed
                group.rss_feeds[group.rss_feeds.index(group_feed)] = group_feed.replace(
                    old_nitter_instance,
                    new_nitter_instance,
                )

            # Save the group
            reader.set_tag((), group.uuid, group.__dict__)

    return ""
