import json
import os
import re
import sys
from urllib.parse import urlparse

import requests
from loguru import logger


def get_hook_and_rule() -> tuple[dict[int, str], dict[int, str]]:
    """Get webhook and rule with the corresponding number.

    For example:
        WEBHOOK_URL1 goes with RULE1.
        WEBHOOK_URL5 goes with RULE5.
    """
    # sourcery skip: extract-method
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
                logger.error("I couldn't figure out what {} was when parsing {}.", get_digit, rule_name)
            else:
                # Remove " and ' from the start and end if they exist
                rules[get_digit] = rule_value.strip("'").strip('"')

                webhooks[get_digit] = os.getenv(f"WEBHOOK_URL{get_digit}", default="")

                if not webhooks[get_digit]:
                    sys.exit(f"Failed to get WEBHOOK_URL{get_digit}")

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
        logger.error("Failed to get WEBHOOK_URL, webhook is None.")
        sys.exit(1)

    # Remove " and ' from the start and end if they exist
    webhooks[0] = webhooks[0].strip("'").strip('"')

    # If we can't get the webhook, exit.
    if not webhooks[0]:
        logger.error("I failed to get WEBHOOK_URL when parsing RULE0.")
        sys.exit(1)

    logger.debug("Rule 0: {} will get sent to {}", rule_value, webhooks[0])


def get_setting_value(env_var: str, default_value: bool) -> bool:  # noqa: FBT001
    """Get the setting value from the environment.

    Convert different values that the user might use to a boolean.

    Args:
        env_var (str): The environment variable to get the value from.
        default_value (bool): The default value of the setting.

    Returns:
        str: The value of the setting.
    """
    value: str = os.getenv(env_var, default="")
    if value.lower() in {"n", "no", "false", "off", "0", "disable", "disabled"}:
        logger.debug("'{}' is set to '{}', disabling.", env_var, value)
        return False
    if value.lower() in {"y", "yes", "true", "on", "1", "enable", "enabled"}:
        logger.debug("'{}' is set to '{}', enabling.", env_var, value)
        return True
    if value != "":  # noqa: PLC1901
        logger.warning(
            "'{}' is set to '{}', which is not a valid value. Defaulting to {}.",
            env_var,
            value,
            default_value,
        )

    return default_value


def exit_if_too_long(setting_value: str, env_var: str, max_length: int) -> None:
    """Exit if the setting value is too long.

    Args:
        setting_value: The value of the setting.
        env_var: The environment variable that the setting value came from.
        max_length: The maximum length of the setting value.
    """
    if len(setting_value) > max_length:
        msg: str = f"{env_var} is {len(setting_value)} characters long, but the max length is {max_length}."
        logger.error(msg)
        sys.exit(1)


def get_bearer_token() -> str:
    # This was the example bearer token in the .env.example file before it got change to YOUR_BEARER_TOKEN.
    example_bearer_token = "AAAAAAAAAAAAAAAAAAAAAAMGcQEAAAAA2Xh6%2Bjxw4NM7xetr2C9trBdsNUo%3DIyQF6ddixAnAtuAUq7NRKUVcGJsJ8IlriICvVWqCWFK2SfhRY"  # noqa: S105, E501
    bearer_token: str = os.getenv("BEARER_TOKEN", default="")

    if not bearer_token or bearer_token == example_bearer_token:
        msg = "You need to set BEARER_TOKEN to a valid bearer token."
        logger.error(msg)
        sys.exit(1)

    return bearer_token


