"""
Unit test to verify the vector_query syntax fix.

This test verifies that the vector_query parameter is formatted correctly
according to Typesense 0.24.0 documentation.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

import unittest
from unittest.mock import MagicMock, patch


class TestVectorQuerySyntax(unittest.TestCase):
    """Test vector_query syntax fix in TypesenseIndexer.search()"""

    def test_vector_query_format(self):
        """Test that vector_query has k parameter INSIDE parentheses"""
        # Import the indexer module
        from indexer_typesense import TypesenseIndexer

        # Create indexer with mock client
        with patch('typesense.Client'):
            indexer = TypesenseIndexer()

            # Mock the multi_search.perform method
            indexer.client.multi_search = MagicMock()
            indexer.client.multi_search.perform = MagicMock(return_value={"results": []})

            # Call search with a sample vector
            sample_vector = [0.1, 0.2, 0.3, 0.4]
            indexer.search("test_collection", sample_vector, top=10)

            # Get the body that was passed to multi_search.perform
            call_args = indexer.client.multi_search.perform.call_args
            body = call_args[0][0]

            # Extract the vector_query
            vector_query = body["searches"][0]["vector_query"]

            # Verify the format: k should be INSIDE parentheses
            expected_vector_str = "[0.1,0.2,0.3,0.4]"
            expected_format = f"vector:({expected_vector_str}, k:10)"

            self.assertEqual(vector_query, expected_format,
                f"vector_query format is incorrect.\n"
                f"Expected: {expected_format}\n"
                f"Got: {vector_query}")

            # Additional checks
            self.assertIn(", k:", vector_query,
                "k parameter should be preceded by ', ' (comma and space)")
            self.assertTrue(vector_query.endswith(")"),
                "vector_query should end with closing parenthesis")
            self.assertNotIn("),k:", vector_query,
                "k parameter should NOT be outside parentheses")

    def test_incorrect_format_detection(self):
        """Demonstrate what the incorrect format looks like"""
        sample_vector = [0.1, 0.2, 0.3, 0.4]
        vector_str = "[" + ",".join(map(str, sample_vector)) + "]"

        # INCORRECT format (old code)
        incorrect_format = f"vector:({vector_str}),k:10"

        # CORRECT format (new code)
        correct_format = f"vector:({vector_str}, k:10)"

        # Verify they are different
        self.assertNotEqual(incorrect_format, correct_format)

        # The incorrect format has k outside parentheses
        self.assertIn("),k:", incorrect_format)
        self.assertNotIn("),k:", correct_format)

        print(f"\nINCORRECT (was): {incorrect_format}")
        print(f"CORRECT (now):   {correct_format}")


class TestVectorQueryWithDifferentVectors(unittest.TestCase):
    """Test vector_query with different vector sizes and values"""

    def setUp(self):
        """Set up mock indexer"""
        with patch('typesense.Client'):
            from indexer_typesense import TypesenseIndexer
            self.indexer = TypesenseIndexer()
            self.indexer.client.multi_search = MagicMock()
            self.indexer.client.multi_search.perform = MagicMock(return_value={"results": []})

    def _get_vector_query(self, vector, top):
        """Helper to get vector_query from search call"""
        self.indexer.search("test", vector, top=top)
        call_args = self.indexer.client.multi_search.perform.call_args
        return call_args[0][0]["searches"][0]["vector_query"]

    def test_high_dimensional_vector(self):
        """Test with 384-dimensional vector (like all-MiniLM-L6-v2)"""
        vector = [0.1] * 384
        query = self._get_vector_query(vector, top=10)

        # Should end with ", k:10)" inside parentheses
        self.assertTrue(query.endswith(", k:10)"))
        self.assertNotIn("),k:", query)

    def test_different_top_values(self):
        """Test with different k values"""
        vector = [0.5, 0.5]

        for top in [5, 10, 100]:
            query = self._get_vector_query(vector, top=top)
            self.assertTrue(query.endswith(f", k:{top})"),
                f"Expected to end with ', k:{top})' but got: {query}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
