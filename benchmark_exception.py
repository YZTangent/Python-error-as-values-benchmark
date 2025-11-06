"""
Traditional exception handling implementation.
Raises exceptions and catches them at the top level.
Only the lowest level (validate_format) raises errors.
"""
from datetime import datetime
from typing import Any


# =============================================================================
# SHALLOW STACK (2-3 levels)
# =============================================================================

def validate_format_shallow_exc(datetime_str: str) -> datetime:
    """Level 3: ONLY level that raises errors - validates and parses datetime."""
    # This is the only function that can raise errors
    if not isinstance(datetime_str, str):
        raise TypeError(f"Expected string, got {type(datetime_str).__name__}")

    if not datetime_str:
        raise ValueError("Empty datetime string")

    # Attempt to parse - this will raise ValueError if invalid
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return dt
    except ValueError as e:
        raise ValueError(f"Failed to parse datetime: {e}")


def parse_datetime_shallow_exc(timestamp_str: str) -> datetime:
    """Level 2: Non-trivial text processing, no errors raised."""
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

    # Call next level - may raise exception
    return validate_format_shallow_exc(rejoined)


def parse_message_shallow_exc(message: Any) -> datetime:
    """Level 1: Extract timestamp with text processing, no errors raised."""
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
    cleaned = timestamp_str.strip().replace(
        '\t', ' ').replace('\n', ' ').replace('\r', ' ')

    # Replace multiple spaces with single space
    cleaned = ' '.join(cleaned.split())

    # Remove any surrounding quotes that might exist
    cleaned = cleaned.strip('"').strip("'")

    # Call next level - may raise exception
    return parse_datetime_shallow_exc(cleaned)


# =============================================================================
# DEEP STACK (4-5 levels)
# =============================================================================

def validate_format_deep_exc(datetime_str: str) -> datetime:
    """Level 5: ONLY level that raises errors - validates and parses datetime."""
    # This is the only function that can raise errors
    if not isinstance(datetime_str, str):
        raise TypeError(f"Expected string, got {type(datetime_str).__name__}")

    if not datetime_str:
        raise ValueError("Empty datetime string")

    # Attempt to parse - this will raise ValueError if invalid
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return dt
    except ValueError as e:
        raise ValueError(f"Failed to parse datetime: {e}")


def parse_datetime_deep_exc(timestamp_str: str) -> datetime:
    """Level 4: Non-trivial text processing, no errors raised."""
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

    # Call next level - may raise exception
    return validate_format_deep_exc(rejoined)


def parse_message_deep_exc(message: Any) -> datetime:
    """Level 3: Extract timestamp field, no errors raised."""
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
    cleaned = normalized.replace('\t', ' ').replace(
        '\n', ' ').replace('\r', ' ')

    # Call next level - may raise exception
    return parse_datetime_deep_exc(cleaned)


def validate_message_deep_exc(message: Any) -> datetime:
    """Level 2: Message field extraction and processing, no errors raised."""
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

    # Call next level with original message - may raise exception
    return parse_message_deep_exc(msg_dict)


def process_batch_deep_exc(message: Any) -> datetime:
    """Level 1: Top-level normalization, no errors raised."""
    # Convert message to string and back to normalize
    msg_str = str(message)

    # Do some string operations (non-trivial processing)
    processed = msg_str.strip().replace('  ', ' ')

    # Character counting (non-trivial operation)
    char_count = len(processed)

    # String manipulation
    normalized = processed.lower().upper().lower()

    # Call next level with original message - may raise exception
    return validate_message_deep_exc(message)


# =============================================================================
# ENTRY POINTS
# =============================================================================

def run_shallow_exc(test_cases):
    """Run shallow stack with exception handling."""
    results = {"success": 0, "failure": 0, "errors": []}

    for test_case in test_cases:
        try:
            message = test_case["message"]
            result = parse_message_shallow_exc(message)
            results["success"] += 1
        except Exception as e:
            results["failure"] += 1
            results["errors"].append(type(e).__name__)

    return results


def run_deep_exc(test_cases):
    """Run deep stack with exception handling."""
    results = {"success": 0, "failure": 0, "errors": []}

    for test_case in test_cases:
        try:
            message = test_case["message"]
            result = process_batch_deep_exc(message)
            results["success"] += 1
        except Exception as e:
            results["failure"] += 1
            results["errors"].append(type(e).__name__)

    return results
