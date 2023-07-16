from dataclasses import dataclass, field
from datetime import datetime, timezone

from loguru import logger
from reader import Reader, TagNotFoundError


@dataclass
class Group:
    """The user can add multiple groups, each group can have multiple usernames and webhooks."""

    # TODO: Change username and hashtag URL.
    uuid: str = ""
    name: str = ""
    usernames: list[str] = field(default_factory=list)
    webhooks: list[str] = field(default_factory=list)
    rss_feeds: list[str] = field(default_factory=list)
    send_retweets: bool = True
    send_replies: bool = False

    # What to send
    send_as_embed: bool = True

    # Send as a link to the tweet
    send_as_link: bool = False

    # Send as the text of the tweet
    send_as_text: bool = False
    # If we should append the username to the text
    send_as_text_username: bool = True

    # Translate settings
    translate: bool = False
    translate_to: str = "en-GB"
    translate_from: str = "auto"

    # Other settings
    unescape_html: bool = True
    remove_copyright: bool = True

    created_at: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())


@dataclass
class ApplicationSettings:
    """Settings for the application."""

    # TODO: Grab every instance from https://github.com/zedeus/nitter/wiki/Instances and use a different one each
    #  time we check for new tweets.
    nitter_instance: str = "https://nitter.lovinator.space"
    deepl_auth_key: str = ""

    def __post_init__(self: "ApplicationSettings") -> None:
        self.nitter_instance = self.nitter_instance.rstrip("/")


def get_app_settings(reader: Reader) -> ApplicationSettings:
    """Get the application settings."""
    try:
        app_settings = reader.get_tag((), "app_settings")
    except TagNotFoundError:
        logger.info("You should fill out the application settings.")
        set_app_settings(reader, ApplicationSettings())
        return ApplicationSettings()

    logger.debug("Got application settings: {}", app_settings)
    return ApplicationSettings(**app_settings)


def set_app_settings(reader: Reader, app_settings: ApplicationSettings) -> None:
    """Set the application settings."""
    reader.set_tag((), "app_settings", app_settings.__dict__)
    logger.debug("Saved application settings: {}", app_settings)


def get_group(reader: Reader, uuid: str) -> Group:
    """Get the group."""
    try:
        group = reader.get_tag((), uuid)
        return Group(**group)
    except TagNotFoundError:
        logger.info("Group {} not found.", uuid)
