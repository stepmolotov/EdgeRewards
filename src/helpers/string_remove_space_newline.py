import re


def string_remove_space_newline(string: str) -> str:
    """
    Remove spaces, dots and newlines from a string.
    :param string: The string to remove spaces and newlines from.
    :return: The string with spaces and newlines removed.
    """
    return re.sub(r"[\n\t\s]*", "", string.replace(".", ""))
