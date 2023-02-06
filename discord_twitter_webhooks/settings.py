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
        if rule_name == "RULE":
            rules[0] = rule_value
            webhooks[0] = os.getenv("WEBHOOK_URL", default="")
            if webhooks[0] == "":
                sys.exit("I failed to get WEBHOOK_URL")
            logger.info(f"Rule 0: {rule_name}={rule_value} will get send to {webhooks[0]!r}")
        elif rule_name.startswith("RULE"):
            m: re.Match[str] | None = re.search(r"\d+$", rule_name)  # Get digits at the end of the string
            get_digit: int | None = int(m.group()) if m else None
            if get_digit is None:
                logger.error(
                    f"I couldn't figure out what {get_digit!r} was when parsing {rule_name}={rule_value}. Contact TheLovinator if this should work."  # noqa: E501
                )
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
