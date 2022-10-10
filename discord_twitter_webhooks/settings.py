"""Loading and parsing settings from .env file or environment variables.

If we have both a .env file and environment variables, we will use the environment variables."""
import logging
import os
import re
import sys

from dotenv import load_dotenv

# Parse the .env file and then load all the variables found as environment variables.
load_dotenv(verbose=True)

# https://developer.twitter.com/en/portal/projects-and-apps
bearer_token: str = os.getenv("BEARER_TOKEN", default="")

webhooks = {}
rules = {}


def get_hook_and_rule():
    """
    Get webhook and rule with the corresponding number.

    For example:
        WEBHOOK_URL1 goes with RULE1.
        WEBHOOK_URL5 goes with RULE5.
    """
    for k, v in os.environ.items():
        if k == "RULE":
            rules[0] = v
            webhooks[0] = os.getenv("WEBHOOK_URL")
            if webhooks[0] is None:
                sys.exit("I failed to get WEBHOOK_URL")
            print(f"Rule 0: {k}={v} will get send to {webhooks[0]!r}")
        elif k.startswith("RULE"):
            m = re.search(r'\d+$', k)  # Get digits at the end of the string
            get_digit = int(m.group()) if m else None
            if get_digit is None:
                print(f"I couldn't figure out what {get_digit!r} was when parsing {k}={v}. Contact TheLovinator if "
                      f"this should work.")
            rules[get_digit] = v
            webhooks[get_digit] = os.getenv(f"WEBHOOK_URL{get_digit}")

            print(f"Rule {get_digit}: {v!r} will get send to {webhooks[get_digit]!r}")


# Get webhook and rule from the environment.
get_hook_and_rule()

# Log severity. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG.
log_level: str = os.getenv("LOG_LEVEL", default="INFO")

# Where https://github.com/TheLovinator1/twitter-image-collage-maker is running.
# You can run your own version or use the default https://twitter.lovinator.space/
collage_maker_url: str = os.getenv("TWITTER_IMAGE_COLLAGE_API", default="https://twitter.lovinator.space/add")

if len(rules) == 0:
    print("No rules found")
    sys.exit(1)

# Tell the user he needs Elevated Twitter API access if he has more than 5 webhooks.
if len(rules) > 26:
    print("You have more than 26 rules. If this doesn't work, you need Academic Research API access.")
elif len(rules) > 5:
    print("You have more than 5 rules. If this doesn't work, you need Elevated Twitter API access.")

# If we should send errors to Discord. Can be True or False.
send_errors: str = os.getenv("SEND_ERRORS", default="False")
error_webhook: str = os.getenv("ERROR_WEBHOOK", default="")

if not bearer_token:
    sys.exit("No bearer token found, exiting")

webhook_author_name: str = os.getenv("WEBHOOK_AUTHOR_NAME", default="")
webhook_author_url: str = os.getenv("WEBHOOK_AUTHOR_URL", default="")
webhook_author_icon: str = os.getenv("WEBHOOK_AUTHOR_ICON", default="")
webhook_image: str = os.getenv("WEBHOOK_IMAGE", default="")
webhook_thumbnail: str = os.getenv("WEBHOOK_THUMBNAIL", default="")
webhook_footer_text: str = os.getenv("WEBHOOK_FOOTER_TEXT", default="")
webhook_footer_icon: str = os.getenv("WEBHOOK_FOOTER_ICON", default="")

if webhook_author_name:
    print(f"Note that you have customized webhook_author_name to '{webhook_author_name}'.")
if webhook_author_url:
    print(f"Note that you have customized webhook_author_url to '{webhook_author_url}'.")
if webhook_author_icon:
    print(f"Note that you have customized webhook_author_icon to '{webhook_author_icon}'.")
if webhook_image:
    print(f"Note that you have customized webhook_image to '{webhook_image}'.")
if webhook_thumbnail:
    print(f"Note that you have customized webhook_thumbnail to '{webhook_thumbnail}'.")
if webhook_footer_text:
    print(f"Note that you have customized webhook_footer_text to '{webhook_footer_text}'.")
if webhook_footer_icon:
    print(f"Note that you have customized webhook_footer_icon to '{webhook_footer_icon}'.")

# TODO: Add logging config file so you can customize the logging
logger = logging
logger.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=log_level,
)
