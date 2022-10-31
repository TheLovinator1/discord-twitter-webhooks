from discord_twitter_webhooks.remove import (copyright_symbols, discord_link_previews, remove_media_links, utm_source)


class TestRemove:
    """Test things from discord_twitter_webhooks/remove.py"""

    hello_txt = "Hello @TheLovinator1 #Hello /u/test /r/aww"
    hello2_txt = "/r/hello r/hello hello/r/hello /u/hello u/hello hello/u/hello"

    short = "Hello I am short Sadge"

    def test_discord_link_previews(self):
        """Test if the discord link previews are removed, aka < and >
        are added."""
        before = "https://pbs.twimg.com/tweet_video_thumb/E6daSHUX0AYR9ap.jpg"
        after = "<https://pbs.twimg.com/tweet_video_thumb/E6daSHUX0AYR9ap.jpg>"
        assert discord_link_previews(before) == after

    def test_utm_source(self):
        """Test if the utm source is removed."""
        before = "https://store.steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter"  # noqa
        after = "https://store.steampowered.com/app/457140/Oxygen_Not_Included/"
        assert utm_source(before) == after

    def test_remove_copyright_symbols(self):
        """Test if ®, ™ and © are removed."""
        before = "Hello© 2020 and I have trademarked®, ™ and © symbols"
        after = "Hello 2020 and I have trademarked,  and  symbols"
        assert copyright_symbols(before) == after

    def test_remove_media_links(self):
        """Test if the media links are removed."""
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
        assert remove_media_links(entities=entities,
                                  text='fs fsf fa fafa af https://t.co/x5R5a8MWYW') == 'fs fsf fa fafa af '
