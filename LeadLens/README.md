Functional requirements

A CLI command leadlens ask "<question>" sends the question to the model and prints the answer.
A --stream flag streams tokens to the terminal as they arrive. Without it, the full response prints at the end.
The system prompt lives in a separate versioned file (prompts/system_v1.md) and loads at startup, not hardcoded.
The model, temperature, top_p and max_tokens are configurable through flags and environment config, with sensible defaults.
A --json mode returns a structured answer validated with Pydantic, with these fields:
answer (string)
confidence (low/medium/high)
assumptions (list of strings)
needs_external_data (bool, set true when the model lacks the information to answer)
A --provider setting supports one native SDK (Anthropic or OpenAI). The provider code sits behind a small client interface, so a second provider can be added later without touching the rest of the app.
Multi-turn conversation inside a single session, with a configurable cap on context size. When the cap is reached, the oldest turns are trimmed.

Failure handling

Timeouts: every call has a configurable timeout. On timeout it retries with exponential backoff and jitter, up to N attempts (default 3), then fails with a clear error.
Rate limits: on a 429, the app honors the retry-after header if present and otherwise backs off. Retry limits are bounded, and the app never retries endlessly.
Transient server errors (5xx, connection resets) are retried. Client errors (400, 401, bad request) are not retried and are reported immediately.
Token-limit truncation: detect when generation stopped because it hit max_tokens. The app then either asks the model to continue or returns the partial answer marked truncated: true, depending on config.
Invalid JSON in --json mode: re-ask the model once, including the validation error in the prompt. If it fails again, return a structured error rather than crashing.
Inconsistent output: run the same prompt five times at temperature 0, measure how often the output format differs, and document the result.
Inputs that are empty, very long or non-text are rejected before any API call is made.

Configuration and security

All settings come from environment variables or a .env file through a Pydantic Settings class. The app fails fast at startup with a clear message if the API key is missing.
No secrets are hardcoded or logged. API keys are redacted from all log output.

Observability

Structured JSON logs record, for every request:
a request ID
the model and parameters
prompt and completion token counts
estimated cost
latency, including time to first token when streaming
retry count
stop reason
error type, if any
A --debug flag logs the full request and response payloads to a local file, so you can inspect exactly what happened on any call.
At the end of each session, the app prints a summary: total requests, total tokens, total cost and average latency.

Testing

Unit tests mock the SDK and cover:
a successful call
a timeout followed by successful retry
a 429 rate limit
a 5xx error
a non-retryable 400 error
truncation
invalid JSON followed by a successful re-ask
a missing API key
One optional integration test hits the real API. It is skipped unless an environment flag is set.
All tests run in GitHub Actions with no API key.

Non-functional requirements

Python 3.11+, type hints throughout, and mypy and ruff passing cleanly.
Retry and backoff overhead adds no more than 50 ms per call on the success path.
A single install command (uv sync or pip install -e .), and the app runs within 2 minutes of cloning.

Start project
source .venv/bin/activate