import re
from pathlib import Path
from .config import Config, TestCase


def _resolve_text(text: str | None, file: str | None, variables: dict) -> str:
    if file:
        content = Path(file).read_text(encoding='utf-8')
    elif text:
        content = text
    else:
        return ""

    for k, v in variables.items():
        content = content.replace(f"{{{{{k}}}}}", str(v))
    return content.strip()


def build_prompt(test: TestCase) -> str:
    prompt = _resolve_text(test.prompt, test.prompt_file, test.variables)
    input_text = _resolve_text(test.input, test.input_file, test.variables)

    if input_text:
        if "{{input}}" in prompt:
            return prompt.replace("{{input}}", input_text)
        return f"{prompt}\n\n{input_text}"
    return prompt


def run_prompt(full_prompt: str, config: Config) -> str:
    if config.provider == "anthropic":
        return _run_anthropic(full_prompt, config.model)
    elif config.provider == "openai":
        return _run_openai(full_prompt, config.model)
    elif config.provider == "mock":
        return _run_mock(full_prompt)
    else:
        raise ValueError(f"Unknown provider: {config.provider}")


def _run_anthropic(prompt: str, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _run_mock(prompt: str) -> str:
    """Returns a deterministic fake response for local testing without an API key."""
    words = prompt.lower().split()
    if "bullet" in words or "list" in words:
        return "- First key point from the text\n- Second key point from the text\n- Third key point from the text"
    if "sentiment" in words:
        return "positive"
    if "summarize" in words or "summary" in words:
        return "This is a mock summary of the provided text for testing purposes."
    return f"Mock response to: {prompt[:60]}..."


def _run_openai(prompt: str, model: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
