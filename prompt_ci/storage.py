import json
from datetime import datetime, timezone
from pathlib import Path


def golden_path(golden_dir: str, test_name: str) -> Path:
    return Path(golden_dir) / f"{test_name}.json"


def save_golden(golden_dir: str, test_name: str, prompt: str, output: str, model: str, provider: str):
    Path(golden_dir).mkdir(parents=True, exist_ok=True)
    data = {
        "test_name": test_name,
        "provider": provider,
        "model": model,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "prompt_hash": _hash(prompt),
        "output": output,
    }
    path = golden_path(golden_dir, test_name)
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return path


def load_golden(golden_dir: str, test_name: str) -> dict | None:
    path = golden_path(golden_dir, test_name)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def _hash(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()[:12]