def get_log_level() -> str:
    """Get the log level from the environment.

    Returns:
        str: The log level. Defaults to "INFO".
    """
    # We have to use print here because the logger is not set up yet.
    log_levels: list[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    log_level = os.getenv("LOG_LEVEL", default="INFO")
    if log_level not in log_levels:
        print(f"LOG_LEVEL is set to '{log_level}', which is not a valid value. Defaulting to INFO.")  # noqa: T201
        log_level = "INFO"

    return log_level


def warn_if_not_https(url: str, hook_name: str) -> None:
    """Warn if the url is not https.

    Args:
        url: The url to check.
        hook_name: The environment variable name.
    """
    if not url:
        return
    if urlparse(url).scheme != "https":
        logger.warning("{} should probably be a https url do to security reasons.", hook_name)


def check_webhook(webhook: str) -> None:
    """Check if the webhook is valid.

    If the webhook is not valid, exit the program with an error message.

    Args:
        webhook: The webhook to check.
    """
    # Connect to the webhook to check if it is a valid webhook
    response: requests.Response = requests.get(webhook, timeout=5)

    # If we can't connect to the webhook, warn the user.
    if not response.ok:
        err_msg: str = ""

        # Discord returns a json with a message if the webhook is invalid
        if message := response.json().get("message", ""):
            err_msg += f"{message}\n"
        elif message := response.json().get("webhook_id", ""):
            for _value in message:
                err_msg += f"{_value}\n"

        # Get message from the response if it exists
        err_msg += (
            f"{response.status_code} {response.reason} - I can't connect to {webhook}, please check if it is a valid"
            " webhook."
        )
        logger.error(err_msg)
        sys.exit(1)

    # Check if the webhook has a name in the response to check if it is a valid webhook
    try:
        if response.json().get("name"):
            logger.debug("Webhook {} is a valid webhook", webhook)
    except json.decoder.JSONDecodeError:
        logger.exception(
            "Tried to connect to {}, but it is not a valid webhook. Got response: {}",
            webhook,
            response.text,
        )
        sys.exit(1)


def get_error_webhook() -> str:
    """Get the error webhook from the environment.

    The webhook to send errors to.

    Returns:
        str: The error webhook. Defaults to "".
    """
    # Get the error webhook from the environment.
    value: str = os.getenv("ERROR_WEBHOOK", default="")

    # If error webhook is not set, return an empty string immediately.
    if not value:
        return value

    # Remove " and ' from the start and end if they exist
    value = value.strip("'").strip('"')

    warn_if_not_https(value, "ERROR_WEBHOOK")

    return value


def get_embed_author_name() -> str:
    """Customize the embed author name.

    Author name can be up to 256 characters.

    Returns:
        str: The webhook author name. Defaults to "".
    """
    author_name: str = ""

    # Setting was renamed from WEBHOOK_AUTHOR_NAME to EMBED_AUTHOR_NAME
    new: str = os.getenv("EMBED_AUTHOR_NAME", default="")
    old: str = os.getenv("WEBHOOK_AUTHOR_NAME", default="")

    # If both are set, use the old one.
    if new and old:
        log_msg = "Both EMBED_AUTHOR_NAME and WEBHOOK_AUTHOR_NAME are set. WEBHOOK_AUTHOR_NAME will be used."
        logger.warning(log_msg)
        author_name = old
    elif old:
        exit_if_too_long(old, "WEBHOOK_AUTHOR_NAME", 256)
        author_name = old
    elif new:
        exit_if_too_long(new, "EMBED_AUTHOR_NAME", 256)
        author_name = new

    return author_name


def get_embed_author_url() -> str:
    """Customize the embed author url.

    Returns:
        str: The webhook author url. Defaults to "".
    """
    author_url: str = ""

    # Setting was renamed from WEBHOOK_AUTHOR_URL to EMBED_AUTHOR_URL
    old: str = os.getenv("WEBHOOK_AUTHOR_URL", default="")
    new: str = os.getenv("EMBED_AUTHOR_URL", default="")

    # If both are set, use the old one.
    if old and new:
        log_msg = "Both WEBHOOK_AUTHOR_URL and EMBED_AUTHOR_URL are set. WEBHOOK_AUTHOR_URL will be used."
        logger.warning(log_msg)
        author_url = old
    elif old:
        warn_if_not_https(author_url, "WEBHOOK_AUTHOR_URL")
        author_url = old
    elif new:
        warn_if_not_https(author_url, "EMBED_AUTHOR_URL")
        author_url = new

    return author_url


def get_embed_author_icon() -> str:
    """Customize the embed author icon.

    Returns:
        str: The webhook author icon. Defaults to "".
    """
    author_icon: str = ""

    # Setting was renamed from WEBHOOK_AUTHOR_ICON to EMBED_AUTHOR_ICON
    old: str = os.getenv("WEBHOOK_AUTHOR_ICON", default="")
    new: str = os.getenv("EMBED_AUTHOR_ICON", default="")

    # If both are set, use the old one.
    if old and new:
        log_msg = "Both WEBHOOK_AUTHOR_ICON and EMBED_AUTHOR_ICON are set. WEBHOOK_AUTHOR_ICON will be used."
        logger.warning(log_msg)
        author_icon = old
    elif old:
        warn_if_not_https(author_icon, "WEBHOOK_AUTHOR_ICON")
        author_icon = old
    elif new:
        warn_if_not_https(author_icon, "EMBED_AUTHOR_ICON")
        author_icon = new

    return author_icon


def get_embed_image() -> str:
    """Customize the embed image.

    Returns:
        str: The webhook image. Defaults to "".
    """
    embed_image: str = ""

    # Setting was renamed from WEBHOOK_IMAGE to EMBED_IMAGE
    old: str = os.getenv("WEBHOOK_IMAGE", default="")
    new: str = os.getenv("EMBED_IMAGE", default="")

    # If both are set, use the old one.
    if old and new:
        log_msg = "Both WEBHOOK_IMAGE and EMBED_IMAGE are set. WEBHOOK_IMAGE will be used."
        logger.warning(log_msg)
        embed_image = old
    elif old:
        warn_if_not_https(embed_image, "WEBHOOK_IMAGE")
        embed_image = old
    elif new:
        warn_if_not_https(embed_image, "EMBED_IMAGE")
        embed_image = new

    return embed_image


def get_embed_thumbnail() -> str:
    """Customize the embed thumbnail.

    Returns:
        str: The webhook thumbnail. Defaults to "".
    """
    embed_thumbnail: str = ""

    # Setting was renamed from WEBHOOK_IMAGE to EMBED_IMAGE
    old: str = os.getenv("WEBHOOK_THUMBNAIL", default="")
    new: str = os.getenv("EMBED_THUMBNAIL", default="")

    # If both are set, use the old one.
    if old and new:
        log_msg = "Both WEBHOOK_THUMBNAIL and EMBED_THUMBNAIL are set. WEBHOOK_THUMBNAIL will be used."
        logger.warning(log_msg)
        embed_thumbnail = old
    elif old:
        warn_if_not_https(embed_thumbnail, "WEBHOOK_THUMBNAIL")
        embed_thumbnail = old
    elif new:
        warn_if_not_https(embed_thumbnail, "EMBED_THUMBNAIL")
        embed_thumbnail = new

    return embed_thumbnail


def get_embed_footer_text() -> str:
    """Customize the embed footer text.

    Returns:
        str: The webhook footer text. Defaults to "".
    """
    footer_text: str = ""

    # Setting was renamed from WEBHOOK_IMAGE to EMBED_IMAGE
    old: str = os.getenv("WEBHOOK_FOOTER_TEXT", default="")
    new: str = os.getenv("EMBED_FOOTER_TEXT", default="Twitter")

    if old:
        warn_if_not_https(footer_text, "WEBHOOK_FOOTER_TEXT")
        exit_if_too_long(old, "WEBHOOK_FOOTER_TEXT", 2000)
        footer_text = old
    elif new:
        warn_if_not_https(footer_text, "EMBED_FOOTER_TEXT")
        exit_if_too_long(new, "EMBED_FOOTER_TEXT", 2000)
        footer_text = new

    return footer_text


def get_embed_footer_icon() -> str:
    """Customize the footer icon of the webhook.

    Returns:
        str: The webhook footer icon. Defaults to "". If WEBHOOK_FOOTER_TEXT is not set, this will also return "".
    """
    # TODO: Warn if WEBHOOK_FOOTER_TEXT is not set. Return "" if it is not set.
    footer_icon: str = ""

    # Default to the Twitter icon
    img: str = "https://abs.twimg.com/icons/apple-touch-icon-192x192.png"

    old: str = os.getenv("WEBHOOK_FOOTER_ICON", default="")
    new: str = os.getenv("EMBED_FOOTER_ICON", default=img)

    if old:
        warn_if_not_https(footer_icon, "WEBHOOK_FOOTER_ICON")
        footer_icon = old
    elif new:
        warn_if_not_https(footer_icon, "EMBED_FOOTER_ICON")
        footer_icon = new

    return footer_icon


def should_make_text_link() -> bool:
    """If we should make the tweet text a link to the tweet.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    value: bool = get_setting_value(env_var="MAKE_TEXT_LINK", default_value=False)
    if value:
        get_setting_value(env_var="NO_EMBED", default_value=False)

    return value


def get_make_text_link_preview() -> bool:
    """If we should make the tweet text a link to the tweet.

    Returns:
        bool: The value of the setting. Defaults to False.
    """
    old: bool = get_setting_value(env_var="MAKE_TEXT_LINK_TWITTER_EMBED", default_value=False)
    new: bool = get_setting_value(env_var="MAKE_TEXT_LINK_PREVIEW", default_value=False)
    return False if old else new


def get_make_text_link_url() -> str:
    """The URL to use for the tweet text link. It defaults to the tweet URL if not set.

    Returns:
        str: The value of the setting. If it is "" it will default to "https://twitter.com/{username}/web/status/{tweet_id}".
    """  # noqa: E501
    value: str = os.getenv("MAKE_TEXT_LINK_URL", default="")
    if value:
        if not should_make_text_link():
            logger.warning(
                "You need to set MAKE_TEXT_LINK to True to use MAKE_TEXT_LINK_URL. Defaulting to tweet URL.",
            )
            return ""
        if not get_setting_value(env_var="NO_EMBED", default_value=False):
            logger.warning(
                "You need to set NO_EMBED to True to use MAKE_TEXT_LINK.",
            )
            return ""
        logger.info("MAKE_TEXT_LINK_URL is set to %s.", value)
    return value


def get_remove_copyright_symbols() -> bool:
    """If we should remove the copyright symbols from the tweet text.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="DISABLE_REMOVE_COPYRIGHT_SYMBOLS", default_value=False)
    new: bool = get_setting_value(env_var="REMOVE_COPYRIGHT_SYMBOLS", default_value=True)
    return False if old else new


