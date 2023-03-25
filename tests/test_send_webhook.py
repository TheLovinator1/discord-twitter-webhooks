from discord_webhook import DiscordEmbed

from discord_twitter_webhooks.send_webhook import set_color


def test_set_color() -> None:
    """Test that set_color sets the color of the embed without error."""
    # TODO: Add more tests.
    embed: DiscordEmbed = DiscordEmbed(description="Test description")

    set_color(embed)
    assert isinstance(embed.color, int)
