def remove_copyright(tweet_text: str) -> str:
    """Remove the copyright.

    Args:
        tweet_text: The tweet text.
        reader: The reader to use to get the tag.

    Returns:
        The tweet text with the copyright removed.
    """
    # Remove the "©" symbol.
    tweet_text = tweet_text.replace("©", "")

    # Remove the trademark symbol.
    tweet_text = tweet_text.replace("™", "")

    # Remove the registered trademark symbol.
    return tweet_text.replace("®", "")