def get_remove_utm_parameters() -> bool:
    """If we should remove the copyright symbols from the tweet text.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="DISABLE_REMOVE_UTM", default_value=False)
    new: bool = get_setting_value(env_var="REMOVE_COPYRIGHT_SYMBOLS", default_value=True)
    return False if old else new


def get_replace_reddit_username() -> bool:
    """If we should remove the copyright symbols from the tweet text.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="DISABLE_REPLACE_REDDIT_USERNAME", default_value=False)
    new: bool = get_setting_value(env_var="REDDIT_USERNAME_LINK", default_value=True)
    return False if old else new


def get_replace_subreddit() -> bool:
    """If we should remove the copyright symbols from the tweet text.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="DISABLE_REPLACE_SUBREDDIT", default_value=False)
    new: bool = get_setting_value(env_var="SUBREDDIT_LINK", default_value=True)
    return False if old else new


def get_discord_link_previews() -> bool:
    old: bool = get_setting_value(env_var="DISABLE_REMOVE_DISCORD_LINK_PREVIEWS", default_value=False)
    new: bool = get_setting_value(env_var="DISCORD_LINK_PREVIEWS", default_value=True)
    return False if old else new


def get_replace_hashtags() -> bool:
    """If we should replace hashtags with links to the hashtag.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="DISABLE_REPLACE_HASHTAG", default_value=False)
    new: bool = get_setting_value(env_var="HASHTAG_LINK", default_value=True)
    return False if old else new


