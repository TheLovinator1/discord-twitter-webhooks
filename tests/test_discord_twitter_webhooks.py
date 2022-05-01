"""Not enough tests here, but it's a good place to start."""
import os

import tweepy

from discord_twitter_webhooks import __version__
from discord_twitter_webhooks.get import (
    media_links_and_remove_url,
    meta_image,
    tweet_text,
)
from discord_twitter_webhooks.reddit import subreddit_to_link, username_to_link
from discord_twitter_webhooks.remove import (
    copyright_symbols,
    discord_link_previews,
    utm_source,
)
from discord_twitter_webhooks.replace import (
    hashtag_with_link,
    tco_url_link_with_real_link,
    username_with_link,
)
from discord_twitter_webhooks.send_embed_webhook import send_embed_webhook
from discord_twitter_webhooks.settings import auth


class TestTweets:
    """Test tweet stuff"""

    api = tweepy.API(auth)

    # https://twitter.com/Bot2Lovi/status/1416158460186611715
    short_tweet_only_text = api.get_status(1416158460186611715)

    # https://twitter.com/Bot2Lovi/status/1416162001076764675
    short_tweet_one_image = api.get_status(1416162001076764675)

    # https://twitter.com/Bot2Lovi/status/1416162224142487555
    short_tweet_two_images = api.get_status(1416162224142487555)

    # https://twitter.com/Bot2Lovi/status/1416162639269539847
    short_tweet_three_images = api.get_status(1416162639269539847)

    # https://twitter.com/Bot2Lovi/status/1416162799777157120
    short_tweet_four_image = api.get_status(1416162799777157120)

    # https://twitter.com/Bot2Lovi/status/1416165082304860160
    long_tweet_only_text = api.get_status(1416165082304860160)

    # https://twitter.com/Bot2Lovi/status/1416193952751947779
    long_tweet_one_image = api.get_status(1416193952751947779)

    # https://twitter.com/Bot2Lovi/status/1416194017197428737
    long_tweet_two_images = api.get_status(1416194017197428737)

    # https://twitter.com/Bot2Lovi/status/1416194068472901634
    long_tweet_three_images = api.get_status(1416194068472901634)

    # https://twitter.com/Bot2Lovi/status/1416194128556199947
    long_tweet_four_image = api.get_status(1416194128556199947)

    # https://twitter.com/Bot2Lovi/status/1416199887293665284
    gif_tweet = api.get_status(1416199887293665284)

    # https://twitter.com/Bot2Lovi/status/1416204465049411593
    at_hash_reddituser_subreddit = api.get_status(1416204465049411593)

    # https://twitter.com/Bot2Lovi/status/1416485664078581761
    retweet_from_somebody_else = api.get_status(1416485664078581761)

    # https://twitter.com/Bot2Lovi/status/1456124564698710017
    link_to_youtube = api.get_status(1456124564698710017)

    webhook_url = os.environ["TEST_WEBHOOK"]

    # Used for testing username/hashtag/reddit user/subreddit regex
    hello_txt = "Hello @TheLovinator1 #Hello /u/test /r/aww"
    hello2_txt = (
        "/r/hello r/hello hello/r/hello /u/hello u/hello hello/u/hello"  # noqa: E501
    )

    short = "Hello I am short Sadge"

    def test_version(self):
        """Test if the version is correct"""
        assert __version__ == "0.3.0"

    def test_send_embed_webhook_one_image(self):
        """Test if the embed webhook is sent correctly"""
        send_embed_webhook(
            tweet=self.short_tweet_one_image,
            webhook=self.webhook_url,
            link_list=["https://pbs.twimg.com/media/E6c309BWYAceCII.jpg"],
            text="Testing embed with one image!",
            twitter_card_image="",
        )

    def test_send_embed_webhook_four_images(self):
        """Test if the embed webhook is sent correctly"""
        send_embed_webhook(
            tweet=self.short_tweet_four_image,
            webhook=self.webhook_url,
            link_list=[
                "https://pbs.twimg.com/media/E6c4jCOXoAIgLW9.jpg",
                "https://pbs.twimg.com/media/E6c4jCQXoAInLOD.jpg",
                "https://pbs.twimg.com/media/E6c4jCNXsAAsiYY.jpg",
                "https://pbs.twimg.com/media/E6c4jCyXMAA4_I9.jpg",
            ],
            text="Testing embed with four images!",
            twitter_card_image="",
        )

    def test_tweet_text(self):
        """Test if the text is returned correctly"""

        assert tweet_text(self.short_tweet_only_text) == self.short

        short1 = "Short 1 Image https://t.co/18WctMxOYa"
        assert tweet_text(self.short_tweet_one_image) == short1

        short2 = "Short 2 Images https://t.co/SPBV5a6YyA"
        assert tweet_text(self.short_tweet_two_images) == short2

        short3 = "Short 3 Images https://t.co/dWPPTQWbHB"
        assert tweet_text(self.short_tweet_three_images) == short3

        short4 = "Short 4 Images https://t.co/OGwDRJCMJF"
        assert tweet_text(self.short_tweet_four_image) == short4

        retweet = "RT @Bot2Lovi: f saf sasaf sa"
        assert tweet_text(self.retweet_from_somebody_else) == retweet

        # TODO: This is not the full text.
        long = "Hello I am longlanglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglong… https://t.co/WuuOFm4xMk"  # noqa, pylint: disable=line-too-long
        assert tweet_text(self.long_tweet_only_text) == long

        long1 = "Long 1 Image Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et… https://t.co/2uafrdmqgg"  # noqa, pylint: disable=line-too-long
        assert tweet_text(self.long_tweet_one_image) == long1

        long2 = "Long 2 Image Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et… https://t.co/DH28OdNtsx"  # noqa, pylint: disable=line-too-long
        assert tweet_text(self.long_tweet_two_images) == long2

        long3 = "Long 3 Image Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et… https://t.co/b1a55tQWAZ"  # noqa, pylint: disable=line-too-long
        assert tweet_text(self.long_tweet_three_images) == long3

        long4 = "Long 4 Image Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et… https://t.co/ehh3OWHbqd"  # noqa, pylint: disable=line-too-long
        assert tweet_text(self.long_tweet_four_image) == long4

    def test_media_links_and_remove_url(self):
        """Test if the media links are returned correctly"""

        # Short tweet, no media
        short_tweet = self.short_tweet_only_text
        short_txt = self.short
        short_1_list = []
        assert media_links_and_remove_url(short_tweet, short_txt) == (
            short_1_list,
            short_txt,
        )

        # Short tweet, one image
        short_1_tweet = self.short_tweet_one_image
        short_1_txt = "Short 1 Image"
        short_1_list = ["https://pbs.twimg.com/media/E6c309BWYAceCII.jpg"]
        assert media_links_and_remove_url(short_1_tweet, short_1_txt) == (
            short_1_list,
            short_1_txt,
        )

        # Short tweet, two images
        short_2_tweet = self.short_tweet_two_images
        short_2_txt = "Short 2 Images"
        short_2_list = [
            "https://pbs.twimg.com/media/E6c4BpyXIAIvvdW.jpg",
            "https://pbs.twimg.com/media/E6c4BqSXMAQq1Fe.jpg",
        ]
        assert media_links_and_remove_url(short_2_tweet, short_2_txt) == (
            short_2_list,
            short_2_txt,
        )

        # Short tweet, three images
        short_3_tweet = self.short_tweet_three_images
        short_3_txt = "Short 3 Images"
        short_3_list = [
            "https://pbs.twimg.com/media/E6c4Zw0WQAQHA6h.jpg",
            "https://pbs.twimg.com/media/E6c4Zw-WUAIr0pJ.jpg",
            "https://pbs.twimg.com/media/E6c4Zx4WUAALtpv.jpg",
        ]
        assert media_links_and_remove_url(short_3_tweet, short_3_txt) == (
            short_3_list,
            short_3_txt,
        )

        # Short tweet, four images
        short_4_tweet = self.short_tweet_four_image
        short_4_txt = "Short 4 Images"
        short_4_list = [
            "https://pbs.twimg.com/media/E6c4jCOXoAIgLW9.jpg",
            "https://pbs.twimg.com/media/E6c4jCQXoAInLOD.jpg",
            "https://pbs.twimg.com/media/E6c4jCNXsAAsiYY.jpg",
            "https://pbs.twimg.com/media/E6c4jCyXMAA4_I9.jpg",
        ]
        assert media_links_and_remove_url(short_4_tweet, short_4_txt) == (
            short_4_list,
            short_4_txt,
        )

        # Short tweet, one gif
        # Returns the thumbnail of the gif, not the gif itself
        gif_tweet = self.gif_tweet
        gif_list = [
            "https://pbs.twimg.com/tweet_video_thumb/E6daSHUX0AYR9ap.jpg",
        ]
        gif_tweet_txt = "Gif"
        assert media_links_and_remove_url(gif_tweet, gif_tweet_txt) == (
            gif_list,
            gif_tweet_txt,
        )

    def test_username_with_link(self):
        """Test if the username is replaced with a link"""
        text = self.hello_txt
        after = "Hello [@TheLovinator1](https://twitter.com/TheLovinator1) #Hello /u/test /r/aww"  # noqa, pylint: disable=line-too-long
        assert username_with_link(text) == after

    def test_hashtag_with_link(self):
        """Test if the hashtag is replaced with a link"""
        text = self.hello_txt
        after = "Hello @TheLovinator1 [#Hello](https://twitter.com/hashtag/Hello) /u/test /r/aww"  # noqa, pylint: disable=line-too-long
        assert hashtag_with_link(text) == after

    def test_subreddit_to_clickable_link(self):
        """Test if the subreddit is replaced with a clickable link"""
        text = self.hello_txt
        after = "Hello @TheLovinator1 #Hello /u/test [/r/aww](https://reddit.com/r/aww)"  # noqa
        assert subreddit_to_link(text) == after

        text2 = self.hello2_txt
        after2 = "[/r/hello](https://reddit.com/r/hello) r/hello hello/r/hello /u/hello u/hello hello/u/hello"
        assert subreddit_to_link(text2) == after2

    def test_reddit_username_to_link(self):
        """Test if the reddit username is replaced with a link"""
        text = self.hello_txt
        after = "Hello @TheLovinator1 #Hello [/u/test](https://reddit.com/u/test) /r/aww"  # noqa
        assert username_to_link(text) == after

        text2 = self.hello2_txt
        after2 = "/r/hello r/hello hello/r/hello [/u/hello](https://reddit.com/u/hello) u/hello hello/u/hello"
        assert username_to_link(text2) == after2

    def test_meta_image(self):
        """Test if the meta image is returned correctly"""
        after = "https://lovinator.space/KaoFace.webp"
        assert meta_image("https://lovinator.space/") == after

    def test_tco_url_link_with_real_link(self):
        """Test if the tco url is replaced with the real link"""

        # No link in the tweet
        assert (
            tco_url_link_with_real_link(
                self.short_tweet_only_text, self.short_tweet_only_text.text
            )
            == self.short
        )

        # One link in the tweet
        assert (
            tco_url_link_with_real_link(
                self.link_to_youtube,
                self.link_to_youtube.text,
            )
            == "https://www.youtube.com/\nHello, this is Youtube"
        )

    def test_discord_link_previews(self):
        """Test if the discord link previews are removed, aka < and >
        are added"""
        before = "https://pbs.twimg.com/tweet_video_thumb/E6daSHUX0AYR9ap.jpg"
        after = "<https://pbs.twimg.com/tweet_video_thumb/E6daSHUX0AYR9ap.jpg>"
        assert discord_link_previews(before) == after

    def test_utm_source(self):
        """Test if the utm source is removed"""
        before = "https://store.steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter"  # noqa, pylint: disable=line-too-long
        after = "https://store.steampowered.com/app/457140/Oxygen_Not_Included/"  # noqa
        assert utm_source(before) == after

    def test_remove_copyright_symbols(self):
        """Test if ®, ™ and © are removed"""
        before = "Hello, © 2020 and I have trademarked ®, ™ and © symbols"
        after = "Hello,  2020 and I have trademarked ,  and  symbols"
        assert copyright_symbols(before) == after
