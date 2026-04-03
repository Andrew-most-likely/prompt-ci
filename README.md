# prompt-drift

[![CI](https://github.com/Andrew-most-likely/prompt-ci/actions/workflows/self-test.yml/badge.svg)](https://github.com/Andrew-most-likely/prompt-ci/actions/workflows/self-test.yml)
[![PyPI](https://img.shields.io/pypi/v/prompt-drift)](https://pypi.org/project/prompt-drift/)
[![Python](https://img.shields.io/pypi/pyversions/prompt-drift)](https://pypi.org/project/prompt-drift/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Unit tests for AI prompts.** Catch regressions before your users do.

When you tweak a prompt, swap models, or upgrade an API version - how do you know your AI still behaves correctly? `prompt-drift` records your expected outputs as golden files and checks every future run against them using semantic similarity.

```bash
pip install prompt-drift
prompt-drift init
prompt-drift record   # capture golden outputs
prompt-drift check    # verify nothing regressed (run this in CI)
```

---

## The problem

You ship an AI feature. It works great. Then you:
- Tweak the prompt slightly
- Switch from GPT-4 to Claude
- Upgrade to a new model version

Suddenly outputs drift - wrong format, different tone, missing information. **You find out when a user complains.**

`prompt-drift` solves this the same way unit tests solve code regressions.

---

## Quickstart

### 1. Install

```bash
pip install prompt-drift
# For OpenAI support:
pip install "prompt-drift[openai]"
```

### 2. Init a config

```bash
prompt-drift init
```

Edit the generated `prompt-ci.yaml`:

```yaml
provider: anthropic   # or openai
model: claude-haiku-4-5-20251001
threshold: 0.80       # fail if semantic similarity drops below this

tests:
  - name: summarize_concise
    prompt: "Summarize in exactly 3 bullet points: {{input}}"
    input: "Your input text here..."
    threshold: 0.85

  - name: sentiment_check
    prompt: "Reply with one word - positive, negative, or neutral:"
    input: "I love this product!"
    threshold: 0.95
```

### 3. Record golden outputs

```bash
export ANTHROPIC_API_KEY=sk-...
prompt-drift record
```

This saves outputs to `.golden/`. **Commit this directory** - it's your source of truth.

### 4. Check for regressions

```bash
prompt-drift check
```

```
Checking prompts (2 tests)

  PASS summarize_concise  score=0.91  threshold=0.85  (llm-judge)
  FAIL sentiment_check    score=0.60  threshold=0.95  (llm-judge)
    Expected: positive
    Actual:   The sentiment of this text is positive and enthusiastic.

1/2 tests failed.
```

Exit code `1` on any failure - drop straight into CI.

### 5. Add to GitHub Actions

```yaml
- name: Run prompt regression tests
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: prompt-drift check
```

---

## Commands

| Command | Description |
|---|---|
| `prompt-drift init` | Create starter `prompt-ci.yaml` |
| `prompt-drift record` | Run all prompts, save golden outputs |
| `prompt-drift check` | Compare current outputs to golden, exit 1 on fail |
| `prompt-drift show <name>` | Print the stored golden output for a test |

### Options

```bash
prompt-drift check --verbose        # show expected vs actual for all tests
prompt-drift check --config path/to/prompt-ci.yaml   # custom config path
```

---

## How similarity scoring works

By default, `prompt-drift` uses an **LLM-as-judge** to score semantic similarity between your golden output and the actual output. The judge rates on a 0.0–1.0 scale considering meaning, structure, and completeness.

If the LLM judge fails (network error, etc.), it falls back to **token overlap** (Jaccard similarity) as a safety net.

---

## Config reference

```yaml
provider: anthropic          # anthropic | openai
model: claude-haiku-4-5-20251001
threshold: 0.80              # global default, 0.0–1.0
golden_dir: .golden          # where golden files are stored

tests:
  - name: my_test            # unique identifier (used for filename)

    # Prompt: inline or from file
    prompt: "Your prompt with {{variables}}"
    prompt_file: prompts/my_prompt.txt

    # Input: inline or from file
    input: "Direct input text"
    input_file: inputs/my_input.txt

    # Variables for template substitution
    variables:
      tone: concise
      max_words: "100"

    threshold: 0.90          # optional per-test override
```

**Variable substitution:** Use `{{variable_name}}` in prompts and inputs. `{{input}}` in a prompt is automatically replaced with the input content.

---

## FAQ

**Does this cost money to run?**
Yes - it calls your LLM provider twice per test (once to get the output, once for the LLM judge). Use `claude-haiku` or `gpt-4o-mini` to minimize cost.

**Should I commit `.golden/`?**
Yes. Golden files are your locked expected behavior. Treat them like snapshots in a snapshot testing framework.

**What if I intentionally change a prompt?**
Re-run `prompt-drift record` after your change. The new output becomes the new golden file.

**Can I use it without a CI system?**
Absolutely - run `prompt-drift check` locally before any deploy.

---

## License

MIT
