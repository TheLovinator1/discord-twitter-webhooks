from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from loguru import logger
from reader import Reader, TagNotFoundError


@dataclass
class Group:
    """The user can add multiple groups, each group can have multiple usernames and webhooks."""

    uuid: str = ""
    name: str = ""
    usernames: list[str] = field(default_factory=list)
    webhooks: list[str] = field(default_factory=list)
    rss_feeds: list[str] = field(default_factory=list)
    send_retweets: bool = True
    send_replies: bool = False
    only_send_if_media: bool = False

    # What to send
    send_as_embed: bool = True
    send_as_link: bool = False
    send_as_text: bool = False
    send_as_text_username: bool = True

    # Translate settings
    translate: bool = False
    translate_to: str = "en-GB"
    translate_from: str = "auto"

    # Other settings
    unescape_html: bool = True
    remove_copyright: bool = True

    # Where hyperlink should point to
    link_destination: Literal["Twitter", "Nitter"] = "Twitter"
    replace_youtube: bool = False
    replace_reddit: bool = False

    # Whitelist/blacklist
    whitelist_enabled: bool = False
    whitelist: list[str] = field(default_factory=list)
    whitelist_regex: list[str] = field(default_factory=list)
    blacklist_enabled: bool = False
    blacklist: list[str] = field(default_factory=list)
    blacklist_regex: list[str] = field(default_factory=list)

    created_at: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())


@dataclass
class ApplicationSettings:
    """Settings for the application."""

    # TODO: Grab every instance from https://github.com/zedeus/nitter/wiki/Instances and use a different one each
    #  time we check for new tweets.
    # The Nitter instance where we will get the RSS feed from
    nitter_instance: str = "https://nitter.lovinator.space"

    # DeepL API key used for translating tweets
    deepl_auth_key: str = ""

    # Piped/Invidious instance if the user wants to replace YouTube links
    piped_instance: str = "https://piped.video"

    # Teddit/Libreddit instance if the user wants to replace Reddit links
    teddit_instance: str = "https://teddit.net"

    def __post_init__(self: "ApplicationSettings") -> None:
        """Don't allow trailing slashes."""
        self.nitter_instance = self.nitter_instance.rstrip("/")
        self.piped_instance = self.piped_instance.rstrip("/")
        self.teddit_instance = self.teddit_instance.rstrip("/")


def get_app_settings(reader: Reader) -> ApplicationSettings:
    """Get the application settings."""
    try:
        app_settings = reader.get_tag((), "app_settings")
    except TagNotFoundError:
        logger.info("Applying default application settings. You can change these in the Settings menu.")
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
        return Group(
            uuid=group.get("uuid", uuid),
            name=group.get("name", Group.name),
            usernames=group.get("usernames", []),
            webhooks=group.get("webhooks", []),
            rss_feeds=group.get("rss_feeds", []),
            send_retweets=group.get("send_retweets", Group.send_retweets),
            send_replies=group.get("send_replies", Group.send_replies),
            only_send_if_media=group.get("only_send_if_media", Group.only_send_if_media),
            send_as_embed=group.get("send_as_embed", Group.send_as_embed),
            send_as_link=group.get("send_as_link", Group.send_as_link),
            send_as_text=group.get("send_as_text", Group.send_as_text),
            send_as_text_username=group.get("send_as_text_username", Group.send_as_text_username),
            translate=group.get("translate", Group.translate),
            translate_to=group.get("translate_to", Group.translate_to),
            translate_from=group.get("translate_from", Group.translate_from),
            unescape_html=group.get("unescape_html", Group.unescape_html),
            remove_copyright=group.get("remove_copyright", Group.remove_copyright),
            link_destination=group.get("link_destination", Group.link_destination),
            whitelist_enabled=group.get("whitelist_enabled", Group.whitelist_enabled),
            whitelist=group.get("whitelist", []),
            whitelist_regex=group.get("whitelist_regex", []),
            blacklist_enabled=group.get("blacklist_enabled", Group.blacklist_enabled),
            blacklist=group.get("blacklist", []),
            blacklist_regex=group.get("blacklist_regex", []),
            replace_reddit=group.get("replace_reddit", Group.replace_reddit),
            replace_youtube=group.get("replace_youtube", Group.replace_youtube),
            created_at=group.get("created_at", datetime.now(tz=timezone.utc).isoformat()),
        )
    except TagNotFoundError:
        logger.info("Group {} not found.", uuid)
