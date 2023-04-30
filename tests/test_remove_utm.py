from discord_twitter_webhooks.remove_utm import remove_utm


def test_remove_utm() -> None:
    """Test remove_utm()."""
    test_string = (
        "steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter"
    )
    assert remove_utm(test_string) == "steampowered.com/app/457140/Oxygen_Not_Included/"
