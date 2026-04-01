import unittest
from MRTD import decode_mrz


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
