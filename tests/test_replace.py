from discord_twitter_webhooks.replace import hashtag_with_link, tco_url_link_with_real_link, username_with_link


class TestReplace:
    """Test things from discord_twitter_webhooks/replace.py"""

    hello_txt = "Hello @TheLovinator1 #Hello /u/test /r/aww"
    hello2_txt = "/r/hello r/hello hello/r/hello /u/hello u/hello hello/u/hello"

    def test_username_with_link(self):
        """Test if the username is replaced with a link."""
        text = self.hello_txt
        after = "Hello [@TheLovinator1](https://twitter.com/TheLovinator1) #Hello /u/test /r/aww"
        assert username_with_link(text) == after

    def test_hashtag_with_link(self):
        """Test if the hashtag is replaced with a link."""
        text = self.hello_txt
        after = "Hello @TheLovinator1 [#Hello](https://twitter.com/hashtag/Hello) /u/test /r/aww"
        assert hashtag_with_link(text) == after

    def test_tco_url_link_with_real_link(self):
        """Test if the t.co url is replaced with the real url."""
        entities = {'urls': [{'start': 18, 'end': 41, 'url': 'https://t.co/x5R5a8MWYW',
                              'expanded_url': 'https://twitter.com/Bot2Lovi/status/1556986132813971458/photo/1',
                              'display_url': 'pic.twitter.com/x5R5a8MWYW', 'media_key': '3_1556986120398929925'},
                             {'start': 18, 'end': 41, 'url': 'https://t.co/x5R5a8MWYW',
                              'expanded_url': 'https://twitter.com/Bot2Lovi/status/1556986132813971458/photo/1',
                              'display_url': 'pic.twitter.com/x5R5a8MWYW', 'media_key': '3_1556986120415711233'},
                             {'start': 18, 'end': 41, 'url': 'https://t.co/x5R5a8MWYW',
                              'expanded_url': 'https://twitter.com/Bot2Lovi/status/1556986132813971458/photo/1',
                              'display_url': 'pic.twitter.com/x5R5a8MWYW', 'media_key': '3_1556986120587689984'},
                             {'start': 18, 'end': 41, 'url': 'https://t.co/x5R5a8MWYW',
                              'expanded_url': 'https://twitter.com/Bot2Lovi/status/1556986132813971458/photo/1',
                              'display_url': 'pic.twitter.com/x5R5a8MWYW', 'media_key': '3_1556986120512192514'}]}
        assert tco_url_link_with_real_link(entities,
                                           "Hello https://t.co/x5R5a8MWYW") == "Hello https://twitter.com/Bot2Lovi/status/1556986132813971458/photo/1"

    def test_mastodon_links(self):
        link = "https://mastodon.gamedev.place/@eloraam?hello#something"
        link_and_twitter = "https://mastodon.gamedev.place/@eloraam?hello#something @eloraam #Hello"
        assert username_with_link(link) == link
        assert username_with_link(
            link_and_twitter) == "https://mastodon.gamedev.place/@eloraam?hello#something [@eloraam](https://twitter.com/eloraam) #Hello"
        assert hashtag_with_link(link) == link
        assert hashtag_with_link(
            link_and_twitter) == "https://mastodon.gamedev.place/@eloraam?hello#something @eloraam [#Hello](https://twitter.com/hashtag/Hello)"
