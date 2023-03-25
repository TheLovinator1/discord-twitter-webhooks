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
            (
                "You have more than %s rules. If this doesn't work, you need Academic Research API access. You can read"
                " more about it here:"
                " https://developer.twitter.com/en/products/twitter-api/academic-research/application-info"
            ),
            max_rules_elevated,
        )
    elif len(rules) > max_rules_pleb:
        logger.warning(
            (
                "You have more than %s rules. If this doesn't work, you need Elevated Twitter API access. You need to"
                " apply for it on https://developer.twitter.com/en/portal/dashboard, under 'Projects and Apps'"
            ),
            max_rules_pleb,
        )


check_rules_valid()

# If we should send errors to Discord.
send_errors: bool = get_settings.get_setting_value(env_var="SEND_ERRORS", default_value=False)
error_webhook: str = get_settings.get_error_webhook()

# If we should use a custom display name. This is the name that shows up on the left side of the username.
webhook_author_name: str = get_settings.get_webhook_author_name()

# If we should use a custom author url. This is the url that the display name and username links to.
webhook_author_url: str = get_settings.get_webhook_author_url()

# If we should use a custom author icon. This is the image on the left side of the display name and username.
webhook_author_icon: str = get_settings.get_webhook_author_icon()

# If we should use a custom image. This will the image in the embed.
webhook_image: str = get_settings.get_webhook_image()

# If we should use a custom thumbnail. This is the image on the right side of the embed.
webhook_thumbnail: str = get_settings.get_webhook_thumbnail()

# If we should use a custom footer text.
webhook_footer_text: str = get_settings.get_webhook_footer_text()

# If we should use a custom footer icon.
webhook_footer_icon: str = get_settings.get_webhook_footer_icon()

# Show a timestamp on the bottom of the embed. This will show when the tweet was sent/created.
webhook_show_timestamp: bool = get_settings.get_setting_value(env_var="SHOW_TIMESTAMP", default_value=True)

# If we should randomize the embed color. This will make the embed color a random color each time a tweet is sent.
webhook_randomize_embed_color: bool = get_settings.get_setting_value(
    env_var="RANDOMIZE_EMBED_COLOR",
    default_value=False,
)

# If we should use a custom embed color. This will override the randomize embed color setting.
webhook_embed_color: str = os.getenv("WEBHOOK_EMBED_COLOR", default="")

# If we should show a webhook title. This shows the tweet authors display name and username.
use_title: bool = get_settings.get_setting_value(env_var="USE_TITLE", default_value=False)

# If we should show a webhook author. This shows the tweet authors display name, username and profile picture.
use_author: bool = get_settings.get_setting_value(env_var="USE_AUTHOR", default_value=True)

# If the tweet should be sent as a text instead of an embed.
no_embed: bool = get_settings.get_setting_value(env_var="NO_EMBED", default_value=False)

# Add [text](tweet_url) to the tweet text. This will make the text a link.
make_text_link: bool = get_settings.get_make_text_link()

# If we should disable the link preview by adding < > around the link.
make_text_link_twitter_embed: bool = get_settings.get_make_text_link_twitter_embed()

# If we should use a custom URL for the link instead of the tweet URL.
make_text_link_url: str = get_settings.get_make_text_link_url()

# If we should only send the link to the tweet.
only_link: bool = get_settings.get_setting_value(env_var="ONLY_LINK", default_value=False)

# If we should disable the link preview by adding < > around the link.
only_link_preview: bool = get_settings.get_setting_value(env_var="ONLY_LINK_PREVIEW", default_value=True)

# Append link to the end of the tweet text.
append_image_links: bool = get_settings.get_append_image_links()

# Don't convert t.co links to their original links
disable_remove_tco_links: bool = get_settings.get_setting_value(
    env_var="DISABLE_REMOVE_TCO_LINKS",
    default_value=False,
)

# Don't unescape text like &amp; to &
disable_unescape_text: bool = get_settings.get_setting_value(env_var="DISABLE_UNESCAPE_TEXT", default_value=False)

# Don't replace usernames with @username
disable_replace_username: bool = get_settings.get_setting_value(
    env_var="DISABLE_REPLACE_USERNAME",
    default_value=False,
)

# Don't replace hashtags with #hashtag
disable_replace_hashtag: bool = get_settings.get_setting_value(
    env_var="DISABLE_REPLACE_HASHTAG",
    default_value=False,
)

# Don't remove discord link previews
disable_remove_discord_link_previews: bool = get_settings.get_setting_value(
    env_var="DISABLE_REMOVE_DISCORD_LINK_PREVIEWS",
    default_value=False,
)

# Don't replace subreddits with /r/subreddit
disable_replace_subreddit: bool = get_settings.get_setting_value(
    env_var="DISABLE_REPLACE_SUBREDDIT",
    default_value=False,
)

# Don't replace reddit usernames with /u/username
disable_replace_reddit_username: bool = get_settings.get_setting_value(
    env_var="DISABLE_REPLACE_REDDIT_USERNAME",
    default_value=False,
)

# Don't remove UTM parameters from links (utm_source, utm_medium, utm_campaign, utm_term, utm_content)
disable_remove_utm_parameters: bool = get_settings.get_setting_value(
    env_var="DISABLE_REMOVE_UTM",
    default_value=False,
)

# Don't remove trailing whitespace
disable_remove_trailing_whitespace: bool = get_settings.get_setting_value(
    env_var="DISABLE_REMOVE_TRAILING_WHITESPACE",
    default_value=False,
)

# Don't remove copyright symbols (®, ™ and ©)
disable_remove_copyright_symbols: bool = get_settings.get_setting_value(
    env_var="DISABLE_REMOVE_COPYRIGHT_SYMBOLS",
    default_value=False,
)
