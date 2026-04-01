"""
Comprehensive unit tests for MRTD (Machine-Readable Travel Document) system.
Uses unittest framework with unittest.mock for stub functions.
"""

import unittest
from unittest.mock import patch
from MRTD import calculate_check_digit, scan_mrz, query_database


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


if __name__ == "__main__":
    unittest.main()
