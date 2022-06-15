from discord_twitter_webhooks.get import meta_image


class TestGet:
    hello_txt = "Hello @TheLovinator1 #Hello /u/test /r/aww"
    hello2_txt = "/r/hello r/hello hello/r/hello /u/hello u/hello hello/u/hello"  # noqa: E501, pylint: disable=line-too-long

    short = "Hello I am short Sadge"

    def test_meta_image(self):
        """Test if the meta image is returned correctly"""
        after = "https://lovinator.space/KaoFace.webp"
        assert meta_image("https://lovinator.space/") == after
