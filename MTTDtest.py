"""
Comprehensive unit tests for MRTD (Machine-Readable Travel Document) system.
Uses unittest framework with unittest.mock for stub functions.
"""

import unittest
from unittest.mock import patch
from MRTD import (
    calculate_check_digit, scan_mrz, query_database, decode_mrz, encode_mrz,
)


class TestCalculateCheckDigit(unittest.TestCase):
    """Tests for the Fletcher-16 based check digit calculation."""

    # Test that an empty string returns 0 (sum1=0, sum2=0, checksum=0, 0%10=0)
    def test_empty_string(self):
        self.assertEqual(calculate_check_digit(""), 0)

    # Test a single digit character — value 5, sum1=5, sum2=5, checksum=(5<<8)|5=1285, 1285%10=5
    def test_single_digit(self):
        self.assertEqual(calculate_check_digit("5"), 5)

    # Test a single letter A — value 10, sum1=10, sum2=10, checksum=(10<<8)|10=2570, 2570%10=0
    def test_single_letter_a(self):
        self.assertEqual(calculate_check_digit("A"), 0)

    # Test all zeros — all values are 0, sums stay 0, result is 0
    def test_all_zeros(self):
        self.assertEqual(calculate_check_digit("000000"), 0)

    # Test all filler characters '<' — each maps to value 0, same as all zeros
    def test_all_fillers(self):
        self.assertEqual(calculate_check_digit("<<<<<<<<<<<<<<"), 0)

    # Test reference passport number "L898902C3" — pre-computed Fletcher-16 result is 4
    def test_passport_number_reference(self):
        self.assertEqual(calculate_check_digit("L898902C3"), 4)

    # Test reference birth date "740812" — pre-computed Fletcher-16 result is 2
    def test_birth_date_reference(self):
        self.assertEqual(calculate_check_digit("740812"), 2)

    # Test reference expiration date "120415" — pre-computed Fletcher-16 result is 3
    def test_expiration_date_reference(self):
        self.assertEqual(calculate_check_digit("120415"), 3)

    # Test reference personal number "ZE184226B<<<<<" — pre-computed Fletcher-16 result is 7
    def test_personal_number_reference(self):
        self.assertEqual(calculate_check_digit("ZE184226B<<<<<"), 7)

    # Test a mixed alphanumeric string to verify correct character-to-value mapping
    def test_mixed_alphanumeric(self):
        # "ABC123": A=10, B=11, C=12, 1=1, 2=2, 3=3
        # Manual Fletcher-16 computation:
        # sum1=10, sum2=10
        # sum1=21, sum2=31
        # sum1=33, sum2=64
        # sum1=34, sum2=98
        # sum1=36, sum2=134
        # sum1=39, sum2=173
        # checksum = (173 << 8) | 39 = 44327, 44327 % 10 = 7
        self.assertEqual(calculate_check_digit("ABC123"), 7)


class TestScanMRZ(unittest.TestCase):
    """Tests for the scan_mrz stub and its mocked behavior."""

    # Test that the stub returns a tuple
    def test_scan_mrz_returns_tuple(self):
        result = scan_mrz()
        self.assertIsInstance(result, tuple)

    # Test that the stub returns two strings
    def test_scan_mrz_returns_two_strings(self):
        result = scan_mrz()
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], str)

    # Test mocking scan_mrz to return valid MRZ lines (UTO passport)
    @patch("MRTD.scan_mrz")
    def test_scan_mrz_mock_valid_data(self, mock_scan):
        mock_scan.return_value = (
            "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
            "L898902C34UTO7408122F1204153ZE184226B<<<<<70",
        )
        line1, line2 = mock_scan()
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)


