# Contributing to prompt-drift

Thanks for your interest. This is a small project and contributions are welcome.

## Setup

```bash
git clone https://github.com/Andrew-most-likely/prompt-ci.git
cd prompt-ci
pip install -e ".[openai]"
```

## Running tests without an API key

The `mock` provider lets you run everything locally with no API key:

```bash
prompt-drift record --config test-mock.yaml
prompt-drift check --config test-mock.yaml
```

## Making changes

1. Fork the repo and create a branch from `master`
2. Make your change
3. Test with `provider: mock` at minimum
4. Open a PR — fill out the template

## What is in scope

- New provider support (Gemini, Mistral, etc.)
- Better similarity scoring methods
- CI integration improvements (GitLab CI, Bitbucket Pipelines)
- Bug fixes

## What is out of scope

- A web UI or dashboard
- Storing results in a database
- Running tests in parallel (for now — API rate limits make this tricky)

## Code style

Plain Python. No formatter enforced yet. Keep it readable.

## Reporting bugs

Use the [bug report template](https://github.com/Andrew-most-likely/prompt-ci/issues/new?template=bug_report.yml).
