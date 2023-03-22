import os
import sys

from dotenv import load_dotenv
from loguru import logger

from discord_twitter_webhooks import get_settings
from discord_twitter_webhooks.logger import setup_logger

# Setup the logger
setup_logger()

# Parse the .env file and then load all the variables found as environment variables.
# TODO: Split .env into multiple files?
load_dotenv(verbose=True)

# https://developer.twitter.com/en/portal/projects-and-apps
bearer_token: str = get_settings.get_bearer_token()

# Get webhook and rule from the environment.
webhooks, rules = get_settings.get_hook_and_rule()

# Where https://github.com/TheLovinator1/twitter-image-collage-maker is running.
# You can run your own version or use the default https://twitter.lovinator.space/
collage_maker_url: str = os.getenv("TWITTER_IMAGE_COLLAGE_API", default="https://twitter.lovinator.space/add")


def check_rules_valid() -> None:
    """Check if the rules are valid.

    Academic Research API access is required for more than 25 rules.
    Elevated Twitter API access is required for more than 5 rules.

    If not, exit or warn the user.
    """
    # TODO: Tell how to get Academic Research API access or Elevated Twitter API access. Or tell them to run more bots?
    max_rules_elevated: int = 26
    max_rules_pleb: int = 5

    if len(rules) == 0:
        sys.exit("No rules found, you should edit the .env or environment variables to add rules.")

    if len(rules) > max_rules_elevated:
        logger.warning(
            "You have more than %s rules. If this doesn't work, you need Academic Research API access.",
            max_rules_elevated,
        )
    elif len(rules) > max_rules_pleb:
        logger.warning(
            "You have more than %s rules. If this doesn't work, you need Elevated Twitter API access.",
            max_rules_pleb,
        )


check_rules_valid()

# Important settings
send_errors: bool = get_settings.get_send_errors()
error_webhook: str = get_settings.get_error_webhook()

# Customization settings
webhook_author_name: str = get_settings.get_webhook_author_name()
webhook_author_url: str = get_settings.get_webhook_author_url()
webhook_author_icon: str = get_settings.get_webhook_author_icon()
webhook_image: str = get_settings.get_webhook_image()
webhook_thumbnail: str = get_settings.get_webhook_thumbnail()
webhook_footer_text: str = get_settings.get_webhook_footer_text()
webhook_footer_icon: str = get_settings.get_webhook_footer_icon()
webhook_show_timestamp: bool = get_settings.get_show_timestamp()
use_title: bool = get_settings.get_use_title()
use_author: bool = get_settings.get_use_author()

# Text instead of embed
no_embed: bool = get_settings.get_no_embed()
make_text_link: bool = get_settings.get_make_text_link()
make_text_link_twitter_embed: bool = get_settings.get_make_text_link_twitter_embed()
make_text_link_url: str = get_settings.get_make_text_link_url()

# If we should disable certain features.
disable_remove_tco_links: bool = get_settings.get_disable_remove_tco_links()
disable_unescape_text: bool = get_settings.get_disable_unescape_text()
disable_replace_username: bool = get_settings.get_disable_replace_username()
disable_replace_hashtag: bool = get_settings.get_disable_replace_hashtag()
disable_remove_discord_link_previews: bool = get_settings.get_disable_remove_discord_link_previews()
disable_replace_subreddit: bool = get_settings.get_disable_replace_subreddit()
disable_replace_reddit_username: bool = get_settings.get_disable_replace_reddit_username()
disable_remove_utm_parameters: bool = get_settings.get_disable_remove_utm_parameters()
disable_remove_trailing_whitespace: bool = get_settings.get_disable_remove_trailing_whitespace()
disable_remove_copyright_symbols: bool = get_settings.get_disable_remove_copyright_symbols()
