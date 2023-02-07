"""Loading and parsing settings from .env file or environment variables.

If we have both a .env file and environment variables, we will use the environment variables."""
import logging
import os
import re
import sys
from typing import Dict

from dotenv import load_dotenv

# Parse the .env file and then load all the variables found as environment variables.
load_dotenv(verbose=True)

# Log severity. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG.
log_level: str = os.getenv("LOG_LEVEL", default="INFO")

# TODO: Add logging config file so you can customize the logging
logger = logging
logger.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S", level=log_level)

# https://developer.twitter.com/en/portal/projects-and-apps
bearer_token: str = os.getenv("BEARER_TOKEN", default="")

webhooks: Dict[int, str] = {}
rules: Dict[int, str] = {}


def get_hook_and_rule() -> None:
    """
    Get webhook and rule with the corresponding number.

    For example:
        WEBHOOK_URL1 goes with RULE1.
        WEBHOOK_URL5 goes with RULE5.
    """
    for rule_name, rule_value in os.environ.items():
        # Check for single rule
        if rule_name == "RULE":
            rules[0] = rule_value
            webhooks[0] = os.getenv("WEBHOOK_URL", default="")

            # If we can't get the webhook, exit.
            if webhooks[0] == "":
                sys.exit("I failed to get WEBHOOK_URL")
            logger.info(f"Rule 0: {rule_name}={rule_value} will get send to {webhooks[0]!r}")

        # Check for multiple rules
        elif rule_name.startswith("RULE"):
            # Get digits at the end of the string
            match: re.Match[str] | None = re.search(r"\d+$", rule_name)
            get_digit: int | None = int(match.group()) if match else None

            # If we can't get the digit, log an error and continue.
            if get_digit is None:
                logger.error(f"I couldn't figure out what {get_digit!r} was when parsing {rule_name}={rule_value}.")
            else:
                rules[get_digit] = rule_value
                webhooks[get_digit] = os.getenv(f"WEBHOOK_URL{get_digit}")  # type: ignore

                logger.info(f"Rule {get_digit}: {rule_value!r} will get sent to {webhooks[get_digit]!r}")


# Get webhook and rule from the environment.
get_hook_and_rule()

# Where https://github.com/TheLovinator1/twitter-image-collage-maker is running.
# You can run your own version or use the default https://twitter.lovinator.space/
collage_maker_url: str = os.getenv("TWITTER_IMAGE_COLLAGE_API", default="https://twitter.lovinator.space/add")

if len(rules) == 0:
    sys.exit("No rules found, you should edit the .env or environment variables to add rules.")

# Tell the user he needs Elevated Twitter API access if he has more than 5 webhooks.
if len(rules) > 26:
    logger.warning("You have more than 26 rules. If this doesn't work, you need Academic Research API access.")
elif len(rules) > 5:
    logger.warning("You have more than 5 rules. If this doesn't work, you need Elevated Twitter API access.")

# If we should send errors to Discord. Can be True or False.
send_errors: str = os.getenv("SEND_ERRORS", default="False")
error_webhook: str = os.getenv("ERROR_WEBHOOK", default="")

if not bearer_token:
    sys.exit("No bearer token found in .env file or environment variables.")

webhook_author_name: str = os.getenv("WEBHOOK_AUTHOR_NAME", default="")
webhook_author_url: str = os.getenv("WEBHOOK_AUTHOR_URL", default="")
webhook_author_icon: str = os.getenv("WEBHOOK_AUTHOR_ICON", default="")
webhook_image: str = os.getenv("WEBHOOK_IMAGE", default="")
webhook_thumbnail: str = os.getenv("WEBHOOK_THUMBNAIL", default="")
webhook_footer_text: str = os.getenv("WEBHOOK_FOOTER_TEXT", default="")
webhook_footer_icon: str = os.getenv("WEBHOOK_FOOTER_ICON", default="")

# Only send the text
no_embed: str = os.getenv("NO_EMBED", default="")

# Disable features
disable_remove_tco_links: str = os.getenv("DISABLE_REMOVE_TCO_LINKS", default="")
disable_unescape_text: str = os.getenv("DISABLE_UNESCAPE_TEXT", default="")
disable_replace_username: str = os.getenv("DISABLE_REPLACE_USERNAME", default="")
disable_replace_hashtag: str = os.getenv("DISABLE_REPLACE_HASHTAG", default="")
disable_remove_discord_link_previews: str = os.getenv("DISABLE_REMOVE_DISCORD_LINK_PREVIEWS", default="")
disable_replace_subreddit: str = os.getenv("DISABLE_REPLACE_SUBREDDIT", default="")
disable_replace_reddit_username: str = os.getenv("DISABLE_REPLACE_REDDIT_USERNAME", default="")
disable_remove_utm_parameters: str = os.getenv("DISABLE_REMOVE_UTM", default="")
disable_remove_trailing_whitespace: str = os.getenv("DISABLE_REMOVE_TRAILING_WHITESPACE", default="")
disable_remove_copyright_symbols: str = os.getenv("DISABLE_REMOVE_COPYRIGHT_SYMBOLS", default="")

if webhook_author_name:
    logger.info(f"Note that you have customized webhook_author_name to '{webhook_author_name}'.")
if webhook_author_url:
    logger.info(f"Note that you have customized webhook_author_url to '{webhook_author_url}'.")
if webhook_author_icon:
    logger.info(f"Note that you have customized webhook_author_icon to '{webhook_author_icon}'.")
if webhook_image:
    logger.info(f"Note that you have customized webhook_image to '{webhook_image}'.")
if webhook_thumbnail:
    logger.info(f"Note that you have customized webhook_thumbnail to '{webhook_thumbnail}'.")
if webhook_footer_text:
    logger.info(f"Note that you have customized webhook_footer_text to '{webhook_footer_text}'.")
if webhook_footer_icon:
    logger.info(f"Note that you have customized webhook_footer_icon to '{webhook_footer_icon}'.")


def str_to_bool(val: str, setting_name: str) -> bool:
    """Convert a string to a boolean.

    Args:
        val: The string to convert.
        setting_name: The name of the setting. Used for logging.

    Raises:
        ValueError: If the string is not a boolean.

    Returns:
        The boolean value.
    """
    if val.lower() in {"y", "yes", "true", "on", "1", "enable", "enabled"}:
        logger.info(f"{setting_name} is enabled.")
        return True
    elif val.lower() in {"n", "no", "false", "off", "0", "disable", "disabled"}:
        logger.debug(f"{setting_name} is not enabled.")
        return False
    else:
        logger.warning(f"{setting_name} is not a boolean. Got '{val}'. Defaulting to False.")
        return False


show_timestamp_value: str = os.getenv("SHOW_TIMESTAMP", default="False")
webhook_show_timestamp: bool = str_to_bool(show_timestamp_value, "SHOW_TIMESTAMP")
