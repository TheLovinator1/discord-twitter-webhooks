from discord_twitter_webhooks.remove import (
    copyright_symbols,
    discord_link_previews,
    utm_source,
)


class TestRemove:
    """Test things from discord_twitter_webhooks/remove.py"""

    hello_txt = "Hello @TheLovinator1 #Hello /u/test /r/aww"
    hello2_txt = "/r/hello r/hello hello/r/hello /u/hello u/hello hello/u/hello"  # noqa: E501, pylint: disable=line-too-long

    short = "Hello I am short Sadge"

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
