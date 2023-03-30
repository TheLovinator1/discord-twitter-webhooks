from discord_twitter_webhooks.send_webhook import get_color


def test_set_color() -> None:
    """Test that set_color sets the color of the embed without error."""
    # TODO: Add more tests.

    color: int = get_color()
    assert isinstance(color, int)
