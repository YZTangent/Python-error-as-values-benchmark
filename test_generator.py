"""
Generate 1000 test cases for datetime parsing benchmark.
200 valid cases, 800 error cases with various failure modes.
"""
import json
import random
from typing import List, Dict, Any


def generate_test_cases() -> List[Dict[str, Any]]:
    """Generate 1000 test cases: 200 valid, 800 with errors."""
    test_cases = []

    # 200 valid cases
    valid_datetimes = [
        "2024-01-15 10:30:45",
        "2023-12-31 23:59:59",
        "2024-06-15 14:22:33",
        "2024-03-10 08:15:00",
        "2024-09-20 17:45:12",
        "2024-11-05 12:00:00",
        "2024-02-29 09:30:15",  # leap year
        "2024-07-04 16:20:55",
        "2024-05-01 11:11:11",
        "2024-08-18 19:45:30",
    ]

    for i in range(200):
        dt = random.choice(valid_datetimes)
        test_cases.append({
            "id": i,
            "message": {
                "timestamp": dt,
                "user": f"user_{i}",
                "data": f"message content {i}"
            },
            "expected_valid": True
        })

    # 800 error cases distributed across different error types

    # 200 cases: Missing timestamp field
    for i in range(200, 400):
        test_cases.append({
            "id": i,
            "message": {
                "user": f"user_{i}",
                "data": f"message content {i}"
                # Missing timestamp
            },
            "expected_valid": False,
            "error_type": "missing_field"
        })

    # 200 cases: Invalid datetime format (malformed strings)
    invalid_formats = [
        "2024/01/15 10:30:45",  # wrong separator
        "15-01-2024 10:30:45",  # wrong order
        "2024-13-01 10:30:45",  # invalid month
        "2024-01-32 10:30:45",  # invalid day
        "2024-01-15 25:30:45",  # invalid hour
        "2024-01-15 10:70:45",  # invalid minute
        "2024-01-15 10:30:70",  # invalid second
        "not-a-datetime",
        "2024-01-15",  # missing time
        "10:30:45",  # missing date
        "2024-1-5 10:30:45",  # single digit month/day
        "24-01-15 10:30:45",  # 2-digit year
        "",  # empty string
        "2024-02-30 10:30:45",  # invalid date for month
        "abcd-ef-gh ij:kl:mn",
    ]

    for i in range(400, 600):
        dt = random.choice(invalid_formats)
        test_cases.append({
            "id": i,
            "message": {
                "timestamp": dt,
                "user": f"user_{i}",
                "data": f"message content {i}"
            },
            "expected_valid": False,
            "error_type": "invalid_format"
        })

    # 200 cases: Type errors (timestamp is not a string)
    invalid_types = [
        123456,
        12345.67,
        True,
        False,
        ["2024-01-15", "10:30:45"],
        {"date": "2024-01-15", "time": "10:30:45"},
        None,
    ]

    for i in range(600, 800):
        dt = random.choice(invalid_types)
        test_cases.append({
            "id": i,
            "message": {
                "timestamp": dt,
                "user": f"user_{i}",
                "data": f"message content {i}"
            },
            "expected_valid": False,
            "error_type": "type_error"
        })

    # 200 cases: Malformed message structure (not a dict, or None)
    for i in range(800, 1000):
        malformed = random.choice([
            None,
            "not a dict",
            123,
            ["list", "of", "items"],
            12.34,
        ])
        test_cases.append({
            "id": i,
            "message": malformed,
            "expected_valid": False,
            "error_type": "malformed_message"
        })

    # Shuffle to mix valid and invalid cases
    random.shuffle(test_cases)

    return test_cases


def save_test_cases(filename: str = "test_cases.json"):
    """Generate and save test cases to a JSON file."""
    test_cases = generate_test_cases()
    with open(filename, 'w') as f:
        json.dump(test_cases, f, indent=2)
    print(f"Generated {len(test_cases)} test cases and saved to {filename}")

    # Print statistics
    valid_count = sum(1 for tc in test_cases if tc.get("expected_valid", False))
    error_count = len(test_cases) - valid_count
    print(f"Valid cases: {valid_count}")
    print(f"Error cases: {error_count}")

    error_types = {}
    for tc in test_cases:
        if not tc.get("expected_valid", False):
            error_type = tc.get("error_type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1

    print("\nError distribution:")
    for error_type, count in sorted(error_types.items()):
        print(f"  {error_type}: {count}")


if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    save_test_cases()
