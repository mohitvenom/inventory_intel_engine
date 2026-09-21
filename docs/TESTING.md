# Testing Strategy

## Unit Tests

Unit tests are located in `tests/`. They test the pure functions and logic boundaries.
To run unit tests and check coverage:
```bash
venv\Scripts\python.exe -m pytest --cov=backend tests/
```

### Coverage
Currently we focus coverage on:
- Graph logic bounds (e.g. price drops exactly at threshold, handling no history, handling out-of-stock transitions).
- HTTP rate limiting logic.

## Evals

Evals are located in `tests/evals/`.
They test the LLM components. Unlike simple deterministic tests, these call out to OpenAI (`gpt-4o-mini`) using synthetic trace data to verify the quality and correctness of the generated run summaries.

To run evals:
```bash
venv\Scripts\python.exe -m pytest tests/evals/test_summary_evals.py
```

## Running

1. Ensure `.env` is fully populated.
2. Run standard pytest. Evals will make real network calls, while standard unit tests use mocks (like `MockTool` inside `test_graph_logic.py`).
