from discord_twitter_webhooks.get import media_links


def test_media_links() -> None:
    """Test if the media links are returned correctly."""
    media: list[dict[str, str]] = [
        {
            "media_key": "3_1556972775885230080",
            "type": "photo",
            "url": "https://pbs.twimg.com/media/FZt6fY-X0AABEHR.jpg",
        },
        {
            "media_key": "3_1556972776094842882",
            "type": "photo",
            "url": "https://pbs.twimg.com/media/FZt6fZwWQAIV-v5.jpg",
        },
        {
            "media_key": "3_1556972776229146626",
            "type": "photo",
            "url": "https://pbs.twimg.com/media/FZt6faQXkAIeAzF.jpg",
        },
        {
            "media_key": "3_1556972776371658752",
            "type": "photo",
            "url": "https://pbs.twimg.com/media/FZt6fayWIAAvSOr.jpg",
        },
    ]

    assert media_links(media=media) == [
        "https://pbs.twimg.com/media/FZt6fY-X0AABEHR.jpg",
        "https://pbs.twimg.com/media/FZt6fZwWQAIV-v5.jpg",
        "https://pbs.twimg.com/media/FZt6faQXkAIeAzF.jpg",
        "https://pbs.twimg.com/media/FZt6fayWIAAvSOr.jpg",
    ]
