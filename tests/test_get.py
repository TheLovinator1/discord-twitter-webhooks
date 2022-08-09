from discord_twitter_webhooks.get import media_links, meta_image, tweet_urls


class TestGet:
    def test_media_links(self):
        """Test if the media links are returned correctly"""

        media = [{'media_key': '3_1556972775885230080', 'type': 'photo',
                  'url': 'https://pbs.twimg.com/media/FZt6fY-X0AABEHR.jpg'},
                 {'media_key': '3_1556972776094842882', 'type': 'photo',
                  'url': 'https://pbs.twimg.com/media/FZt6fZwWQAIV-v5.jpg'},
                 {'media_key': '3_1556972776229146626', 'type': 'photo',
                  'url': 'https://pbs.twimg.com/media/FZt6faQXkAIeAzF.jpg'},
                 {'media_key': '3_1556972776371658752', 'type': 'photo',
                  'url': 'https://pbs.twimg.com/media/FZt6fayWIAAvSOr.jpg'}]

        assert media_links(media=media) == ['https://pbs.twimg.com/media/FZt6fY-X0AABEHR.jpg',
                                            'https://pbs.twimg.com/media/FZt6fZwWQAIV-v5.jpg',
                                            'https://pbs.twimg.com/media/FZt6faQXkAIeAzF.jpg',
                                            'https://pbs.twimg.com/media/FZt6fayWIAAvSOr.jpg']

    def test_meta_image(self):
        """Test if the meta image is returned correctly"""
        after = "https://lovinator.space/KaoFace.webp"
        assert meta_image("https://lovinator.space/") == after

    def test_tweet_url(self):
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

        # TODO: This is broken
        assert tweet_urls(entities=entities) == []
