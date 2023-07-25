import re


def check_word_in_string(input_string: str, word: str) -> bool:
    """Check if a word exists in the input string.

    Parameters:
        input_string (str): The input string to search for the word.
        word (str): The word to search for.

    Returns:
        bool: True if the word is found, False otherwise.
    """
    # If the word is in the list of words, return True, otherwise, return False
    return word in input_string


def check_word_in_string_regex(input_string: str, regex_pattern: str) -> bool:
    """Check if a word matching the given regular expression pattern exists in the input string.

    Parameters:
        input_string (str): The input string to search for the word.
        regex_pattern (str): The regular expression pattern to match the word.

    Returns:
        bool: True if the word matching the pattern is found, False otherwise.
    """
    # Compile the regex pattern
    pattern = re.compile(regex_pattern, flags=re.IGNORECASE)

    # Search for the pattern in the input string
    match = pattern.search(input_string)

    # If the pattern is found, return True, otherwise, return False
    return match is not None
