from discord_twitter_webhooks.reddit import subreddit_to_link, username_to_link


class TestReddit:
    """Test things from discord_twitter_webhooks/reddit.py"""

    hello_txt = "Hello @TheLovinator1 #Hello /u/test /r/aww"
    hello2_txt = "/r/hello r/hello hello/r/hello /u/hello u/hello hello/u/hello"  # noqa: E501, pylint: disable=line-too-long

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
