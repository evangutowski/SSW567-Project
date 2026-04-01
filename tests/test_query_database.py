import unittest
from unittest.mock import patch
from MRTD import query_database


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
