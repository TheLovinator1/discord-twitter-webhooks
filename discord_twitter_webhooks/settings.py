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
webhooks = {}
hook_num = 0
for hook in os.environ:
    if hook.startswith("WEBHOOK_URL"):
        print(f"{hook_num}: {hook}={os.environ[hook]}")
        webhooks[hook_num] = {os.environ[hook]}

        hook_num += 1
print(f"webhooks={webhooks}")

# Log severity. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG.
log_level: str = os.getenv("LOG_LEVEL", default="INFO")

# Where https://github.com/TheLovinator1/twitter-image-collage-maker is running.
# You can run your own version or use the default https://twitter.lovinator.space/
collage_maker_url: str = os.getenv("TWITTER_IMAGE_COLLAGE_API", default="https://twitter.lovinator.space/add")

# https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
rules = {}
rule_num = 0
for rule in os.environ:
    if rule.startswith("RULE"):
        print(f"{rule_num}: {rule}={os.environ[rule]}")
        rules[rule_num] = os.environ[rule]

        rule_num += 1
print(f"rules={rules}")

if len(rules) == 0:
    print("No rules found")
    sys.exit(1)

# Tell the user he needs Elevated Twitter API access if he has more than 5 webhooks.
if len(rules) > 26:
    print("You have more than 26 rules. If this doesn't work, you need Academic Research API access.")
elif len(rules) > 5:
    print("You have more than 5 rules. If this doesn't work, you need Elevated Twitter API access.")

if len(webhooks) != len(rules):
    print(f"Note: You have {len(webhooks)} webhooks but only {len(rules)} rules.")

# If we should send errors to Discord. Can be True or False.
send_errors: str = os.getenv("SEND_ERRORS", default="False")
error_webhook: str = os.getenv("ERROR_WEBHOOK", default="")

if not bearer_token:
    sys.exit("No bearer token found, exiting")

# TODO: Add logging config file so you can customize the logging
logger = logging
logger.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=log_level,
)
