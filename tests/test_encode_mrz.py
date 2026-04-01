import unittest
from MRTD import encode_mrz


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
