import os


def check_if_we_used_v1():
    """Check if we have USERS_TO_FOLLOW in our environment, this means
    we have used the bot before v2.0.0. If we have, send a message to
    the Discord channel that we have been updated. After that we sleep for 4 hours,
    so we don't spam the channel.
    """
    if "USERS_TO_FOLLOW" in os.environ:
        # Send a message to the channel to let the user know that the
        # configuration file has been updated.
        print(MESSAGE)
        return True


MESSAGE = """Hello!

[discord-twitter-webhooks](https://github.com/TheLovinator1/discord-twitter-webhooks) has been updated to version 2.0.0.
There have been a few breaking changes, and it looks like you were using
the old version.

You will need to update your environment/configuration file to get
discord-twitter-webhooks working again.

The bot is now using the V2 version of the Twitter API, which means that you
will need to update your configuration file to use a bearer token
instead of API keys.

Rules are also used instead of user ids. It's now possible to
have more granular control over what tweets get sent to Discord.
You can now filter specific words, only get tweets with images, and much more instead
of getting all the tweets from a specific user.

You can find more information in the [README.md](https://github.com/TheLovinator1/discord-twitter-webhooks).


The bot will now sleep for 4 hours before restarting to avoid spamming
this channel due to Docker/Systemd restarting the bot every time it
shuts down. You will have to remove USERS_TO_FOLLOW from your
environment/configuration file to stop this message from appearing.


Feel free to contact me on Discord, make an [issue](https://github.com/TheLovinator1/discord-twitter-webhooks),
or email me at tlovinator@gmail.com if you have any questions.

Thanks,
TheLovinator#9276"""
