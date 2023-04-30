import re


def remove_utm(text: str) -> str:
    """Remove the utm_source parameter from the url.

    https://en.wikipedia.org/wiki/UTM_parameters

    Before: steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter

    After: steampowered.com/app/457140/Oxygen_Not_Included/

    Args:
        text: Text from the tweet

    Returns:
        Text with the utm_source parameter removed
    """
    pattern = r"(\?|&)utm_source=[^&]*"
    text = re.sub(pattern, "", text)

    pattern = r"(\?|&)utm_campaign=[^&]*"
    text = re.sub(pattern, "", text)

    pattern = r"(\?|&)utm_medium=[^&]*"
    text = re.sub(pattern, "", text)

    pattern = r"(\?|&)utm_term=[^&]*"
    text = re.sub(pattern, "", text)

    pattern = r"(\?|&)utm_content=[^&]*"
    text = re.sub(pattern, "", text)

    return text
