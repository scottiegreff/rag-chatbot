# Performance Testing Guide

## Automated Performance Testing Script

### Quick Start

Run the comprehensive performance test:

```bash
python3 tests/run_performance_test_simple.py
```

### What the Script Does

1. **Tests Docker CPU Environment** (current environment)
   - Simple generic query
   - RAG query with context
   - SQL database query
   - Long generation test

2. **Switches to M1 GPU Environment**
   - Runs the same 4 tests
   - Measures performance differences

3. **Generates Report**
   - Creates timestamped markdown file in `testing_summaries/`
   - Includes detailed metrics and comparisons
   - Provides recommendations

### Test Metrics Measured

- **First Token Latency:** Time to first response
- **Generation Time:** Time to complete response
- **Tokens/Second:** Generation speed
- **Total Time:** End-to-end request time
- **Response Quality:** Token count and content length

### Sample Output

The script generates reports like:
```
testing_summaries/performance_test_2025-07-09_12-22-56.md
```

### Report Contents

- **Test Configuration:** Environment details
- **Performance Results:** Detailed metrics for each test
- **Performance Comparison:** Side-by-side analysis
- **Key Findings:** Average performance improvements
- **Recommendations:** Usage guidance

### Usage Examples

```bash
# Run full test suite
python3 tests/run_performance_test_simple.py

# Check generated reports
ls -la testing_summaries/

# View latest report
cat testing_summaries/performance_test_*.md | tail -1
```

### Requirements

- Python 3.7+
- requests library
- Backend running on localhost:8000
- Environment switching scripts available

### Troubleshooting

- **Backend not ready:** Script waits up to 2 minutes for backend
- **Environment switch fails:** Check if Docker is running
- **Test timeout:** Increase timeout values in script if needed

### Customization

Edit `tests/run_performance_test_simple.py` to:
- Change test queries
- Modify timeout values
- Add new test types
- Customize report format 