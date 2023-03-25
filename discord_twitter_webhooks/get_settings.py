import os
import re
import sys
from urllib.parse import urlparse

from loguru import logger


def get_hook_and_rule() -> tuple[dict[int, str], dict[int, str]]:
    """Get webhook and rule with the corresponding number.

    For example:
        WEBHOOK_URL1 goes with RULE1.
        WEBHOOK_URL5 goes with RULE5.
    """
    webhooks: dict[int, str] = {}
    rules: dict[int, str] = {}
    for rule_name, rule_value in os.environ.items():
        # Check for single rule
        if rule_name == "RULE":
            single_rule(rule_value, rules, webhooks)
        elif rule_name.startswith("RULE"):
            # Get digits at the end of the string
            match: re.Match[str] | None = re.search(r"\d+$", rule_name)
            get_digit: int | None = int(match.group()) if match else None

            # If we can't get the digit, log an error and continue.
            if get_digit is None:
                logger.error(
                    "I couldn't figure out what {} was when parsing {}. Contact TheLovinator if this should work.",
                    get_digit,
                    rule_name,
                )
            else:
                # Remove " and ' from the start and end if they exist
                rules[get_digit] = rule_value.strip("'").strip('"')

                webhooks[get_digit] = os.getenv(f"WEBHOOK_URL{get_digit}")  # type: ignore
                if webhooks[get_digit] is None:
                    logger.error("webhook is None for {}", get_digit)
                    sys.exit("I failed to get WEBHOOK_URL")

                # Remove " and ' from the start and end if they exist
                webhooks[get_digit] = webhooks[get_digit].strip("'").strip('"')

                logger.debug("Rule {}: {} will get sent to {}", get_digit, rule_value, webhooks[get_digit])
    return webhooks, rules


def single_rule(rule_value: str, rules: dict[int, str], webhooks: dict[int, str]) -> None:
    """Get the single rule.

    Args:
        rule_value: The value of the rule.
        rules: The rule.
        webhooks: The webhook or webhooks.
    """
    # TODO: Should we return something in this function?

    # Remove " and ' from the start and end if they exist
    rules[0] = rule_value.strip("'").strip('"')

    webhooks[0] = os.getenv("WEBHOOK_URL", default="")

    if webhooks[0] is None:
        logger.error("Webhook is None for Rule 0")
        sys.exit("I failed to get WEBHOOK_URL")

    # Remove " and ' from the start and end if they exist
    webhooks[0] = webhooks[0].strip("'").strip('"')

    # If we can't get the webhook, exit.
    if not webhooks[0]:
        sys.exit("I failed to get WEBHOOK_URL")

    logger.debug("Rule 0: {} will get sent to {}", rule_value, webhooks[0])


def get_setting_value(setting_name: str, default_value: bool) -> bool:
    """Get the setting value from the environment.

    Args:
        setting_name (str): The name of the setting.
        default_value (bool): The default value of the setting.

    Returns:
        str: The value of the setting.
    """
    env_var: str = os.getenv(setting_name, default="")
    if env_var.lower() in {"n", "no", "false", "off", "0", "disable", "disabled"}:
        logger.debug("'{}' is set to '{}', disabling.", setting_name, env_var)
        return False
    if env_var.lower() in {"y", "yes", "true", "on", "1", "enable", "enabled"}:
        logger.debug("'{}' is set to '{}', enabling.", setting_name, env_var)
        return True
    logger.debug(
        "Failed to get a valid value for '{}' which is set to '{}'. Defaulting to '{}'.",
        setting_name,
        env_var,
        default_value,
    )
    return default_value


def get_bearer_token() -> str:
    bearer_token: str = os.getenv("BEARER_TOKEN", default="")
    if not bearer_token:
        sys.exit("No bearer token found in .env file or environment variables.")
    return bearer_token


