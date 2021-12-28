def get_urls(tweet) -> list[str]:
    """Get the URLs from the tweet and add them to a list.

    We use this to get the images from websites.

    Args:
        tweet ([type]): Tweet object

    Returns:
        list[str]: Urls from the tweet
    """
    url_list = []
    try:
        for url in tweet.extended_tweet["entities"]["urls"]:
            url_list.append(url["expanded_url"])
    except AttributeError:
        # Tweet is less than 140 characters
        try:
            for url in tweet.entities["urls"]:
                url_list.append(url["expanded_url"])
        except AttributeError:
            # Tweet has no links
            pass
    return url_list
