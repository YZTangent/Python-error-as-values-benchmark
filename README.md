# ERV-Bench: Error As Value Benchmarks in Python

A comprehensive performance comparison of three error handling approaches in Python:
- **Traditional Exceptions** (`try`/`except`)
- **Union Types** (`Result | Exception`)
- **Tuple Returns** (`(Result | None, Exception | None)`)

## But why

Because hidden control flow is cringe and it's not like we need language level support to do error as values; so why not?

The question I wanted to answer was: does handling error as values in python, being helpful as it is for understanding and readability, have a negative impact on performance? Basically is ERV a tradeoff or just strictly a difference in style?

Let's be real, if performance is absolutely critical, you won't be using python; but that doesn't mean we shouldn't at least consider the performance impact of our design choices, which leads me to this little experiment here

Addendum: Owing to writing too much Go recently I was only considering testing ERV in Go style ([test 2](#3-union-types-type-safe)) only, but [this article by Aaron](https://www.inngest.com/blog/python-errors-as-values) on the topic also made me consider using a union type as well, reminiscent of how Rust does things.

## Error Handling Approaches

### 1. Exception Handling (Traditional)
```python
try:
    result = parse_message(message)
except ValueError as e:
    # handle error
```

### 2. Tuple Returns (Go-Style)
```python
result, error = parse_message(message)
if error:
    # handle error
else:
    # use result
```

### 3. Union Types (Type-Safe)
```python
result = parse_message(message)
if isinstance(result, Exception):
    # handle error
else:
    # use result

```
## Benchmark Results

Results from 1,000 test cases per scenario (213 successes, 787 failures):

### Performance Comparison

| Implementation              | Stack   | Total Time | μs/test | Speedup |
|-----------------------------|---------|------------|---------|---------|
| Exception Handling          | Shallow | 0.014078s  | 14.08   | 1.00x   |
| Exception Handling          | Deep    | 0.013265s  | 13.27   | 1.00x   |
| Union (Result \| Exception) | Shallow | 0.010351s  | 10.35   | 1.36x   |
| Union (Result \| Exception) | Deep    | 0.013037s  | 13.04   | 1.02x   |
| Tuple (Result, Error)       | Shallow | 0.009780s  | 9.78    | **1.44x**   |
| Tuple (Result, Error)       | Deep    | 0.012409s  | 12.41   | 1.07x   |

### Key Findings

#### Shallow Stack (2-3 levels)
- **Exception handling:** 14.08 μs (baseline)
- **Union error:** 10.35 μs (26.5% faster)
- **Tuple error:** 9.78 μs (30.5% faster) ✓

The tuple approach provides the best performance in shallow call stacks, with union types close behind. Both significantly outperform traditional exception handling.

#### Deep Stack (4-5 levels)
- **Exception handling:** 13.27 μs (baseline)
- **Union error:** 13.04 μs (1.7% faster)
- **Tuple error:** 12.41 μs (6.5% faster)

In deeper call stacks, the performance gap narrows considerably. All three approaches converge to similar performance levels, with tuples maintaining a slight edge.

## Thoughts

### When to Use Each Approach

**Tuple Returns** (`(Result, Error)`)
- No hidden control flow (caused by raised exceptions)
- Better performance than `try/catch`, especially for shallow call stacks
- Simple error handling needs
- Go-style error handling preference
- Ideal for recoverable conditions arising from some expected errors (e.g. malformed user input)
- Easier to propagate error up the stack in a predictable way for logging too

**Union Types** (`Result | Exception`)
- Same benefits as above, but with modern Python type-safe approach
- Works well with type checkers (mypy, pyright)
- Clear type contracts

**Exception Handling** (Traditional)
- Idiomatic Python (ew)
- Should still be used when some fundamental assertions about the program state is well and truly cooked, and the program should stop execution right here and now
- For checked exceptions that is very well recoverable, this is not the way IMHO

### Some caveats
- Benchmarks measure **error-heavy workloads** (78.7% failure rate)
- Performance characteristics may differ with different error rates
- Actual performance depends on error complexity and stack depth
- These results are from a specific Python implementation (CPython 3.13), but this should not differ much or at all across versions that support union type annotations (Python 3.10+)

## Architecture

The benchmark tests two call stack depths:

**Shallow Stack:** 3 levels of function calls
```
parse_message → parse_datetime → validate_format
```

**Deep Stack:** 5 levels of function calls
```
process_batch → validate_message → parse_message → parse_datetime → validate_format
```

Each level performs realistic text processing operations (normalization, cleanup, formatting) before calling the next level. Only the deepest level (`validate_format`) can raise errors.

## Running

### Prerequisites
- Python 3.13+
- uv (recommended) or pip

### Installation
```bash
# Using uv
uv sync

# Using pip
pip install -e .
```

### Run Benchmarks
```bash
python run_benchmarks.py
```

Results will be saved to:
- `benchmark_results_YYYYMMDD_HHMMSS.json` - Structured JSON data
- `benchmark_results_YYYYMMDD_HHMMSS.txt` - Human-readable report

## Project Structure

```
erv-bench/
├── benchmark_exception.py    # Traditional exception handling
├── benchmark_union.py        # Union type error handling
├── benchmark_tuple.py        # Tuple return error handling
├── run_benchmarks.py         # Main benchmark runner
├── test_generator.py         # Test case generation
├── test_cases.json           # 1,000 test cases
└── README.md                 # This file
```

## License

This benchmark is provided as-is for fun and procrastination purposes. Not in any way academically rigorous lol
