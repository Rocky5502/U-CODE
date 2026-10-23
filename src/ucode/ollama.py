"""Optional local Ollama adapter. Returns text; NEVER executes model outputs."""
import json
import urllib.parse
import urllib.request


def generate_local(prompt: str, model: str = "qwen2.5-coder:7b",
                   base_url: str = "http://127.0.0.1:11434",
                   temperature: float = 0.2, seed: int = 7,
                   timeout: int = 180) -> str:
    """Calls locally running Ollama /api/generate (opt-in).

    Set up a local Ollama model separately. Network requests are restricted to
    127.0.0.1/localhost to prevent accidental prompt transmission to remote hosts.
    """
    parsed = urllib.parse.urlsplit(base_url)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost"):
        raise ValueError("only local HTTP Ollama endpoints are allowed")
    if not 0 <= temperature <= 2:
        raise ValueError("temperature outside [0,2]")
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": temperature, "seed": seed},
    }).encode("utf-8")
    req = urllib.request.Request(base_url.rstrip("/") + "/api/generate",
                                 data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result = json.load(response)
    text = result.get("response")
    if not isinstance(text, str):
        raise ValueError("Ollama did not return text")
    return text