def get_log_level() -> str:
    """Get the log level from the environment.

    Returns:
        str: The log level. Defaults to "INFO".
    """
    log_levels: list[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    log_level: str = os.getenv("LOG_LEVEL", default="INFO")
    if log_level not in log_levels:
        logger.warning(
            "LOG_LEVEL is set to {}, which is not a valid value. Defaulting to INFO.",
            log_level,
        )
    return log_level


def get_send_errors() -> bool:
    """Get the send errors setting from the environment.

    If we should send errors to Discord.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="SEND_ERRORS", default_value=False)


def warn_if_http(url: str, hook_name: str) -> None:
    if urlparse(url).scheme == "http":
        logger.warning("{} should probably be a https url do to security reasons.", hook_name)


def get_error_webhook() -> str:
    """Get the error webhook from the environment.

    The webhook to send errors to.

    Returns:
        str: The error webhook. Defaults to "".
    """
    # Only get the error webhook if we should send errors.
    value: str = os.getenv("ERROR_WEBHOOK", default="")
    if not get_setting_value(setting_name="SEND_ERRORS", default_value=False):
        logger.warning("SEND_ERRORS is set to False, but ERROR_WEBHOOK is set to '{}'.", value)
    return value


def get_webhook_author_name(author_name: str = "", max_author_name_length: int = 236) -> str:
    """Customize the name of the webhook author.

    Embed titles can be up to 256 characters.
    256 (max title) - 15 (max username) - 2 (spaces) - 1 (@) - 2 (parenthesis) = 236

    Args:
        author_name: The name of the webhook author.
        max_author_name_length: The maximum length of the webhook author name.

    Returns:
        str: The webhook author name. Defaults to "".
    """
    if not author_name:
        author_name = os.getenv("WEBHOOK_AUTHOR_NAME", default="")
    if len(author_name) > max_author_name_length:
        logger.warning("WEBHOOK_AUTHOR_NAME has to be less than 236 characters. It will be truncated.")
        author_name = author_name[:max_author_name_length]
    return author_name


def get_webhook_author_url(author_url: str = "") -> str:
    """Customize the url of the webhook author.

    Args:
        author_url: Custom url for the webhook author. Otherwise defaults to the env var or "".

    Returns:
        str: The webhook author url. Defaults to "".
    """
    if not author_url:
        author_url = os.getenv("WEBHOOK_AUTHOR_URL", default="")
    warn_if_http(author_url, "WEBHOOK_AUTHOR_URL")
    return author_url


def get_webhook_author_icon(author_icon: str = "") -> str:
    """Customize the icon of the webhook author.

    Args:
        author_icon: Custom icon for the webhook author. Otherwise defaults to the env var or "".

    Returns:
        str: The webhook author icon. Defaults to "".
    """
    if not author_icon:
        author_icon = os.getenv("WEBHOOK_AUTHOR_ICON", default="")
    warn_if_http(author_icon, "WEBHOOK_AUTHOR_ICON")
    return author_icon


def get_webhook_image(webhook_image: str = "") -> str:
    """Customize the image of the webhook.

    Args:
        webhook_image: Custom image for the webhook. Otherwise defaults to the env var or "".

    Returns:
        str: The webhook image. Defaults to "".
    """
    if not webhook_image:
        os.getenv("WEBHOOK_IMAGE", default="")
    warn_if_http(webhook_image, "WEBHOOK_IMAGE")
    return webhook_image


def get_webhook_thumbnail(webhook_thumbnail: str = "") -> str:
    """Customize the thumbnail of the webhook.

    Args:
        webhook_thumbnail: Custom thumbnail for the webhook. Otherwise defaults to the env var or "".

    Returns:
        str: The webhook thumbnail. Defaults to "".
    """
    if not webhook_thumbnail:
        os.getenv("WEBHOOK_THUMBNAIL", default="")
    warn_if_http(webhook_thumbnail, "WEBHOOK_THUMBNAIL")
    return webhook_thumbnail


def get_webhook_footer_text(footer_text: str = "") -> str:
    """Customize the footer text of the webhook.

    Returns:
        str: The webhook footer text. Defaults to "".
    """
    # The footer text is limited to 2048 characters
    max_footer_length: int = 2047
    env_name: str = "WEBHOOK_FOOTER_TEXT"
    if not footer_text:
        footer_text = os.getenv(env_name, default="")
    if len(footer_text) > max_footer_length:
        logger.warning(
            "{} has to be less than {} characters. It will be truncated.",
            env_name,
            max_footer_length,
        )
        footer_text = footer_text[:max_footer_length]
    return footer_text


def get_webhook_footer_icon() -> str:
    """Customize the footer icon of the webhook.

    Returns:
        str: The webhook footer icon. Defaults to "". If WEBHOOK_FOOTER_TEXT is not set, this will also return "".
    """
    # TODO: Check if valid url.
    value: str = os.getenv("WEBHOOK_FOOTER_ICON", default="")
    if value and not os.getenv("WEBHOOK_FOOTER_TEXT", default=""):
        logger.warning(
            (
                "WEBHOOK_FOOTER_ICON is set, but WEBHOOK_FOOTER_TEXT is not. I think you need to enable this to show"
                " the icon."
            ),
        )
    return value


def get_show_timestamp() -> bool:
    """If we should show the timestamp in the embed.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    return get_setting_value(setting_name="SHOW_TIMESTAMP", default_value=True)


def get_no_embed() -> bool:
    """If we should send the text only, without an embed.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="NO_EMBED", default_value=False)


def get_make_text_link() -> bool:
    """If we should make the tweet text a link to the tweet.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    value: bool = get_setting_value(setting_name="MAKE_TEXT_LINK", default_value=False)
    if value and not get_no_embed():
        logger.warning(
            "You need to set NO_EMBED to True to use MAKE_TEXT_LINK. Defaulting to False.",
        )
        return False
    return value


def get_make_text_link_twitter_embed() -> bool:
    """If we should make the tweet text a link to the tweet.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    value: bool = get_setting_value(setting_name="MAKE_TEXT_LINK_TWITTER_EMBED", default_value=False)
    if value and not get_no_embed():
        logger.warning(
            "You need to set NO_EMBED to True to use MAKE_TEXT_LINK_TWITTER_EMBED. Defaulting to False.",
        )
        return False

    return value


def get_make_text_link_url() -> str:
    """The URL to use for the tweet text link. It defaults to the tweet URL if not set.

    Returns:
        str: The value of the setting. If it is "" it will default to "https://twitter.com/{username}/web/status/{tweet_id}".
    """  # noqa: E501
    value: str = os.getenv("MAKE_TEXT_LINK_URL", default="")
    if value:
        if not get_make_text_link():
            logger.warning(
                "You need to set MAKE_TEXT_LINK to True to use MAKE_TEXT_LINK_URL. Defaulting to tweet URL.",
            )
            return ""
        if not get_no_embed():
            logger.warning(
                "You need to set NO_EMBED to True to use MAKE_TEXT_LINK.",
            )
            return ""
    return value


def get_use_title() -> bool:
    """If we should set the embed title to the tweet authors name.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="USE_TITLE", default_value=False)


