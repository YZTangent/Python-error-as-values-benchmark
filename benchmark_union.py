"""
Error as value implementation using Union types.
Functions return: Result | Exception
Check errors with isinstance(result, Exception)
Only the lowest level (validate_format) returns errors.
"""
from datetime import datetime
from typing import Any


# =============================================================================
# SHALLOW STACK (2-3 levels)
# =============================================================================

def validate_format_shallow_union(datetime_str: str) -> datetime | Exception:
    """Level 3: ONLY level that returns errors - validates and parses datetime."""
    # This is the only function that can return errors
    if not isinstance(datetime_str, str):
        return TypeError(f"Expected string, got {type(datetime_str).__name__}")

    if not datetime_str:
        return ValueError("Empty datetime string")

    # Attempt to parse - this will return ValueError if invalid
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return dt
    except ValueError as e:
        return ValueError(f"Failed to parse datetime: {e}")


def parse_datetime_shallow_union(timestamp_str: str) -> datetime | Exception:
    """Level 2: Non-trivial text processing, propagates errors."""
    # Normalize whitespace - strip leading/trailing, collapse multiple spaces
    normalized = ' '.join(timestamp_str.split())

    # Remove common punctuation that might appear
    cleaned = normalized.replace(',', '').replace(';', '').replace('|', ' ')

    # Additional normalization - ensure single spaces
    cleaned = ' '.join(cleaned.split())

    # Convert to title case and back to test string operations
    temp = cleaned.title().lower()

    # Split and rejoin to ensure format
    parts = temp.split()
    rejoined = ' '.join(parts)

    # Call next level - may return exception
    result = validate_format_shallow_union(rejoined)
    if isinstance(result, Exception):
        return result

    return result


def parse_message_shallow_union(message: Any) -> datetime | Exception:
    """Level 1: Extract timestamp with text processing, propagates errors."""
    # Convert message to string representation if needed
    msg_str = str(message) if not isinstance(message, dict) else ""

    # If it's a dict, extract timestamp (or use empty string)
    if isinstance(message, dict):
        timestamp = message.get("timestamp", "")
    else:
        # Try to extract something resembling a timestamp from string representation
        timestamp = ""

    # Convert timestamp to string with normalization
    timestamp_str = str(timestamp) if timestamp is not None else ""

    # Clean up the string - remove extra whitespace, tabs, newlines
    cleaned = timestamp_str.strip().replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')

    # Replace multiple spaces with single space
    cleaned = ' '.join(cleaned.split())

    # Remove any surrounding quotes that might exist
    cleaned = cleaned.strip('"').strip("'")

    # Call next level - may return exception
    result = parse_datetime_shallow_union(cleaned)
    if isinstance(result, Exception):
        return result

    return result


# =============================================================================
# DEEP STACK (4-5 levels)
# =============================================================================

def validate_format_deep_union(datetime_str: str) -> datetime | Exception:
    """Level 5: ONLY level that returns errors - validates and parses datetime."""
    # This is the only function that can return errors
    if not isinstance(datetime_str, str):
        return TypeError(f"Expected string, got {type(datetime_str).__name__}")

    if not datetime_str:
        return ValueError("Empty datetime string")

    # Attempt to parse - this will return ValueError if invalid
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return dt
    except ValueError as e:
        return ValueError(f"Failed to parse datetime: {e}")


def parse_datetime_deep_union(timestamp_str: str) -> datetime | Exception:
    """Level 4: Non-trivial text processing, propagates errors."""
    # Normalize whitespace
    normalized = ' '.join(timestamp_str.split())

    # Remove common punctuation
    cleaned = normalized.replace(',', '').replace(';', '').replace('|', ' ')

    # Ensure single spaces
    cleaned = ' '.join(cleaned.split())

    # Case transformations
    temp = cleaned.title().lower()

    # Split and rejoin
    parts = temp.split()
    rejoined = ' '.join(parts)

    # Call next level - may return exception
    result = validate_format_deep_union(rejoined)
    if isinstance(result, Exception):
        return result

    return result


def parse_message_deep_union(message: Any) -> datetime | Exception:
    """Level 3: Extract timestamp field, propagates errors."""
    # Extract timestamp field if dict, otherwise empty string
    if isinstance(message, dict):
        timestamp = message.get("timestamp", "")
    else:
        timestamp = ""

    # Convert to string
    timestamp_str = str(timestamp) if timestamp is not None else ""

    # Normalize the extracted string
    normalized = timestamp_str.strip()

    # Remove control characters
    cleaned = normalized.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')

    # Call next level - may return exception
    result = parse_datetime_deep_union(cleaned)
    if isinstance(result, Exception):
        return result

    return result


def validate_message_deep_union(message: Any) -> datetime | Exception:
    """Level 2: Message field extraction and processing, propagates errors."""
    # Convert to dict representation if possible
    if isinstance(message, dict):
        msg_dict = message
    else:
        # Create empty dict for non-dict types
        msg_dict = {}

    # Extract all string values and concatenate (non-trivial processing)
    str_values = [str(v) for v in msg_dict.values() if v is not None]
    concatenated = ' '.join(str_values)

    # Do some processing on concatenated string
    processed = concatenated.strip().lower().upper().lower()

    # Call next level with original message - may return exception
    result = parse_message_deep_union(msg_dict)
    if isinstance(result, Exception):
        return result

    return result


def process_batch_deep_union(message: Any) -> datetime | Exception:
    """Level 1: Top-level normalization, propagates errors."""
    # Convert message to string and back to normalize
    msg_str = str(message)

    # Do some string operations (non-trivial processing)
    processed = msg_str.strip().replace('  ', ' ')

    # Character counting (non-trivial operation)
    char_count = len(processed)

    # String manipulation
    normalized = processed.lower().upper().lower()

    # Call next level with original message - may return exception
    result = validate_message_deep_union(message)
    if isinstance(result, Exception):
        return result

    return result


# =============================================================================
# ENTRY POINTS
# =============================================================================

def run_shallow_union(test_cases):
    """Run shallow stack with union error handling."""
    results = {"success": 0, "failure": 0, "errors": []}

    for test_case in test_cases:
        message = test_case["message"]
        result = parse_message_shallow_union(message)

        if isinstance(result, Exception):
            results["failure"] += 1
            results["errors"].append(type(result).__name__)
        else:
            results["success"] += 1

    return results


def run_deep_union(test_cases):
    """Run deep stack with union error handling."""
    results = {"success": 0, "failure": 0, "errors": []}

    for test_case in test_cases:
        message = test_case["message"]
        result = process_batch_deep_union(message)

        if isinstance(result, Exception):
            results["failure"] += 1
            results["errors"].append(type(result).__name__)
        else:
            results["success"] += 1

    return results
