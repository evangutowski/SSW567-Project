"""
MRTD (Machine-Readable Travel Document) system.
Implements MRZ encoding, decoding, and validation using Fletcher-16 checksums.
"""

import re


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


_MRZ_PATTERN = re.compile(r'^[A-Z0-9<]+$')


def decode_mrz(line1: str, line2: str) -> dict:
    """Decode two 44-character MRZ strings into a dictionary of fields.

    Validates input length and character set. Raises ValueError on invalid input.
    """
    # Validate both lines
    for name, line in [("line1", line1), ("line2", line2)]:
        if len(line) != 44:
            raise ValueError(
                f"{name} must be exactly 44 characters, got {len(line)}"
            )
        if not _MRZ_PATTERN.match(line):
            raise ValueError(
                f"{name} contains invalid characters (only A-Z, 0-9, '<' allowed)"
            )

    # Parse line 1
    document_type = line1[0:2].rstrip('<')
    issuing_country = line1[2:5].rstrip('<')

    # Names field: surname and given names separated by '<<'
    names_raw = line1[5:44]
    parts = names_raw.split('<<')
    surname = parts[0].replace('<', ' ').strip()
    given_names = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""

    # Parse line 2
    passport_number = line2[0:9].rstrip('<')
    check_digit_passport = line2[9]
    country_code = line2[10:13].rstrip('<')
    birth_date = line2[13:19]
    check_digit_birth = line2[19]
    sex = line2[20]
    expiration_date = line2[21:27]
    check_digit_expiration = line2[27]
    personal_number = line2[28:42].rstrip('<')
    check_digit_personal = line2[42]
    overall_check_digit = line2[43]

    return {
        "document_type": document_type,
        "issuing_country": issuing_country,
        "surname": surname,
        "given_names": given_names,
        "passport_number": passport_number,
        "check_digit_passport": check_digit_passport,
        "country_code": country_code,
        "birth_date": birth_date,
        "check_digit_birth": check_digit_birth,
        "sex": sex,
        "expiration_date": expiration_date,
        "check_digit_expiration": check_digit_expiration,
        "personal_number": personal_number,
        "check_digit_personal": check_digit_personal,
        "overall_check_digit": overall_check_digit,
    }


_REQUIRED_ENCODE_FIELDS = [
    "document_type", "issuing_country", "surname", "given_names",
    "passport_number", "country_code", "birth_date", "sex", "expiration_date",
]


def encode_mrz(fields: dict) -> tuple:
    """Encode a dictionary of travel document fields into two 44-char MRZ strings.

    Required fields: document_type, issuing_country, surname, given_names,
    passport_number, country_code, birth_date, sex, expiration_date.
    Optional: personal_number (defaults to '<' padding).
    Raises ValueError if required fields are missing or fixed-length fields are wrong.
    """
    # Check required fields
    for field in _REQUIRED_ENCODE_FIELDS:
        if field not in fields or not fields[field]:
            raise ValueError(f"Required field '{field}' is missing or empty")

    # Extract and normalize fields
    document_type = fields["document_type"].upper()
    issuing_country = fields["issuing_country"].upper()
    surname = fields["surname"].upper().replace(' ', '<')
    given_names = fields["given_names"].upper().replace(' ', '<')
    passport_number = fields["passport_number"].upper()
    country_code = fields["country_code"].upper()
    birth_date = fields["birth_date"]
    sex = fields["sex"].upper()
    expiration_date = fields["expiration_date"]
    personal_number = fields.get("personal_number", "").upper().replace(' ', '<')

    # Validate fixed-length fields
    if len(document_type) < 1 or len(document_type) > 2:
        raise ValueError("document_type must be 1-2 characters")
    if len(issuing_country) != 3:
        raise ValueError("issuing_country must be exactly 3 characters")
    if len(passport_number) != 9:
        raise ValueError("passport_number must be exactly 9 characters")
    if len(country_code) != 3:
        raise ValueError("country_code must be exactly 3 characters")
    if len(birth_date) != 6:
        raise ValueError("birth_date must be exactly 6 characters")
    if len(sex) != 1:
        raise ValueError("sex must be exactly 1 character")
    if len(expiration_date) != 6:
        raise ValueError("expiration_date must be exactly 6 characters")

    # Build line 1: document_type (2) + issuing_country (3) + names (39) = 44
    doc_type_padded = document_type.ljust(2, '<')
    names_field = surname + '<<' + given_names
    names_field = names_field[:39].ljust(39, '<')
    line1 = doc_type_padded + issuing_country + names_field

    # Build line 2
    personal_number_padded = personal_number[:14].ljust(14, '<')

    cd_passport = calculate_check_digit(passport_number)
    cd_birth = calculate_check_digit(birth_date)
    cd_expiration = calculate_check_digit(expiration_date)
    cd_personal = calculate_check_digit(personal_number_padded)

    # Assemble line2 without overall check digit first
    line2_partial = (
        passport_number + str(cd_passport)
        + country_code + birth_date + str(cd_birth)
        + sex + expiration_date + str(cd_expiration)
        + personal_number_padded + str(cd_personal)
    )

    # Overall check digit: computed over positions 1-10, 14-20, 22-43 (1-indexed)
    # In 0-indexed: [0:10] + [13:20] + [21:43]
    overall_data = line2_partial[0:10] + line2_partial[13:20] + line2_partial[21:43]
    cd_overall = calculate_check_digit(overall_data)

    line2 = line2_partial + str(cd_overall)

    return (line1, line2)
