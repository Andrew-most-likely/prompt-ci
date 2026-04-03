"""
Semantic similarity via LLM-as-judge.
Falls back to token overlap if judge fails.
"""
import warnings

JUDGE_PROMPT = """You are a semantic similarity judge.

Compare these two AI outputs and rate how semantically equivalent they are.
Consider: meaning, structure, completeness, and key information preserved.

Expected output:
---
{expected}
---

Actual output:
---
{actual}
---

Return ONLY a decimal number between 0.0 and 1.0 where:
1.0 = identical meaning and structure
0.8 = same meaning, minor differences in wording/format
0.6 = mostly same, some missing or extra information
0.4 = partially related but notable divergence
0.0 = completely different

Number only, no explanation:"""


def score_similarity(expected: str, actual: str, provider: str, model: str) -> tuple[float, str]:
    """Returns (score, method_used)"""
    if provider == "mock":
        score = _token_overlap(expected, actual)
        return score, "token-overlap"
    try:
        score = _llm_judge(expected, actual, provider, model)
        return score, "llm-judge"
    except Exception as e:
        warnings.warn(f"LLM judge failed ({e}); falling back to token-overlap scoring.", stacklevel=2)
        score = _token_overlap(expected, actual)
        return score, "token-overlap"


def _llm_judge(expected: str, actual: str, provider: str, model: str) -> float:
    prompt = JUDGE_PROMPT.format(expected=expected, actual=actual)

    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI returned empty judge response.")
        raw = content.strip()
    else:
        raise ValueError(f"Unknown provider: {provider}")

    return float(raw)


def _token_overlap(a: str, b: str) -> float:
    """Simple Jaccard similarity on word tokens as fallback."""
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a and not tokens_b:
        return 1.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)
