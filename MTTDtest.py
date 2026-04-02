"""
Comprehensive unit tests for MRTD (Machine-Readable Travel Document) system.
Entry point — actual tests live in tests/ package.
"""

import unittest
from tests.test_calculate_check_digit import TestCalculateCheckDigit
from tests.test_scan_mrz import TestScanMRZ
from tests.test_query_database import TestQueryDatabase
from tests.test_decode_mrz import TestDecodeMRZ
from tests.test_encode_mrz import TestEncodeMRZ
from tests.test_validate_mrz import TestValidateMRZ
from tests.test_round_trip import TestRoundTrip
from tests.test_mutpy_additional import TestMutPyAdditional

if __name__ == "__main__":
    unittest.main()
