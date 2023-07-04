from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from loguru import logger
from reader import Reader


@dataclass
class Group:
    """The user can add multiple groups, each group can have multiple usernames and webhooks.
    Each group can have its own settings."""

    # TODO: Change username and hashtag URL.
    uuid: str = ""
    name: str = ""
    usernames: list[str] = field(default_factory=list)
    webhooks: list[str] = field(default_factory=list)
    send_retweets: bool = True
    send_replies: bool = True

    # What to send
    send_as_embed: bool = True
    send_as_link: bool = False
    send_as_link_preview: bool = True

    send_as_text: bool = False
    send_as_text_link: bool = False
    send_as_text_link_preview: bool = False
    send_as_text_link_url: str = ""

    # Embed settings
    embed_color: str | Literal["random"] = "#1DA1F2"
    embed_author_name: str = ""
    embed_author_url: str = ""
    embed_author_icon_url: str = ""
    embed_url: str = ""
    embed_timestamp: bool = True
    embed_image: str = ""
    embed_footer_text: str = ""
    embed_footer_icon_url: str = ""
    embed_show_title: bool = False
    embed_show_author: bool = True

    # Other settings
    unescape_html: bool = True
    remove_utm: bool = True
    remove_copyright: bool = True

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ApplicationSettings:
    """Settings for the application."""

    # TODO: Grab every instance from https://github.com/zedeus/nitter/wiki/Instances and use a different one each time we check for new tweets.
    nitter_instance: str = "https://nitter.lovinator.space"
    send_errors_to_discord: bool = False
    error_webhook: str = ""

    def __post_init__(self) -> None:
        self.nitter_instance = self.nitter_instance.rstrip("/")

        if self.send_errors_to_discord and not self.error_webhook:
            logger.warning("send_errors_to_discord is True, but no error_webhook is set. Disabling.")
            self.send_errors_to_discord = False


def get_app_settings(reader: Reader) -> ApplicationSettings:
    """Get the application settings."""
    app_settings = reader.get_tag((), "app_settings", ApplicationSettings())
    logger.debug("Got application settings: {}", app_settings)
    return ApplicationSettings(**app_settings)


def set_app_settings(reader: Reader, app_settings: ApplicationSettings) -> None:
    """Set the application settings."""
    reader.set_tag((), "app_settings", app_settings.__dict__)
    logger.debug("Saved application settings: {}", app_settings)


def get_group(reader: Reader, uuid: str) -> Group:
    """Get the group."""
    group = reader.get_tag((), uuid, Group())
    logger.debug("Got group: {}", group)
    return Group(**group)


def set_group(reader: Reader, uuid: str, group: Group) -> None:
    """Set the group."""
    reader.set_tag((), uuid, group.__dict__)
    logger.debug("Saved group: {}", group)