class TestQueryDatabase(unittest.TestCase):
    """Tests for the query_database stub and its mocked behavior."""

    # Test that the stub returns None
    def test_query_database_returns_none(self):
        result = query_database()
        self.assertIsNone(result)

    # Test mocking query_database to return a passport record dict
    @patch("MRTD.query_database")
    def test_query_database_mock_result(self, mock_db):
        mock_db.return_value = {
            "surname": "ERIKSSON",
            "given_names": "ANNA MARIA",
            "passport_number": "L898902C3",
        }
        result = mock_db()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["surname"], "ERIKSSON")

    # Test mocking query_database to return None for an unknown passport
    @patch("MRTD.query_database")
    def test_query_database_mock_not_found(self, mock_db):
        mock_db.return_value = None
        result = mock_db()
        self.assertIsNone(result)


class TestDecodeMRZ(unittest.TestCase):
    """Tests for decoding MRZ strings into field dictionaries."""

    # Test decoding the reference UTO passport (Fletcher-16 corrected line 2)
    def test_decode_reference_uto(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C34UTO7408122F1204153ZE184226B<<<<<70"
        result = decode_mrz(line1, line2)
        self.assertEqual(result["document_type"], "P")
        self.assertEqual(result["issuing_country"], "UTO")
        self.assertEqual(result["surname"], "ERIKSSON")
        self.assertEqual(result["given_names"], "ANNA MARIA")
        self.assertEqual(result["passport_number"], "L898902C3")
        self.assertEqual(result["check_digit_passport"], "4")
        self.assertEqual(result["country_code"], "UTO")
        self.assertEqual(result["birth_date"], "740812")
        self.assertEqual(result["check_digit_birth"], "2")
        self.assertEqual(result["sex"], "F")
        self.assertEqual(result["expiration_date"], "120415")
        self.assertEqual(result["check_digit_expiration"], "3")
        self.assertEqual(result["personal_number"], "ZE184226B")
        self.assertEqual(result["check_digit_personal"], "7")
        self.assertEqual(result["overall_check_digit"], "0")

    # Test decoding a USA passport
    def test_decode_usa_passport(self):
        line1 = "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        line2 = "AB1234567" + "1" + "USA" + "950101" + "4" + "M" + "250101" + "5" + "<<<<<<<<<<<<<<" + "0" + "4"
        # Verify line2 is 44 chars
        self.assertEqual(len(line2), 44)
        result = decode_mrz(line1, line2)
        self.assertEqual(result["surname"], "SMITH")
        self.assertEqual(result["given_names"], "JOHN")
        self.assertEqual(result["issuing_country"], "USA")
        self.assertEqual(result["passport_number"], "AB1234567")
        self.assertEqual(result["sex"], "M")

    # Test decoding a GBR passport with multiple given names
    def test_decode_gbr_passport(self):
        line1 = "P<GBRJONES<<ELIZABETH<MARY<<<<<<<<<<<<<<<<<<"
        line2 = "CD9876543" + "5" + "GBR" + "880515" + "7" + "F" + "280515" + "5" + "12345<<<<<<<<<" + "2" + "8"
        self.assertEqual(len(line2), 44)
        result = decode_mrz(line1, line2)
        self.assertEqual(result["surname"], "JONES")
        self.assertEqual(result["given_names"], "ELIZABETH MARY")
        self.assertEqual(result["country_code"], "GBR")

    # Test decoding a DEU passport
    def test_decode_deu_passport(self):
        line1 = "P<DEUMUELLER<<HANS<<<<<<<<<<<<<<<<<<<<<<<<<<"
        line2 = "XY0000001" + "8" + "DEU" + "700101" + "5" + "M" + "300101" + "7" + "<<<<<<<<<<<<<<" + "0" + "4"
        self.assertEqual(len(line2), 44)
        result = decode_mrz(line1, line2)
        self.assertEqual(result["surname"], "MUELLER")
        self.assertEqual(result["given_names"], "HANS")
        self.assertEqual(result["issuing_country"], "DEU")

    # Test decoding a JPN passport
    def test_decode_jpn_passport(self):
        line1 = "P<JPNTANAKA<<YUKI<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        line2 = "JP5551234" + "5" + "JPN" + "901231" + "2" + "F" + "301231" + "0" + "<<<<<<<<<<<<<<" + "0" + "8"
        self.assertEqual(len(line2), 44)
        result = decode_mrz(line1, line2)
        self.assertEqual(result["surname"], "TANAKA")
        self.assertEqual(result["given_names"], "YUKI")
        self.assertEqual(result["issuing_country"], "JPN")

    # Test decoding a FRA passport with three given names
    def test_decode_fra_passport(self):
        line1 = "P<FRADUPONT<<JEAN<PIERRE<LOUIS<<<<<<<<<<<<<<"
        line2 = "FR1112223" + "4" + "FRA" + "650720" + "6" + "M" + "250720" + "8" + "ABC123<<<<<<<<" + "9" + "4"
        self.assertEqual(len(line2), 44)
        result = decode_mrz(line1, line2)
        self.assertEqual(result["surname"], "DUPONT")
        self.assertEqual(result["given_names"], "JEAN PIERRE LOUIS")
        self.assertEqual(result["issuing_country"], "FRA")

    # Test that line1 shorter than 44 chars raises ValueError
    def test_decode_wrong_length_line1(self):
        line2 = "L898902C34UTO7408122F1204153ZE184226B<<<<<70"
        with self.assertRaises(ValueError):
            decode_mrz("P<UTOERIKSSON<<ANNA<MARIA", line2)

    # Test that line2 shorter than 44 chars raises ValueError
    def test_decode_wrong_length_line2(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        with self.assertRaises(ValueError):
            decode_mrz(line1, "L898902C34UTO740812")

    # Test that lowercase characters in input raise ValueError
    def test_decode_invalid_chars_lowercase(self):
        line1 = "p<utoeriksson<<anna<maria<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C34UTO7408122F1204153ZE184226B<<<<<70"
        with self.assertRaises(ValueError):
            decode_mrz(line1, line2)

    # Test that spaces in input raise ValueError
    def test_decode_invalid_chars_spaces(self):
        line1 = "P UTOERIKSSON  ANNA MARIA                   "
        line2 = "L898902C34UTO7408122F1204153ZE184226B<<<<<70"
        with self.assertRaises(ValueError):
            decode_mrz(line1, line2)

    # Test that special characters raise ValueError
    def test_decode_invalid_chars_special(self):
        line1 = "P!UTOERIKSSON@@ANNA#MARIA$$$$$$$$$$$$$$$$$$$"
        line2 = "L898902C34UTO7408122F1204153ZE184226B<<<<<70"
        with self.assertRaises(ValueError):
            decode_mrz(line1, line2)

    # Test decoding when personal_number is all '<' (empty)
    def test_decode_empty_personal_number(self):
        line1 = "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        line2 = "AB1234567" + "1" + "USA" + "950101" + "4" + "M" + "250101" + "5" + "<<<<<<<<<<<<<<" + "0" + "4"
        result = decode_mrz(line1, line2)
        self.assertEqual(result["personal_number"], "")

    # Test decoding a passport with surname only (no given names)
    def test_decode_surname_only(self):
        line1 = "P<USOMADONNA<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        line2 = "AB1234567" + "1" + "USO" + "950101" + "4" + "F" + "250101" + "5" + "<<<<<<<<<<<<<<" + "0" + "4"
        self.assertEqual(len(line1), 44)
        result = decode_mrz(line1, line2)
        self.assertEqual(result["surname"], "MADONNA")
        self.assertEqual(result["given_names"], "")


class TestEncodeMRZ(unittest.TestCase):
    """Tests for encoding field dictionaries into MRZ strings."""

    def _uto_fields(self):
        """Helper: return the reference UTO passport fields."""
        return {
            "document_type": "P",
            "issuing_country": "UTO",
            "surname": "ERIKSSON",
            "given_names": "ANNA MARIA",
            "passport_number": "L898902C3",
            "country_code": "UTO",
            "birth_date": "740812",
            "sex": "F",
            "expiration_date": "120415",
            "personal_number": "ZE184226B",
        }

    # Test encoding reference UTO passport produces correct 44-char lines
    def test_encode_reference_uto(self):
        fields = self._uto_fields()
        line1, line2 = encode_mrz(fields)
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)
        self.assertEqual(line1, "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<")
        # Verify check digits match Fletcher-16 pre-computed values
        self.assertEqual(line2[9], "4")   # passport check digit
        self.assertEqual(line2[19], "2")  # birth date check digit
        self.assertEqual(line2[27], "3")  # expiration check digit
        self.assertEqual(line2[42], "7")  # personal number check digit
        self.assertEqual(line2[43], "0")  # overall check digit

    # Test encoding a USA passport
    def test_encode_usa_passport(self):
        fields = {
            "document_type": "P",
            "issuing_country": "USA",
            "surname": "SMITH",
            "given_names": "JOHN",
            "passport_number": "AB1234567",
            "country_code": "USA",
            "birth_date": "950101",
            "sex": "M",
            "expiration_date": "250101",
        }
        line1, line2 = encode_mrz(fields)
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)
        self.assertEqual(line1, "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        self.assertEqual(line2[10:13], "USA")

    # Test encoding a FRA passport with multiple given names
    def test_encode_fra_passport(self):
        fields = {
            "document_type": "P",
            "issuing_country": "FRA",
            "surname": "DUPONT",
            "given_names": "JEAN PIERRE LOUIS",
            "passport_number": "FR1112223",
            "country_code": "FRA",
            "birth_date": "650720",
            "sex": "M",
            "expiration_date": "250720",
        }
        line1, line2 = encode_mrz(fields)
        self.assertEqual(len(line1), 44)
        self.assertIn("DUPONT<<JEAN<PIERRE<LOUIS", line1)

    # Test encoding without personal_number defaults to all '<' padding
    def test_encode_no_personal_number(self):
        fields = self._uto_fields()
        del fields["personal_number"]
        line1, line2 = encode_mrz(fields)
        self.assertEqual(len(line2), 44)
        # personal_number field (pos 29-42) should be all '<'
        self.assertEqual(line2[28:42], "<<<<<<<<<<<<<<")

    # Test that missing required field 'surname' raises ValueError
    def test_encode_missing_surname(self):
        fields = self._uto_fields()
        del fields["surname"]
        with self.assertRaises(ValueError):
            encode_mrz(fields)

    # Test that missing required field 'passport_number' raises ValueError
    def test_encode_missing_passport_number(self):
        fields = self._uto_fields()
        del fields["passport_number"]
        with self.assertRaises(ValueError):
            encode_mrz(fields)

    # Test that missing required field 'birth_date' raises ValueError
    def test_encode_missing_birth_date(self):
        fields = self._uto_fields()
        del fields["birth_date"]
        with self.assertRaises(ValueError):
            encode_mrz(fields)

    # Test that wrong-length passport_number raises ValueError
    def test_encode_wrong_length_passport(self):
        fields = self._uto_fields()
        fields["passport_number"] = "SHORT"
        with self.assertRaises(ValueError):
            encode_mrz(fields)

    # Test that wrong-length birth_date raises ValueError
    def test_encode_wrong_length_birth_date(self):
        fields = self._uto_fields()
        fields["birth_date"] = "19740812"
        with self.assertRaises(ValueError):
            encode_mrz(fields)

    # Test that wrong-length country_code raises ValueError
    def test_encode_wrong_length_country(self):
        fields = self._uto_fields()
        fields["country_code"] = "UTOPIA"
        with self.assertRaises(ValueError):
            encode_mrz(fields)

    # Test that lowercase input is converted to uppercase automatically
    def test_encode_lowercase_input(self):
        fields = self._uto_fields()
        fields["surname"] = "eriksson"
        fields["given_names"] = "anna maria"
        line1, line2 = encode_mrz(fields)
        self.assertIn("ERIKSSON", line1)
        self.assertIn("ANNA<MARIA", line1)

    # Test that both output lines are always exactly 44 characters
    def test_encode_output_lengths(self):
        fields = self._uto_fields()
        line1, line2 = encode_mrz(fields)
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)


if __name__ == "__main__":
    unittest.main()
