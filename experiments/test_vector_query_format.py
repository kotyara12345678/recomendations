"""
Unit test for vector_query format.
Tests the fix without requiring the typesense module.
"""
import unittest
import re


def build_vector_query_old(query_vector, top=10):
    """OLD INCORRECT implementation"""
    vector_str = "[" + ",".join(map(str, query_vector)) + "]"
    return f"vector:({vector_str}),k:{top}"


def build_vector_query_new(query_vector, top=10):
    """NEW CORRECT implementation - k is INSIDE parentheses"""
    vector_str = "[" + ",".join(map(str, query_vector)) + "]"
    return f"vector:({vector_str}, k:{top})"


class TestVectorQueryFormat(unittest.TestCase):
    """Test vector_query format according to Typesense 0.24.0 docs"""

    def test_old_format_is_wrong(self):
        """Old format has k OUTSIDE parentheses - this is wrong"""
        vector = [0.1, 0.2, 0.3]
        result = build_vector_query_old(vector, top=10)

        # Old format: vector:([...]),k:10
        self.assertIn("),k:", result)
        self.assertTrue(result.endswith(",k:10"))

    def test_new_format_is_correct(self):
        """New format has k INSIDE parentheses - this is correct per docs"""
        vector = [0.1, 0.2, 0.3]
        result = build_vector_query_new(vector, top=10)

        # New format: vector:([...], k:10)
        self.assertIn(", k:", result)
        self.assertTrue(result.endswith(", k:10)"))
        self.assertNotIn("),k:", result)

    def test_formats_are_different(self):
        """Verify old and new formats are different"""
        vector = [0.5, 0.6, 0.7, 0.8]
        old = build_vector_query_old(vector, top=5)
        new = build_vector_query_new(vector, top=5)

        self.assertNotEqual(old, new)
        print(f"\nOLD (wrong): {old}")
        print(f"NEW (correct): {new}")

    def test_typesense_doc_format(self):
        """Test format matches Typesense 0.24.0 documentation example"""
        # From docs: "vec:([0.96826, 0.94, 0.39557, 0.306488], k:100)"
        vector = [0.96826, 0.94, 0.39557, 0.306488]
        result = build_vector_query_new(vector, top=100)

        # Expected format pattern: field:([...], k:N)
        pattern = r'^vector:\(\[[\d\.,]+\], k:\d+\)$'
        self.assertTrue(re.match(pattern, result),
            f"Format doesn't match Typesense docs pattern.\n"
            f"Expected pattern: field:([...], k:N)\n"
            f"Got: {result}")

    def test_high_dimension_vector(self):
        """Test with 384-dimensional vector (all-MiniLM-L6-v2 output)"""
        vector = [0.1] * 384
        result = build_vector_query_new(vector, top=10)

        # Should still end correctly
        self.assertTrue(result.endswith(", k:10)"))
        self.assertNotIn("),k:", result)

    def test_various_top_values(self):
        """Test with different k values"""
        vector = [0.5, 0.5]

        for top in [1, 5, 10, 50, 100, 200]:
            result = build_vector_query_new(vector, top=top)
            self.assertTrue(result.endswith(f", k:{top})"),
                f"For top={top}, expected ending ', k:{top})' but got: {result}")


class TestActualCodeFix(unittest.TestCase):
    """Verify the fix was applied correctly to indexer_typesense.py"""

    def test_code_fix_applied(self):
        """Read the file and verify the fix"""
        import os
        file_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'indexer_typesense.py')

        with open(file_path, 'r') as f:
            content = f.read()

        # The fix: k should be inside parentheses
        # Correct: f"vector:({vector_str}, k:{top})"
        # Wrong: f"vector:({vector_str}),k:{top}"

        # Should find the correct pattern
        self.assertIn('f"vector:({vector_str}, k:{top})"', content,
            "The fix should have k INSIDE the parentheses")

        # Should NOT find the incorrect pattern
        self.assertNotIn('f"vector:({vector_str}),k:{top}"', content,
            "The old incorrect format should not be present")

        print("\n✓ Fix verified in indexer_typesense.py")


if __name__ == "__main__":
    unittest.main(verbosity=2)
