"""Loading and parsing settings from .env file or environment variables.

If we have both a .env file and environment variables, we will use the environment variables."""
import logging
import os
import sys

from dotenv import load_dotenv

# Parse the .env file and then load all the variables found as environment variables.
load_dotenv(verbose=True)

# https://developer.twitter.com/en/portal/projects-and-apps
bearer_token: str = os.getenv("BEARER_TOKEN", default="")

# https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
webhook_url: str = os.environ["WEBHOOK_URL"]
webhook_url2: str = os.getenv("WEBHOOK_URL2", default="")
webhook_url3: str = os.getenv("WEBHOOK_URL3", default="")
webhook_url4: str = os.getenv("WEBHOOK_URL4", default="")
webhook_url5: str = os.getenv("WEBHOOK_URL5", default="")

# Log severity. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG.
log_level: str = os.getenv("LOG_LEVEL", default="INFO")

# Where https://github.com/TheLovinator1/twitter-image-collage-maker is running.
# You can run your own version or use the default https://twitter.lovinator.space/
collage_maker_url: str = os.getenv("TWITTER_IMAGE_COLLAGE_API", default="https://twitter.lovinator.space/add")

# https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
rule: str = os.getenv("RULE", default="")
rule2: str = os.getenv("RULE2", default="")
rule3: str = os.getenv("RULE3", default="")
rule4: str = os.getenv("RULE4", default="")
rule5: str = os.getenv("RULE5", default="")

# If we should send errors to Discord. Can be True or False.
send_errors: str = os.getenv("SEND_ERRORS", default="False")
error_webhook: str = os.getenv("ERROR_WEBHOOK", default="")

if not bearer_token:
    sys.exit("No bearer token found, exiting")

if not rule:
    sys.exit("No rule found, exiting")

# TODO: Add logging config file so you can customize the logging
logger = logging
logger.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=log_level,
)
