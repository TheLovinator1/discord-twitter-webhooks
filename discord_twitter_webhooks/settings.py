import logging
import os

import sys
from dotenv import load_dotenv

# Parse the .env file and then load all the variables found as
# environment variables
load_dotenv()

# Environment variables
# https://developer.twitter.com/en/portal/projects-and-apps
bearer_token: str = os.getenv("BEARER_TOKEN", default="")

# https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
webhook_url: str = os.environ["WEBHOOK_URL"]

# Log severity. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG
log_level: str = os.getenv("LOG_LEVEL", default="INFO")

# Where https://github.com/TheLovinator1/twitter-image-collage-maker is
# running. You can run your own version or use the default
# https://twitter.lovinator.space/
collage_maker_url: str = os.getenv("TWITTER_IMAGE_COLLAGE_API", default="https://twitter.lovinator.space/add")

# https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
rule: str = os.getenv("RULE", default="")

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
