"""
Comprehensive unit tests for MRTD (Machine-Readable Travel Document) system.
Uses unittest framework with unittest.mock for stub functions.
"""

import unittest
from MRTD import decode_mrz, encode_mrz, validate_mrz
from tests.test_calculate_check_digit import TestCalculateCheckDigit
from tests.test_scan_mrz import TestScanMRZ
from tests.test_query_database import TestQueryDatabase
from tests.test_decode_mrz import TestDecodeMRZ


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


class TestValidateMRZ(unittest.TestCase):
    """Tests for MRZ check digit validation."""

    # Valid Fletcher-16 MRZ lines (produced by encode_mrz)
    UTO_LINE1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
    UTO_LINE2 = "L898902C34UTO7408122F1204153ZE184226B<<<<<70"
    USA_LINE1 = "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    USA_LINE2 = "AB12345671USA9501014M2501015<<<<<<<<<<<<<<04"

    # Test that a valid UTO passport passes all check digit validations
    def test_validate_all_correct_uto(self):
        result = validate_mrz(self.UTO_LINE1, self.UTO_LINE2)
        self.assertTrue(result["overall_result"])
        for field in result["fields"]:
            self.assertTrue(field["match"], f"{field['field_name']} failed")

    # Test that a valid USA passport passes all check digit validations
    def test_validate_all_correct_usa(self):
        result = validate_mrz(self.USA_LINE1, self.USA_LINE2)
        self.assertTrue(result["overall_result"])
        for field in result["fields"]:
            self.assertTrue(field["match"], f"{field['field_name']} failed")

    # Test that tampering the passport check digit (pos 10) is detected
    def test_validate_wrong_passport_check(self):
        tampered = self.UTO_LINE2[:9] + "0" + self.UTO_LINE2[10:]
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        passport_field = result["fields"][0]
        self.assertEqual(passport_field["field_name"], "passport_number")
        self.assertFalse(passport_field["match"])

    # Test that tampering the birth date check digit (pos 20) is detected
    def test_validate_wrong_birth_check(self):
        tampered = self.UTO_LINE2[:19] + "0" + self.UTO_LINE2[20:]
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        birth_field = result["fields"][1]
        self.assertEqual(birth_field["field_name"], "birth_date")
        self.assertFalse(birth_field["match"])

    # Test that tampering the expiration check digit (pos 28) is detected
    def test_validate_wrong_expiration_check(self):
        tampered = self.UTO_LINE2[:27] + "0" + self.UTO_LINE2[28:]
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        exp_field = result["fields"][2]
        self.assertEqual(exp_field["field_name"], "expiration_date")
        self.assertFalse(exp_field["match"])

    # Test that tampering the personal number check digit (pos 43) is detected
    def test_validate_wrong_personal_check(self):
        tampered = self.UTO_LINE2[:42] + "0" + self.UTO_LINE2[43:]
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        pn_field = result["fields"][3]
        self.assertEqual(pn_field["field_name"], "personal_number")
        self.assertFalse(pn_field["match"])

    # Test that tampering the overall check digit (pos 44) is detected
    def test_validate_wrong_overall_check(self):
        tampered = self.UTO_LINE2[:43] + "9"
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        overall_field = result["fields"][4]
        self.assertEqual(overall_field["field_name"], "overall")
        self.assertFalse(overall_field["match"])

    # Test that tampering all check digits reports all mismatches (no short-circuit)
    def test_validate_all_wrong(self):
        tampered = (
            self.UTO_LINE2[:9] + "0"
            + self.UTO_LINE2[10:19] + "0"
            + self.UTO_LINE2[20:27] + "0"
            + self.UTO_LINE2[28:42] + "0" + "9"
        )
        self.assertEqual(len(tampered), 44)
        result = validate_mrz(self.UTO_LINE1, tampered)
        self.assertFalse(result["overall_result"])
        # All 5 fields should be reported as mismatches
        mismatches = [f for f in result["fields"] if not f["match"]]
        self.assertEqual(len(mismatches), 5)

    # Test that the original ICAO reference passport fails Fletcher-16 validation
    def test_validate_icao_reference_fails(self):
        icao_line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<<1"
        result = validate_mrz(self.UTO_LINE1, icao_line2)
        self.assertFalse(result["overall_result"])

    # Test that the response dict has the correct structure with all 5 field entries
    def test_validate_returns_all_fields(self):
        result = validate_mrz(self.UTO_LINE1, self.UTO_LINE2)
        self.assertIn("overall_result", result)
        self.assertIn("fields", result)
        self.assertEqual(len(result["fields"]), 5)
        expected_names = [
            "passport_number", "birth_date", "expiration_date",
            "personal_number", "overall",
        ]
        actual_names = [f["field_name"] for f in result["fields"]]
        self.assertEqual(actual_names, expected_names)
        # Each field entry must have expected, actual, and match keys
        for field in result["fields"]:
            self.assertIn("expected", field)
            self.assertIn("actual", field)
            self.assertIn("match", field)


