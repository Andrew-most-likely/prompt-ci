import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TestCase:
    name: str
    prompt: Optional[str] = None
    prompt_file: Optional[str] = None
    input: Optional[str] = None
    input_file: Optional[str] = None
    variables: dict = field(default_factory=dict)
    threshold: Optional[float] = None  # overrides global


@dataclass
class Config:
    provider: str = "anthropic"
    model: str = "claude-haiku-4-5-20251001"
    threshold: float = 0.80
    golden_dir: str = ".golden"
    tests: list[TestCase] = field(default_factory=list)


def load_config(path: str = "prompt-ci.yaml") -> Config:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {path}\nRun `prompt-ci init` to create one.")

    with open(p) as f:
        raw = yaml.safe_load(f)

    tests = []
    for t in raw.get("tests", []):
        tests.append(TestCase(**t))

    return Config(
        provider=raw.get("provider", "anthropic"),
        model=raw.get("model", "claude-haiku-4-5-20251001"),
        threshold=raw.get("threshold", 0.80),
        golden_dir=raw.get("golden_dir", ".golden"),
        tests=tests,
    )
