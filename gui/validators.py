def is_positive_number(number_str: str) -> bool:
    """
    Checking a string for whether it is a positive number.

    Args:
        number_str (str): String to be checked.
    Returns:
        True if the string is a positive number or empty string, otherwise False
    """
    if number_str.isdigit():
        return int(number_str) >= 0
    elif number_str == "":
        return True
    else:
        return False


def get_number(number_str: str) -> int:
    """
    Function to get a number from a string.

    Args:
        number_str (str): String to be converted to a number.
    Returns:
        The number obtained from the input string.
    """
    if number_str == "":
        return 0
    else:
        return int(number_str)
