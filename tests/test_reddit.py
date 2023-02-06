from discord_twitter_webhooks.reddit import subreddit_to_link, username_to_link

hello_txt: str = "Hello @TheLovinator1 #Hello /u/test /r/aww"
hello2_txt: str = "/r/hello r/hello hello/r/hello /u/hello u/hello hello/u/hello"


def test_subreddit_to_clickable_link() -> None:
    """Test if the subreddit is replaced with a clickable link."""

    def test_subreddit(text: str, after: str) -> None:
        assert subreddit_to_link(text) == after

    test_subreddit(hello_txt, "Hello @TheLovinator1 #Hello /u/test [/r/aww](https://reddit.com/r/aww)")
    test_subreddit(hello2_txt, "[/r/hello](https://reddit.com/r/hello) r/hello hello/r/hello /u/hello u/hello hello/u/hello")  # noqa: E501


def test_reddit_username_to_link() -> None:
    """Test if the reddit username is replaced with a link."""

    def test_username(text: str, after: str) -> None:
        assert username_to_link(text) == after

    test_username(hello_txt, "Hello @TheLovinator1 #Hello [/u/test](https://reddit.com/u/test) /r/aww")  # noqa: E501
    test_username(hello2_txt, "/r/hello r/hello hello/r/hello [/u/hello](https://reddit.com/u/hello) u/hello hello/u/hello")  # noqa: E501
