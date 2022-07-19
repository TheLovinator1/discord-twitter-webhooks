from discord_twitter_webhooks.replace import hashtag_with_link, username_with_link


class TestReplace:
    """Test things from discord_twitter_webhooks/replace.py"""

    hello_txt = "Hello @TheLovinator1 #Hello /u/test /r/aww"
    hello2_txt = "/r/hello r/hello hello/r/hello /u/hello u/hello hello/u/hello"

    def test_username_with_link(self):
        """Test if the username is replaced with a link"""
        text = self.hello_txt
        after = "Hello [@TheLovinator1](https://twitter.com/TheLovinator1) #Hello /u/test /r/aww"
        assert username_with_link(text) == after

    def test_hashtag_with_link(self):
        """Test if the hashtag is replaced with a link"""
        text = self.hello_txt
        after = "Hello @TheLovinator1 [#Hello](https://twitter.com/hashtag/Hello) /u/test /r/aww"
        assert hashtag_with_link(text) == after