def get_replace_username() -> bool:
    """If we should replace usernames with links to the user.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="DISABLE_REPLACE_USERNAME", default_value=False)
    new: bool = get_setting_value(env_var="USERNAME_LINK", default_value=True)
    return False if old else new


def get_unescape_text() -> bool:
    """If we should unescape HTML entities in the tweet text.

    For example, "&amp;" becomes "&".

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="DISABLE_UNESCAPE_TEXT", default_value=False)
    new: bool = get_setting_value(env_var="UNESCAPE_TEXT", default_value=True)
    return False if old else new


def get_convert_tco_links() -> bool:
    """If we should convert t.co links to their original links.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="DISABLE_REMOVE_TCO_LINKS", default_value=False)
    new: bool = get_setting_value(env_var="CONVERT_TCO_LINKS", default_value=True)
    return False if old else new


def get_show_title() -> bool:
    """If we should show the title of the tweet.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="USE_TITLE", default_value=False)
    new: bool = get_setting_value(env_var="SHOW_TITLE", default_value=False)
    return True if old else new


def get_show_author() -> bool:
    """If we should show the author of the tweet.

    Returns:
        bool: The value of the setting. Defaults to True.
    """
    old: bool = get_setting_value(env_var="USE_AUTHOR", default_value=True)
    new: bool = get_setting_value(env_var="SHOW_AUTHOR", default_value=True)
    return True if old else new


def get_embed_color() -> str:
    default_color: str = "#1DA1F2"  # Twitter blue
    old: str = os.getenv("WEBHOOK_EMBED_COLOR", default=default_color)
    new: str = os.getenv("EMBED_COLOR", default=default_color)

    random_color: bool = get_setting_value(env_var="RANDOMIZE_EMBED_COLOR", default_value=False)
    if random_color:
        logger.info("Embed color is set to random.")
        return "random"

    if old != default_color:
        logger.warning("WEBHOOK_EMBED_COLOR is deprecated. Use EMBED_COLOR instead.")
        logger.info("WEBHOOK_EMBED_COLOR is set to %s.", old)
        return old
    if new != default_color:
        logger.info("EMBED_COLOR is set to %s.", new)
        return new

    if old.lower() == "random" or new.lower() == "random":
        logger.info("Embed color is set to random.")

    return default_color


def get_no_embed() -> bool:
    old: bool = get_setting_value(env_var="NO_EMBED", default_value=False)
    new: bool = get_setting_value(env_var="SEND_TEXT", default_value=False)
    return True if old else new


def get_embed_timestamp() -> bool:
    old: bool = get_setting_value(env_var="SHOW_TIMESTAMP", default_value=True)
    new: bool = get_setting_value(env_var="EMBED_TIMESTAMP", default_value=True)
    return True if old else new
