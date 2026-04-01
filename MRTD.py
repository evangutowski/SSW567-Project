"""
MRTD (Machine-Readable Travel Document) system.
Implements MRZ encoding, decoding, and validation using Fletcher-16 checksums.
"""


def _char_to_value(c):
    """Convert an MRZ character to its numeric value.
    Digits 0-9 -> 0-9, letters A-Z -> 10-35, '<' -> 0.
    """
    if c.isdigit():
        return int(c)
    elif c.isalpha() and c.isupper():
        return ord(c) - ord('A') + 10
    elif c == '<':
        return 0
    else:
        raise ValueError(f"Invalid MRZ character: '{c}'")


def calculate_check_digit(data: str) -> int:
    """Calculate a check digit using the Fletcher-16 algorithm.

    For each character, convert to numeric value then update running sums:
        sum1 = (sum1 + value) mod 255
        sum2 = (sum2 + sum1) mod 255
    Checksum = (sum2 << 8) | sum1
    Returns checksum mod 10.
    """
    sum1, sum2 = 0, 0
    for c in data:
        value = _char_to_value(c)
        sum1 = (sum1 + value) % 255
        sum2 = (sum2 + sum1) % 255
    checksum = (sum2 << 8) | sum1
    return checksum % 10


def scan_mrz():
    """Stub: simulate scanning a passport MRZ. Hardware scanner not available."""
    return ("", "")


def query_database():
    """Stub: simulate querying a travel document database."""
    return None