def get_use_author() -> bool:
    """If we should set the embed author to the tweet authors name.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    return get_setting_value(setting_name="USE_AUTHOR", default_value=True)


def get_disable_remove_tco_links() -> bool:
    """If we should disable removing t.co links.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_REMOVE_TCO_LINKS", default_value=False)


def get_disable_unescape_text() -> bool:
    """If we should not unescape the tweet text.

    Unescaping text means that we replace HTML entities with their unicode equivalent.
    For example, "&amp;" becomes "&".

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_UNESCAPE_TEXT", default_value=False)


def get_disable_replace_username() -> bool:
    """If we should disable replacing usernames with mentions.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_REPLACE_USERNAME", default_value=False)


def get_disable_replace_hashtag() -> bool:
    """If we should disable replacing hashtags with links.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_REPLACE_HASHTAG", default_value=False)


def get_disable_remove_discord_link_previews() -> bool:
    """If we should disable replacing urls with links.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_REMOVE_DISCORD_LINK_PREVIEWS", default_value=False)


def get_disable_replace_subreddit() -> bool:
    """If we should disable replacing urls with links.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_REPLACE_SUBREDDIT", default_value=False)


def get_disable_replace_reddit_username() -> bool:
    """If we should disable replacing urls with links.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_REPLACE_REDDIT_USERNAME", default_value=False)


def get_disable_remove_utm_parameters() -> bool:
    """If we should disable replacing urls with links.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_REMOVE_UTM", default_value=False)


def get_disable_remove_trailing_whitespace() -> bool:
    """If we should disable removing trailing whitespace.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_REMOVE_TRAILING_WHITESPACE", default_value=False)


def get_disable_remove_copyright_symbols() -> bool:
    """If we should disable removing copyright symbols.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="DISABLE_REMOVE_COPYRIGHT_SYMBOLS", default_value=False)


def get_webhook_show_timestamp() -> bool:
    """If we should disable removing emoji.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="SHOW_TIMESTAMP", default_value=False)

def get_embed_colors() -> bool:
    """If we should use a random color in the embed.
    Returns:
        bool: The value of the setting. Defaults to False.
    """
    return get_setting_value(setting_name="RANDOM_EMBED_COLORS", default_value=False)
