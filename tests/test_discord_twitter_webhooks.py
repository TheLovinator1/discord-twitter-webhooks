from discord_twitter_webhooks import __version__
from discord_twitter_webhooks.get import meta_image
from discord_twitter_webhooks.reddit import subreddit_to_link, username_to_link
from discord_twitter_webhooks.remove import (
    copyright_symbols,
    discord_link_previews,
    utm_source,
)
from discord_twitter_webhooks.replace import (  # noqa: E501, pylint: disable=line-too-long
    hashtag_with_link,
    username_with_link,
)


class TestTweets:
    """Test tweet stuff"""

    # Used for testing username/hashtag/reddit user/subreddit regex
    hello_txt = "Hello @TheLovinator1 #Hello /u/test /r/aww"
    hello2_txt = "/r/hello r/hello hello/r/hello /u/hello u/hello hello/u/hello"  # noqa: E501, pylint: disable=line-too-long

    short = "Hello I am short Sadge"

    def test_version(self):
        """Test if the version is correct"""
        assert __version__ == "2.0.0"

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
        after2 = "[/r/hello](https://reddit.com/r/hello) r/hello hello/r/hello /u/hello u/hello hello/u/hello"  # noqa: E501, pylint: disable=line-too-long
        assert subreddit_to_link(text2) == after2

    def test_reddit_username_to_link(self):
        """Test if the reddit username is replaced with a link"""
        text = self.hello_txt
        after = "Hello @TheLovinator1 #Hello [/u/test](https://reddit.com/u/test) /r/aww"  # noqa
        assert username_to_link(text) == after

        text2 = self.hello2_txt
        after2 = "/r/hello r/hello hello/r/hello [/u/hello](https://reddit.com/u/hello) u/hello hello/u/hello"  # noqa: E501, pylint: disable=line-too-long
        assert username_to_link(text2) == after2

    def test_meta_image(self):
        """Test if the meta image is returned correctly"""
        after = "https://lovinator.space/KaoFace.webp"
        assert meta_image("https://lovinator.space/") == after

    def test_discord_link_previews(self):
        """Test if the discord link previews are removed, aka < and >
        are added"""
        before = "https://pbs.twimg.com/tweet_video_thumb/E6daSHUX0AYR9ap.jpg"
        after = "<https://pbs.twimg.com/tweet_video_thumb/E6daSHUX0AYR9ap.jpg>"
        assert discord_link_previews(before) == after

    def test_utm_source(self):
        """Test if the utm source is removed"""
        before = "https://store.steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter"  # noqa, pylint: disable=line-too-long
        after = "https://store.steampowered.com/app/457140/Oxygen_Not_Included/"  # noqa: E501, pylint: disable=line-too-long
        assert utm_source(before) == after

    def test_remove_copyright_symbols(self):
        """Test if ®, ™ and © are removed"""
        before = "Hello© 2020 and I have trademarked®, ™ and © symbols"
        after = "Hello 2020 and I have trademarked,  and  symbols"
        assert copyright_symbols(before) == after
