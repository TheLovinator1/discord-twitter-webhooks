import sys
from configparser import ConfigParser
import os

config = ConfigParser()

config["discord"] = {
    "webhook_url": "webhook_url",
    "webhook_error_url": "webhook_error_url",
}

config["twitter"] = {
    "consumer_key": "consumer_key",
    "consumer_secret": "consumer_secret",
    "access_token": "access_token",
    "access_token_secret": "access_token_secret",
    "users_to_follow": "user1, user2, user3",
}

config["logging"] = {
    "log_level": "INFO",
    "log_to_file": False,
    "log_level_file": "INFO",
    "log_name": "log.txt",
}

# Check if config file exists before creating one
if not os.path.isfile("config.ini"):
    with open("config.ini", "w") as f:
        config.write(f)

parser = ConfigParser()
parser.read("config.ini")

# TODO: Check if the url is correct and not if it is "webhook_url"
if parser.get("discord", "webhook_url") == "webhook_url":
    print("Please fill out the config file!")
    sys.exit(0)

webhook_url = parser.get("discord", "webhook_url")
webhook_error_url = parser.get("discord", "webhook_error_url")

consumer_key = parser.get("twitter", "consumer_key")
consumer_secret = parser.get("twitter", "consumer_secret")
access_token = parser.get("twitter", "access_token")
access_token_secret = parser.get("twitter", "access_token_secret")

users_to_follow = parser.get("twitter", "users_to_follow")
user_list = [x.strip() for x in users_to_follow.split(",")]

log_level_file = parser.get("logging", "log_level_file")
log_level = parser.get("logging", "log_level")
log_name = parser.get("logging", "log_name")