class TestRoundTrip(unittest.TestCase):
    """Tests verifying encode->decode and encode->validate round-trips."""

    # Test that encoding fields then decoding the result recovers the original data
    def test_encode_then_decode_uto(self):
        fields = {
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
        line1, line2 = encode_mrz(fields)
        decoded = decode_mrz(line1, line2)
        self.assertEqual(decoded["document_type"], "P")
        self.assertEqual(decoded["surname"], "ERIKSSON")
        self.assertEqual(decoded["given_names"], "ANNA MARIA")
        self.assertEqual(decoded["passport_number"], "L898902C3")
        self.assertEqual(decoded["birth_date"], "740812")
        self.assertEqual(decoded["sex"], "F")
        self.assertEqual(decoded["expiration_date"], "120415")
        self.assertEqual(decoded["personal_number"], "ZE184226B")

    # Test encode->decode round-trip for a USA passport
    def test_encode_then_decode_usa(self):
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
        decoded = decode_mrz(line1, line2)
        self.assertEqual(decoded["surname"], "SMITH")
        self.assertEqual(decoded["given_names"], "JOHN")
        self.assertEqual(decoded["country_code"], "USA")

    # Test that encoding then validating always passes all check digits
    def test_encode_then_validate_passes(self):
        fields = {
            "document_type": "P",
            "issuing_country": "GBR",
            "surname": "JONES",
            "given_names": "ELIZABETH MARY",
            "passport_number": "CD9876543",
            "country_code": "GBR",
            "birth_date": "880515",
            "sex": "F",
            "expiration_date": "280515",
            "personal_number": "12345",
        }
        line1, line2 = encode_mrz(fields)
        result = validate_mrz(line1, line2)
        self.assertTrue(result["overall_result"])
        for field in result["fields"]:
            self.assertTrue(field["match"], f"{field['field_name']} failed")

    # Test decode->encode round-trip reproduces the original MRZ lines
    def test_decode_then_encode_roundtrip(self):
        orig_line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        orig_line2 = "L898902C34UTO7408122F1204153ZE184226B<<<<<70"
        decoded = decode_mrz(orig_line1, orig_line2)
        # Build fields dict from decoded output
        fields = {
            "document_type": decoded["document_type"],
            "issuing_country": decoded["issuing_country"],
            "surname": decoded["surname"],
            "given_names": decoded["given_names"],
            "passport_number": decoded["passport_number"],
            "country_code": decoded["country_code"],
            "birth_date": decoded["birth_date"],
            "sex": decoded["sex"],
            "expiration_date": decoded["expiration_date"],
            "personal_number": decoded["personal_number"],
        }
        line1, line2 = encode_mrz(fields)
        self.assertEqual(line1, orig_line1)
        self.assertEqual(line2, orig_line2)


if __name__ == "__main__":
    unittest.main()
