# Security

## API keys

prompt-drift reads API keys from environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`). It never stores, logs, or transmits them anywhere other than the provider API call.

## Golden files

Golden files (`.golden/*.json`) contain AI-generated text from your prompts. Do not commit golden files that contain sensitive information from your inputs.

## Reporting a vulnerability

Please do not open a public GitHub issue for security vulnerabilities. Email the maintainer directly via the email on the GitHub profile. You will get a response within 72 hours.
