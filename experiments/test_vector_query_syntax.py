"""
Experiment script to verify the vector_query syntax issue in Typesense.

Problem identified:
- Current code produces: vector:([...]),k:10
- Correct syntax should be: vector:([...], k:10)

The k parameter must be INSIDE the parentheses, not outside.
"""

# Incorrect vector_query format (current implementation):
def build_vector_query_incorrect(query_vector, top=10):
    vector_str = "[" + ",".join(map(str, query_vector)) + "]"
    return f"vector:({vector_str}),k:{top}"


# Correct vector_query format (fix):
def build_vector_query_correct(query_vector, top=10):
    vector_str = "[" + ",".join(map(str, query_vector)) + "]"
    return f"vector:({vector_str}, k:{top})"


if __name__ == "__main__":
    # Example vector (short for demonstration)
    sample_vector = [0.96826, 0.94, 0.39557, 0.306488]

    print("=== Vector Query Syntax Comparison ===\n")

    incorrect = build_vector_query_incorrect(sample_vector, top=10)
    correct = build_vector_query_correct(sample_vector, top=10)

    print(f"INCORRECT (current code):\n  {incorrect}\n")
    print(f"CORRECT (Typesense docs):\n  {correct}\n")

    print("Key difference:")
    print("  - INCORRECT: k:{top} is OUTSIDE the parentheses")
    print("  - CORRECT: k:{top} is INSIDE the parentheses with a space after the vector")

    print("\n=== Reference from Typesense 0.24.0 docs ===")
    print('Expected format: "vec:([0.96826, 0.94, 0.39557, 0.306488], k:100)"')
