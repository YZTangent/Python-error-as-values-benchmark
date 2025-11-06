"""
Main benchmark runner with cProfile integration.
Profiles all 6 combinations and displays comprehensive results.
"""
import json
import cProfile
import pstats
import io
from typing import Dict, Any, List
import time
from datetime import datetime

import benchmark_exception
import benchmark_union
import benchmark_tuple


def load_test_cases(filename: str = "test_cases.json") -> List[Dict[str, Any]]:
    """Load test cases from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def profile_function(func, test_cases):
    """Profile a function using cProfile and return stats."""
    profiler = cProfile.Profile()

    # Profile the function
    profiler.enable()
    start_time = time.perf_counter()
    result = func(test_cases)
    end_time = time.perf_counter()
    profiler.disable()

    # Get stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.strip_dirs()
    ps.sort_stats('cumulative')

    return {
        'result': result,
        'total_time': end_time - start_time,
        'profiler': profiler,
        'stats': ps
    }


def extract_function_stats(stats: pstats.Stats, func_patterns: List[str]) -> Dict[str, Dict[str, float]]:
    """Extract timing information for specific functions from profiler stats."""
    function_times = {}

    for func_pattern in func_patterns:
        function_times[func_pattern] = {
            'ncalls': 0,
            'tottime': 0.0,
            'cumtime': 0.0,
            'percall_tot': 0.0,
            'percall_cum': 0.0
        }

    # Get the stats dictionary
    for func, (cc, nc, tt, ct, callers) in stats.stats.items():
        func_name = func[2]  # function name

        for pattern in func_patterns:
            if pattern in func_name:
                function_times[pattern]['ncalls'] = nc
                function_times[pattern]['tottime'] = tt
                function_times[pattern]['cumtime'] = ct
                function_times[pattern]['percall_tot'] = tt / \
                    nc if nc > 0 else 0
                function_times[pattern]['percall_cum'] = ct / \
                    nc if nc > 0 else 0
                break

    return function_times


def print_separator(char='=', length=100):
    """Print a separator line."""
    print(char * length)


def print_benchmark_result(name: str, profile_data: Dict[str, Any], func_patterns: List[str]):
    """Print detailed results for a single benchmark."""
    print_separator()
    print(f"BENCHMARK: {name}")
    print_separator()

    result = profile_data['result']
    total_time = profile_data['total_time']
    stats = profile_data['stats']

    print(f"\nTotal Time: {total_time:.6f} seconds")
    print(f"Success: {result['success']}")
    print(f"Failures: {result['failure']}")
    print(
        f"Average time per test case: {(total_time / 1000) * 1000000:.2f} µs")

    # Extract function-level stats
    function_stats = extract_function_stats(stats, func_patterns)

    print("\nFunction-level breakdown:")
    print(f"{'Function':<40} {'Calls':>10} {'TotTime':>12} {'PerCall':>12} {'CumTime':>12}")
    print('-' * 90)

    for func_name, data in function_stats.items():
        if data['ncalls'] > 0:
            print(f"{func_name:<40} {data['ncalls']:>10} "
                  f"{data['tottime']:>12.6f} {data['percall_tot']:>12.9f} "
                  f"{data['cumtime']:>12.6f}")

    print()


def save_results_json(results: Dict, benchmarks: List[Dict], filename: str):
    """Save benchmark results to JSON file."""
    timestamp = datetime.now().isoformat()

    output_data = {
        'timestamp': timestamp,
        'benchmarks': []
    }

    for benchmark in benchmarks:
        name = benchmark['name']
        profile_data = results[name]

        # Extract function stats
        function_stats = extract_function_stats(
            profile_data['stats'], benchmark['patterns'])

        bench_data = {
            'name': name,
            'total_time': profile_data['total_time'],
            'success': profile_data['result']['success'],
            'failures': profile_data['result']['failure'],
            'us_per_test': (profile_data['total_time'] / 1000) * 1000000,
            'function_stats': function_stats
        }
        output_data['benchmarks'].append(bench_data)

    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nResults saved to {filename}")


def save_results_text(results: Dict, benchmarks: List[Dict], filename: str):
    """Save benchmark results to text file."""
    with open(filename, 'w') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Benchmark Results - {timestamp}\n")
        f.write("=" * 100 + "\n\n")

        # Write detailed results
        for benchmark in benchmarks:
            name = benchmark['name']
            profile_data = results[name]
            result = profile_data['result']
            total_time = profile_data['total_time']

            f.write("=" * 100 + "\n")
            f.write(f"BENCHMARK: {name}\n")
            f.write("=" * 100 + "\n\n")

            f.write(f"Total Time: {total_time:.6f} seconds\n")
            f.write(f"Success: {result['success']}\n")
            f.write(f"Failures: {result['failure']}\n")
            f.write(
                f"Average time per test case: {(total_time / 1000) * 1000000:.2f} µs\n\n")

            # Extract function-level stats
            function_stats = extract_function_stats(
                profile_data['stats'], benchmark['patterns'])

            f.write("Function-level breakdown:\n")
            f.write(
                f"{'Function':<40} {'Calls':>10} {'TotTime':>12} {'PerCall':>12} {'CumTime':>12}\n")
            f.write('-' * 90 + "\n")

            for func_name, data in function_stats.items():
                if data['ncalls'] > 0:
                    f.write(f"{func_name:<40} {data['ncalls']:>10} "
                            f"{data['tottime']:>12.6f} {data['percall_tot']:>12.9f} "
                            f"{data['cumtime']:>12.6f}\n")

            f.write("\n")

        # Write comparison table
        f.write("=" * 100 + "\n")
        f.write("PERFORMANCE COMPARISON\n")
        f.write("=" * 100 + "\n\n")

        baseline_shallow = results['Exception Handling - Shallow Stack']['total_time']
        baseline_deep = results['Exception Handling - Deep Stack']['total_time']

        f.write(
            f"{'Implementation':<50} {'Stack':>10} {'Total Time':>15} {'µs/test':>12} {'Speedup':>10}\n")
        f.write('-' * 100 + "\n")

        comparison_data = [
            ('Exception Handling', 'Shallow',
             results['Exception Handling - Shallow Stack'], baseline_shallow),
            ('Exception Handling', 'Deep',
             results['Exception Handling - Deep Stack'], baseline_deep),
            ('Union (Result | Exception)', 'Shallow',
             results['Union Error (Result | Exception) - Shallow Stack'], baseline_shallow),
            ('Union (Result | Exception)', 'Deep',
             results['Union Error (Result | Exception) - Deep Stack'], baseline_deep),
            ('Tuple (Result, Error)', 'Shallow',
             results['Tuple Error (Result, Error) - Shallow Stack'], baseline_shallow),
            ('Tuple (Result, Error)', 'Deep',
             results['Tuple Error (Result, Error) - Deep Stack'], baseline_deep),
        ]

        for impl, stack, data, baseline in comparison_data:
            total_time = data['total_time']
            us_per_test = (total_time / 1000) * 1000000
            speedup = baseline / total_time
            speedup_str = f"{speedup:.2f}x"

            f.write(
                f"{impl:<50} {stack:>10} {total_time:>15.6f}s {us_per_test:>11.2f} {speedup_str:>10}\n")

        f.write("\n")

    print(f"Results saved to {filename}")


def run_all_benchmarks():
    """Run all 6 benchmark combinations and display results."""
    print("Loading test cases...")
    test_cases = load_test_cases()
    print(f"Loaded {len(test_cases)} test cases\n")

    benchmarks = [
        {
            'name': 'Exception Handling - Shallow Stack',
            'func': benchmark_exception.run_shallow_exc,
            'patterns': ['validate_format_shallow_exc', 'parse_datetime_shallow_exc',
                         'parse_message_shallow_exc']
        },
        {
            'name': 'Exception Handling - Deep Stack',
            'func': benchmark_exception.run_deep_exc,
            'patterns': ['validate_format_deep_exc', 'parse_datetime_deep_exc',
                         'parse_message_deep_exc', 'validate_message_deep_exc',
                         'process_batch_deep_exc']
        },
        {
            'name': 'Union Error (Result | Exception) - Shallow Stack',
            'func': benchmark_union.run_shallow_union,
            'patterns': ['validate_format_shallow_union', 'parse_datetime_shallow_union',
                         'parse_message_shallow_union']
        },
        {
            'name': 'Union Error (Result | Exception) - Deep Stack',
            'func': benchmark_union.run_deep_union,
            'patterns': ['validate_format_deep_union', 'parse_datetime_deep_union',
                         'parse_message_deep_union', 'validate_message_deep_union',
                         'process_batch_deep_union']
        },
        {
            'name': 'Tuple Error (Result, Error) - Shallow Stack',
            'func': benchmark_tuple.run_shallow_tuple,
            'patterns': ['validate_format_shallow_tuple', 'parse_datetime_shallow_tuple',
                         'parse_message_shallow_tuple']
        },
        {
            'name': 'Tuple Error (Result, Error) - Deep Stack',
            'func': benchmark_tuple.run_deep_tuple,
            'patterns': ['validate_format_deep_tuple', 'parse_datetime_deep_tuple',
                         'parse_message_deep_tuple', 'validate_message_deep_tuple',
                         'process_batch_deep_tuple']
        },
    ]

    results = {}

    for benchmark in benchmarks:
        print(f"\nRunning: {benchmark['name']}...")
        profile_data = profile_function(benchmark['func'], test_cases)
        results[benchmark['name']] = profile_data
        print(f"Completed in {profile_data['total_time']:.6f} seconds")

    # Print detailed results
    print("\n")
    print_separator('=', 100)
    print("DETAILED RESULTS")
    print_separator('=', 100)

    for benchmark in benchmarks:
        print_benchmark_result(
            benchmark['name'],
            results[benchmark['name']],
            benchmark['patterns']
        )

    # Print comparison table
    print_separator('=', 100)
    print("PERFORMANCE COMPARISON")
    print_separator('=', 100)
    print()

    print(f"{'Implementation':<50} {'Stack':>10} {'Total Time':>15} {'µs/test':>12} {'Speedup':>10}")
    print('-' * 100)

    baseline_shallow = results['Exception Handling - Shallow Stack']['total_time']
    baseline_deep = results['Exception Handling - Deep Stack']['total_time']

    comparison_data = [
        ('Exception Handling', 'Shallow',
         results['Exception Handling - Shallow Stack'], baseline_shallow),
        ('Exception Handling', 'Deep',
         results['Exception Handling - Deep Stack'], baseline_deep),
        ('Union (Result | Exception)', 'Shallow',
         results['Union Error (Result | Exception) - Shallow Stack'], baseline_shallow),
        ('Union (Result | Exception)', 'Deep',
         results['Union Error (Result | Exception) - Deep Stack'], baseline_deep),
        ('Tuple (Result, Error)', 'Shallow',
         results['Tuple Error (Result, Error) - Shallow Stack'], baseline_shallow),
        ('Tuple (Result, Error)', 'Deep',
         results['Tuple Error (Result, Error) - Deep Stack'], baseline_deep),
    ]

    for impl, stack, data, baseline in comparison_data:
        total_time = data['total_time']
        us_per_test = (total_time / 1000) * 1000000
        speedup = baseline / total_time
        speedup_str = f"{speedup:.2f}x"

        print(
            f"{impl:<50} {stack:>10} {total_time:>15.6f}s {us_per_test:>11.2f} {speedup_str:>10}")

    print()
    print_separator('=', 100)

    # Summary
    print("\nKEY FINDINGS:")
    print("-" * 100)

    exc_shallow_time = results['Exception Handling - Shallow Stack']['total_time']
    union_shallow_time = results['Union Error (Result | Exception) - Shallow Stack']['total_time']
    tuple_shallow_time = results['Tuple Error (Result, Error) - Shallow Stack']['total_time']

    exc_deep_time = results['Exception Handling - Deep Stack']['total_time']
    union_deep_time = results['Union Error (Result | Exception) - Deep Stack']['total_time']
    tuple_deep_time = results['Tuple Error (Result, Error) - Deep Stack']['total_time']

    print(f"\nShallow Stack (2-3 levels):")
    print(f"  Exception handling: {exc_shallow_time:.6f}s (baseline)")
    print(
        f"  Union error:        {union_shallow_time:.6f}s ({(union_shallow_time/exc_shallow_time):.2f}x)")
    print(
        f"  Tuple error:        {tuple_shallow_time:.6f}s ({(tuple_shallow_time/exc_shallow_time):.2f}x)")

    if union_shallow_time < exc_shallow_time:
        improvement = ((exc_shallow_time - union_shallow_time) /
                       exc_shallow_time) * 100
        print(f"  → Union is {improvement:.1f}% faster than exceptions")
    else:
        slowdown = ((union_shallow_time - exc_shallow_time) /
                    exc_shallow_time) * 100
        print(f"  → Union is {slowdown:.1f}% slower than exceptions")

    if tuple_shallow_time < exc_shallow_time:
        improvement = ((exc_shallow_time - tuple_shallow_time) /
                       exc_shallow_time) * 100
        print(f"  → Tuple is {improvement:.1f}% faster than exceptions")
    else:
        slowdown = ((tuple_shallow_time - exc_shallow_time) /
                    exc_shallow_time) * 100
        print(f"  → Tuple is {slowdown:.1f}% slower than exceptions")

    print(f"\nDeep Stack (4-5 levels):")
    print(f"  Exception handling: {exc_deep_time:.6f}s (baseline)")
    print(
        f"  Union error:        {union_deep_time:.6f}s ({(union_deep_time/exc_deep_time):.2f}x)")
    print(
        f"  Tuple error:        {tuple_deep_time:.6f}s ({(tuple_deep_time/exc_deep_time):.2f}x)")

    if union_deep_time < exc_deep_time:
        improvement = ((exc_deep_time - union_deep_time) / exc_deep_time) * 100
        print(f"  → Union is {improvement:.1f}% faster than exceptions")
    else:
        slowdown = ((union_deep_time - exc_deep_time) / exc_deep_time) * 100
        print(f"  → Union is {slowdown:.1f}% slower than exceptions")

    if tuple_deep_time < exc_deep_time:
        improvement = ((exc_deep_time - tuple_deep_time) / exc_deep_time) * 100
        print(f"  → Tuple is {improvement:.1f}% faster than exceptions")
    else:
        slowdown = ((tuple_deep_time - exc_deep_time) / exc_deep_time) * 100
        print(f"  → Tuple is {slowdown:.1f}% slower than exceptions")

    print()

    # Save results to files
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_results_json(results, benchmarks,
                      f"benchmark_results_{timestamp_str}.json")
    save_results_text(results, benchmarks,
                      f"benchmark_results_{timestamp_str}.txt")


if __name__ == "__main__":
    run_all_benchmarks()
