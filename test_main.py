from main import twitter_regex
import html
import os
from dhooks import Webhook

# TODO: Use real tweet instead of str
tweet_text = """Hello.
#IAmHashtag
@TheLovinator1

/r/ThisIsSubreddit
/u/ThisIsUser
&amp;"""


def test_regex_substitutor():
    correct_text = "Hello.\n[#IAmHashtag](<https://twitter.com/hashtag/IAmHashtag>)\n[@TheLovinator1](<https://twitter.com/TheLovinator1>)\n\n[/r/ThisIsSubreddit](https://reddit.com/r/ThisIsSubreddit)\n[/u/ThisIsUser](https://reddit.com/u/ThisIsUser)\n&amp;"
    text = twitter_regex(text=tweet_text)
    assert correct_text == text


def test_convert_safe_html():
    correct_text = (
        "Hello.\n#IAmHashtag\n@TheLovinator1\n\n/r/ThisIsSubreddit\n/u/ThisIsUser\n&"
    )
    text = html.unescape(tweet_text)
    assert correct_text == text


# def test_send_error_webhook():
#    webhook_url_error = os.environ["WEBHOOK_URL"]
#    hook = Webhook(webhook_url_error)
#    assert hook.send("This is a test") is None  # TODO: Do this better
