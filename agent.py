"""Plain Anthropic Opus agent."""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    from correlation_zero import Agent, AgentQuery
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "sdk"))
    from correlation_zero import Agent, AgentQuery


AGENT_ID = "plain-anthropic-opus-agent"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-opus-4-7"
DEFAULT_MAX_TOKENS = 2048


def load_env_local() -> None:
    env_path = Path(__file__).resolve().parent / ".env.local"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def verified_ssl_context() -> ssl.SSLContext | None:
    try:
        import certifi
    except ImportError:
        return None
    return ssl.create_default_context(cafile=certifi.where())


def content_text(content: list[dict[str, Any]]) -> str:
    return "\n".join(
        block.get("text", "")
        for block in content
        if block.get("type") == "text" and block.get("text")
    ).strip()


class PlainAnthropicOpusAgent(Agent):
    AGENT_ID = AGENT_ID

    def __init__(self) -> None:
        load_env_local()
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)

    def freeform(self, query: AgentQuery) -> str:
        if not self.api_key:
            return "ANTHROPIC_API_KEY is not configured for this runtime."

        payload = self.build_payload(query)
        request = urllib.request.Request(
            ANTHROPIC_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
                "x-api-key": self.api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=60,
                context=verified_ssl_context(),
            ) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            return f"Anthropic API returned HTTP {exc.code}: {body}"
        except urllib.error.URLError as exc:
            return f"Anthropic API request failed: {exc.reason}"

        answer = content_text(result.get("content", []))
        return answer or "Anthropic API returned an empty text response."

    def build_payload(self, query: AgentQuery) -> dict[str, Any]:
        context = query.context or {}
        system_prompt = str(context.get("system") or "You are a helpful assistant.")
        model = str(context.get("model") or self.model)
        max_tokens = int(context.get("max_tokens") or DEFAULT_MAX_TOKENS)
        temperature = float(context.get("temperature") or 0.2)
        messages = context.get("messages")

        if not isinstance(messages, list) or not messages:
            messages = [{"role": "user", "content": query.prompt}]

        return {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": messages,
        }


def build_query_from_stdin() -> AgentQuery:
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        return AgentQuery(
            query_id="cli",
            prompt="Return a short response that proves the agent is working.",
        )

    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError:
        return AgentQuery(query_id="cli", prompt=raw_input)

    return AgentQuery(
        query_id=str(payload.get("query_id") or payload.get("id") or "cli"),
        prompt=str(payload.get("prompt") or payload.get("query") or raw_input),
        response_format=str(payload.get("response_format") or "freeform"),
        context=payload.get("context") if isinstance(payload.get("context"), dict) else {},
        metrics=payload.get("metrics") if isinstance(payload.get("metrics"), list) else [],
    )


def main() -> int:
    query = build_query_from_stdin()
    print(PlainAnthropicOpusAgent().freeform(query))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
