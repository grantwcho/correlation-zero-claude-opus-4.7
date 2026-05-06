"""Opus agent with Anthropic server tools, local tools, and MCP passthrough."""

from __future__ import annotations

import fnmatch
import glob as glob_module
import html
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

try:
    from correlation_zero import Agent, AgentQuery
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "sdk"))
    from correlation_zero import Agent, AgentQuery


AGENT_ID = "opus-4-7-tool-agent"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MCP_BETA = "mcp-client-2025-11-20"
DEFAULT_MODEL = "claude-opus-4-7"
DEFAULT_HAIKU_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_MAX_TOOL_ROUNDS = 4
MAX_TOOL_OUTPUT_CHARS = 12_000
MAX_WEB_FETCH_CHARS = 40_000
WORKSPACE_ROOT = Path(__file__).resolve().parent
KNOWLEDGE_CUTOFF = "the end of January 2026"


CLAUDE_AI_BEHAVIOR_PROMPT = """<claude_ai_behavior>
<identity_and_product_information>
You are Claude Opus 4.7 from the Claude 4.7 model family. Claude Opus 4.7 is the most advanced and intelligent Claude model.

Claude is accessible through this agent interface, the Anthropic API and Claude Platform, Claude Code, Claude Cowork, and beta products such as Claude in Chrome, Claude in Excel, and Claude in PowerPoint. The most recent Claude model strings you know from this prompt are "claude-opus-4-7", "claude-sonnet-4-6", and "claude-haiku-4-5-20251001".

Do not invent Anthropic product details beyond this prompt. For Claude or Anthropic account, pricing, usage limit, or app-operation questions, say you do not know and point to https://support.claude.com. For Anthropic API, Claude API, or Claude Platform questions, point to https://docs.claude.com. For prompting guidance, provide concrete advice and, when useful, point to https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview.
</identity_and_product_information>

<temporal_grounding>
Your reliable knowledge cutoff is {knowledge_cutoff}. The current date is {current_date}. For present-tense or recently changing facts, including news, prices, law, regulations, schedules, product information, software versions, sports, weather, financial markets, public figures, or recommendations, use web tools before answering. If web tools are unavailable or fail, say that your answer may be outdated and make the date limitation explicit. Do not agree with or deny claims about events after January 2026 unless you have checked current sources.
</temporal_grounding>

<style_and_formatting>
Use warm, direct prose by default. Keep short questions short. Avoid sycophantic openings, theatrical apologies, and performative empathy. Be kind, steady, and honest.

Use the minimum formatting needed. Prefer paragraphs over headers, bold text, numbered lists, and bullets. Do not use bullets or numbered lists for ordinary explanations, reports, documents, or refusals unless the user explicitly asks for a list or the answer would be much harder to understand without one. If the user asks for minimal formatting, honor that exactly. Do not use emojis unless the user asks for them or just used them.
</style_and_formatting>

<acting_vs_clarifying>
When minor details are missing, make a reasonable attempt instead of interviewing the user. Ask at most one clarifying question only when the task is genuinely impossible or risky without the missing detail. If a tool can resolve the ambiguity, use the tool first.

Once you start a task, finish it. Search again when results are off target, inspect files before editing, run relevant checks when you can, and use tool results to answer instead of making the user read raw logs.
</acting_vs_clarifying>

<tool_use_policy>
You have Anthropic server tools, local workspace tools, and optional MCP toolsets. Use web_search for broad current discovery and web_fetch or WebFetch for specific URLs or deeper reading. Use local Read, Glob, Grep, Edit, Write, Bash, and str_replace_based_edit_tool for code and file work. Use code_execution for isolated calculation, data analysis, and generated files when it is the better environment. Use MCP tools for configured external systems.

Before saying you lack access to files, external data, a user's connected system, or a capability, inspect the available tools and MCP toolsets. When the user asks you to take an external action, such as sending, scheduling, posting, or updating something, using a tool is the task; an inline draft is only a fallback after you determine no relevant integration exists.

When using web sources, cite sources when the answer depends on them. Quote sparingly: at most one short quote per source, and no more than 15 quoted words from a source unless the user provided the text.
</tool_use_policy>

<safety_and_refusals>
You can discuss virtually any topic factually and objectively, but keep firm boundaries. Never create romantic or sexual content involving minors, content that facilitates grooming, secrecy, isolation of a minor from trusted adults, or any content that could help sexualize, abuse, or harm children. If you find yourself mentally reframing a child-safety request to make it acceptable, refuse instead.

Do not provide technical details that enable weapons, explosives, chemical, biological, radiological, or nuclear harm. Do not write, explain, or improve malicious code, malware, exploit chains, phishing or spoofing sites, ransomware, viruses, credential theft, or evasion. Decline briefly and, when possible, offer a safe alternative.

You may write creative content involving fictional characters, but avoid creative writing involving real named public figures and avoid attributing fictional quotes to them.
</safety_and_refusals>

<wellbeing>
Support the user's wellbeing. Do not encourage self-harm, addiction, disordered eating, unhealthy exercise, or extreme self-criticism. If a user is in emotional distress and asks for information that could facilitate harm, address the distress rather than providing the requested details. For mental health crisis signals, express concern and offer appropriate resources without asking safety-assessment questions or making categorical promises about helpline policies.

If a user shows signs of disordered eating, do not provide precise nutrition, diet, weight, calorie, or exercise targets or step-by-step plans. If a user may be experiencing mania, psychosis, dissociation, or loss of attachment with reality, do not reinforce the belief; share concern plainly and suggest support from a trusted person or professional.
</wellbeing>

<legal_financial_and_medical>
For legal, financial, or medical questions, provide useful factual information and decision frameworks without presenting yourself as a lawyer, financial advisor, or clinician. Avoid confident recommendations such as what trade to make or what legal action to take. Encourage consulting an appropriate professional for high-stakes decisions.
</legal_financial_and_medical>

<evenhandedness>
For political, ethical, policy, empirical, or otherwise contested topics, treat the request as a good-faith inquiry. If asked to argue for a view, present the best case defenders would make rather than framing it as your personal belief, and include meaningful opposing perspectives or empirical disputes where relevant. Decline single-word verdicts on complex contested issues when nuance is needed.
</evenhandedness>

<mistakes_and_criticism>
When you make a mistake, own it and fix it without excessive self-critique. If the user is dissatisfied, stay focused on solving the problem. Maintain respectful, self-possessed helpfulness.
</mistakes_and_criticism>
</claude_ai_behavior>"""


TOOLING_CONTEXT_PROMPT = """<available_tooling_context>
This runtime wires Claude to live web search, server-side web fetch, server-side code execution, local URL fetch, local bash, local file read/write/edit/glob/grep tools, synchronous Task sub-agent calls, Anthropic text editor compatibility, and remote MCP toolsets when configured.

Distinguish Anthropic server-side code_execution from local Bash/File tools. Local paths are constrained to the submitted workspace. Bash is non-interactive. Remote MCP servers may expose additional tools for connected systems.
</available_tooling_context>"""


class HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip_depth += 1
        if tag in {"p", "br", "div", "li", "tr", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
        if tag in {"p", "div", "li", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        return clean_text(" ".join(self.parts))


def load_env_local() -> None:
    env_path = WORKSPACE_ROOT / ".env.local"
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


def env_flag(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off", ""}


def env_int(name: str, default: int, minimum: int = 1, maximum: int = 100) -> int:
    try:
        value = int(os.getenv(name, ""))
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def truncate(text: str, limit: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 200].rstrip() + f"\n\n[truncated to {limit} characters]"


def current_date_for_prompt(context: dict[str, Any]) -> str:
    raw_date = (
        context.get("current_date")
        or context.get("currentDate")
        or context.get("date")
        or os.getenv("CURRENT_DATE")
    )
    if raw_date:
        return str(raw_date)
    return date.today().isoformat()


def container_id_from(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("id")
    return str(value).strip() if value else ""


def verified_ssl_context() -> ssl.SSLContext | None:
    try:
        import certifi
    except ImportError:
        return None
    return ssl.create_default_context(cafile=certifi.where())


def normalize_content_text(content: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    citations: list[str] = []
    for block in content:
        if block.get("type") == "text" and block.get("text"):
            chunks.append(block["text"])
            for citation in block.get("citations", []) or []:
                url = citation.get("url")
                title = citation.get("title") or url
                if url:
                    citations.append(f"- {title}: {url}")
    if citations:
        chunks.append("\nSources:\n" + "\n".join(dict.fromkeys(citations)))
    return "\n".join(chunks).strip()


class OpusToolAgent(Agent):
    AGENT_ID = AGENT_ID

    def __init__(self) -> None:
        load_env_local()
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self.haiku_model = os.getenv("ANTHROPIC_WEBFETCH_MODEL", DEFAULT_HAIKU_MODEL)
        self.max_tool_rounds = env_int(
            "ANTHROPIC_MAX_TOOL_ROUNDS",
            DEFAULT_MAX_TOOL_ROUNDS,
            1,
            8,
        )

    def freeform(self, query: AgentQuery) -> str:
        if not self.api_key:
            return "ANTHROPIC_API_KEY is not configured for this runtime."

        messages = self.initial_messages(query)
        tools, mcp_servers = self.build_tools(query.context or {})
        system_prompt = self.system_prompt(query.context or {})
        beta_headers = [MCP_BETA] if mcp_servers else []
        has_code_execution = any(tool.get("name") == "code_execution" for tool in tools)
        container_id = self.initial_container_id(query.context or {})

        last_response: dict[str, Any] | None = None
        for _ in range(self.max_tool_rounds + 1):
            payload = {
                "model": str((query.context or {}).get("model") or self.model),
                "max_tokens": int((query.context or {}).get("max_tokens") or DEFAULT_MAX_TOKENS),
                "system": system_prompt,
                "messages": messages,
                "tools": tools,
            }
            if mcp_servers:
                payload["mcp_servers"] = mcp_servers
            if has_code_execution and container_id:
                payload["container"] = container_id

            response = self.call_anthropic(payload, beta_headers)
            if "_error" in response:
                return response["_error"]
            last_response = response
            container_id = self.response_container_id(response) or container_id

            stop_reason = response.get("stop_reason")
            content = response.get("content", [])
            if stop_reason == "pause_turn":
                messages.append({"role": "assistant", "content": content})
                continue
            if stop_reason != "tool_use":
                return normalize_content_text(content) or "Anthropic returned an empty response."

            tool_results = self.execute_tool_uses(content)
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": tool_results})

        if last_response:
            return normalize_content_text(last_response.get("content", [])) or (
                "Stopped after maximum tool rounds without a final text response."
            )
        return "Stopped before Anthropic returned a response."

    def initial_container_id(self, context: dict[str, Any]) -> str:
        return (
            container_id_from(context.get("container"))
            or container_id_from(context.get("container_id"))
            or container_id_from(context.get("containerId"))
        )

    def response_container_id(self, response: dict[str, Any]) -> str:
        return container_id_from(response.get("container"))

    def initial_messages(self, query: AgentQuery) -> list[dict[str, Any]]:
        context = query.context or {}
        messages = context.get("messages")
        if isinstance(messages, list) and messages:
            return messages
        return [{"role": "user", "content": query.prompt}]

    def system_prompt(self, context: dict[str, Any]) -> str:
        current_date = current_date_for_prompt(context)
        prompt_parts = [
            CLAUDE_AI_BEHAVIOR_PROMPT.format(
                current_date=current_date,
                knowledge_cutoff=KNOWLEDGE_CUTOFF,
            ),
            TOOLING_CONTEXT_PROMPT,
        ]

        base = str(context.get("system") or "").strip()
        if base:
            prompt_parts.append(
                "<request_specific_system_instructions>\n"
                f"{base}\n"
                "</request_specific_system_instructions>"
            )

        return "\n\n".join(prompt_parts)

    def build_tools(self, context: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        tools: list[dict[str, Any]] = []

        if env_flag("ENABLE_WEB_SEARCH", True):
            tools.append(
                {
                    "type": os.getenv("ANTHROPIC_WEB_SEARCH_TOOL", "web_search_20260209"),
                    "name": "web_search",
                    "max_uses": env_int("ANTHROPIC_WEB_SEARCH_MAX_USES", 5, 1, 20),
                }
            )

        if env_flag("ENABLE_SERVER_WEB_FETCH", True):
            tools.append(
                {
                    "type": os.getenv("ANTHROPIC_WEB_FETCH_TOOL", "web_fetch_20260209"),
                    "name": "web_fetch",
                    "max_uses": env_int("ANTHROPIC_WEB_FETCH_MAX_USES", 5, 1, 20),
                    "citations": {"enabled": True},
                    "max_content_tokens": env_int("ANTHROPIC_WEB_FETCH_MAX_TOKENS", 50_000, 1000, 100_000),
                }
            )

        if env_flag("ENABLE_CODE_EXECUTION", True):
            tools.append(
                {
                    "type": os.getenv("ANTHROPIC_CODE_EXECUTION_TOOL", "code_execution_20260120"),
                    "name": "code_execution",
                }
            )

        if env_flag("ENABLE_BASH", True):
            tools.append({"type": "bash_20250124", "name": "bash"})
            tools.append(self.tool_bash())
        if env_flag("ENABLE_FILE_TOOLS", True):
            tools.extend(
                [
                    self.tool_read(),
                    self.tool_write(),
                    self.tool_edit(),
                    self.tool_glob(),
                    self.tool_grep(),
                    {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool", "max_characters": 12_000},
                ]
            )
        if env_flag("ENABLE_WEB_FETCH", True):
            tools.append(self.tool_web_fetch())
        if env_flag("ENABLE_TASK", True):
            tools.append(self.tool_task())

        mcp_servers = self.mcp_servers(context)
        for server in mcp_servers:
            tools.append(
                {
                    "type": "mcp_toolset",
                    "mcp_server_name": server["name"],
                    "default_config": {"enabled": True, "defer_loading": False},
                }
            )
        return tools, mcp_servers

    def call_anthropic(
        self,
        payload: dict[str, Any],
        beta_headers: list[str] | None = None,
    ) -> dict[str, Any]:
        headers = {
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
            "x-api-key": self.api_key,
        }
        if beta_headers:
            headers["anthropic-beta"] = ",".join(beta_headers)
        request = urllib.request.Request(
            ANTHROPIC_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                context=verified_ssl_context(),
            ) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            return {"_error": f"Anthropic API returned HTTP {exc.code}: {body}"}
        except urllib.error.URLError as exc:
            return {"_error": f"Anthropic API request failed: {exc.reason}"}

    def execute_tool_uses(self, content: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for block in content:
            if block.get("type") != "tool_use":
                continue
            name = block.get("name", "")
            tool_input = block.get("input") or {}
            try:
                output = self.execute_tool(name, tool_input)
                is_error = False
            except Exception as exc:
                output = f"{type(exc).__name__}: {exc}"
                is_error = True
            result: dict[str, Any] = {
                "type": "tool_result",
                "tool_use_id": block["id"],
                "content": truncate(str(output)),
            }
            if is_error:
                result["is_error"] = True
            results.append(result)
        return results

    def execute_tool(self, name: str, tool_input: dict[str, Any]) -> str:
        if name == "Read":
            return self.read_file(tool_input)
        if name == "Write":
            return self.write_file(tool_input)
        if name == "Edit":
            return self.edit_file(tool_input)
        if name == "Glob":
            return self.glob_files(tool_input)
        if name == "Grep":
            return self.grep_files(tool_input)
        if name in {"Bash", "bash"}:
            return self.run_bash(tool_input)
        if name == "WebFetch":
            return self.local_web_fetch(tool_input)
        if name == "Task":
            return self.run_task(tool_input)
        if name == "str_replace_based_edit_tool":
            return self.text_editor(tool_input)
        return f"Unknown tool: {name}"

    def resolve_path(self, raw_path: str) -> Path:
        candidate = Path(raw_path or ".").expanduser()
        if not candidate.is_absolute():
            candidate = WORKSPACE_ROOT / candidate
        resolved = candidate.resolve()
        root = WORKSPACE_ROOT.resolve()
        if resolved != root and root not in resolved.parents:
            raise ValueError(f"Path escapes workspace root: {raw_path}")
        return resolved

    def read_file(self, tool_input: dict[str, Any]) -> str:
        path = self.resolve_path(str(tool_input.get("path") or "."))
        if path.is_dir():
            items = sorted(item.name + ("/" if item.is_dir() else "") for item in path.iterdir())
            return "\n".join(items)
        text = path.read_text(encoding="utf-8", errors="replace")
        start = int(tool_input.get("start_line") or 1)
        limit = int(tool_input.get("limit") or 300)
        lines = text.splitlines()
        selected = lines[start - 1 : start - 1 + limit]
        return "\n".join(f"{idx}: {line}" for idx, line in enumerate(selected, start=start))

    def write_file(self, tool_input: dict[str, Any]) -> str:
        path = self.resolve_path(str(tool_input.get("path") or ""))
        content = str(tool_input.get("content") or "")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} characters to {path.relative_to(WORKSPACE_ROOT)}."

    def edit_file(self, tool_input: dict[str, Any]) -> str:
        path = self.resolve_path(str(tool_input.get("path") or ""))
        old = str(tool_input.get("old_string") or tool_input.get("old_str") or "")
        new = str(tool_input.get("new_string") or tool_input.get("new_str") or "")
        replace_all = bool(tool_input.get("replace_all"))
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if not old:
            raise ValueError("old_string is required.")
        if count == 0:
            raise ValueError("old_string was not found.")
        if count > 1 and not replace_all:
            raise ValueError(f"old_string matched {count} times; set replace_all=true to replace all.")
        path.write_text(text.replace(old, new, -1 if replace_all else 1), encoding="utf-8")
        return f"Replaced {count if replace_all else 1} occurrence(s) in {path.relative_to(WORKSPACE_ROOT)}."

    def glob_files(self, tool_input: dict[str, Any]) -> str:
        pattern = str(tool_input.get("pattern") or "**/*")
        base = self.resolve_path(str(tool_input.get("path") or "."))
        matches = sorted(
            str(Path(match).resolve().relative_to(WORKSPACE_ROOT))
            for match in glob_module.glob(str(base / pattern), recursive=True)
        )
        return "\n".join(matches[:500]) or "No matches."

    def grep_files(self, tool_input: dict[str, Any]) -> str:
        pattern = str(tool_input.get("pattern") or "")
        if not pattern:
            raise ValueError("pattern is required.")
        base = self.resolve_path(str(tool_input.get("path") or "."))
        include = str(tool_input.get("include") or "*")
        flags = re.IGNORECASE if tool_input.get("ignore_case") else 0
        regex = re.compile(pattern, flags)
        max_results = int(tool_input.get("max_results") or 200)
        results: list[str] = []
        for path in base.rglob("*") if base.is_dir() else [base]:
            if not path.is_file() or not fnmatch.fnmatch(path.name, include):
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, start=1):
                if regex.search(line):
                    results.append(f"{path.relative_to(WORKSPACE_ROOT)}:{line_no}: {line}")
                    if len(results) >= max_results:
                        return "\n".join(results)
        return "\n".join(results) or "No matches."

    def run_bash(self, tool_input: dict[str, Any]) -> str:
        command = str(tool_input.get("command") or "")
        if not command:
            raise ValueError("command is required.")
        completed = subprocess.run(
            command,
            shell=True,
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
        )
        return (
            f"exit_code={completed.returncode}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    def local_web_fetch(self, tool_input: dict[str, Any]) -> str:
        url = str(tool_input.get("url") or "")
        prompt = str(tool_input.get("prompt") or "Summarize the fetched page.")
        if not url.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 OpusToolAgent/1.0"},
        )
        with urllib.request.urlopen(request, context=verified_ssl_context()) as response:
            raw = response.read(MAX_WEB_FETCH_CHARS).decode("utf-8", errors="replace")
            media_type = response.headers.get("content-type", "")

        text = self.html_to_text(raw) if "html" in media_type else clean_text(raw)
        if env_flag("ANTHROPIC_WEBFETCH_USE_HAIKU", True):
            summary = self.summarize_with_haiku(url, prompt, text)
            if summary:
                return summary
        return f"Fetched {url}\nContent-Type: {media_type}\n\n{truncate(text)}"

    def html_to_text(self, raw_html: str) -> str:
        parser = HTMLTextExtractor()
        parser.feed(raw_html)
        return parser.text()

    def summarize_with_haiku(self, url: str, prompt: str, text: str) -> str:
        payload = {
            "model": self.haiku_model,
            "max_tokens": 1024,
            "system": "Summarize fetched web content for a parent Opus agent. Be concise and cite the URL.",
            "messages": [
                {
                    "role": "user",
                    "content": f"URL: {url}\nTask: {prompt}\n\nContent:\n{truncate(text, 20_000)}",
                }
            ],
        }
        response = self.call_anthropic(payload, [])
        if "_error" in response:
            return ""
        return normalize_content_text(response.get("content", []))

    def run_task(self, tool_input: dict[str, Any]) -> str:
        prompt = str(tool_input.get("prompt") or "")
        if not prompt:
            raise ValueError("prompt is required.")
        description = str(tool_input.get("description") or "subtask")
        model = str(tool_input.get("model") or self.model)
        payload = {
            "model": model,
            "max_tokens": int(tool_input.get("max_tokens") or 1024),
            "system": f"You are a focused sub-agent. Complete this delegated task: {description}",
            "messages": [{"role": "user", "content": prompt}],
        }
        response = self.call_anthropic(payload, [])
        if "_error" in response:
            return response["_error"]
        return normalize_content_text(response.get("content", []))

    def text_editor(self, tool_input: dict[str, Any]) -> str:
        command = str(tool_input.get("command") or "")
        if command == "view":
            return self.read_file(tool_input)
        if command == "create":
            return self.write_file({"path": tool_input.get("path"), "content": tool_input.get("file_text", "")})
        if command == "str_replace":
            return self.edit_file(
                {
                    "path": tool_input.get("path"),
                    "old_string": tool_input.get("old_str"),
                    "new_string": tool_input.get("new_str"),
                }
            )
        if command == "insert":
            path = self.resolve_path(str(tool_input.get("path") or ""))
            insert_line = int(tool_input.get("insert_line") or 0)
            insert_text = str(tool_input.get("insert_text") or "")
            lines = path.read_text(encoding="utf-8").splitlines()
            index = max(0, min(insert_line, len(lines)))
            lines[index:index] = insert_text.splitlines()
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return f"Inserted text after line {insert_line} in {path.relative_to(WORKSPACE_ROOT)}."
        raise ValueError(f"Unsupported text editor command: {command}")

    def mcp_servers(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        raw_servers = context.get("mcp_servers")
        if not raw_servers:
            raw_servers = os.getenv("MCP_SERVERS_JSON", "")
        servers: list[dict[str, Any]] = []
        if isinstance(raw_servers, str) and raw_servers.strip():
            try:
                raw_servers = json.loads(raw_servers)
            except json.JSONDecodeError:
                raw_servers = []
        if isinstance(raw_servers, list):
            for item in raw_servers:
                if not isinstance(item, dict):
                    continue
                server = {
                    "type": "url",
                    "url": item.get("url"),
                    "name": item.get("name"),
                }
                token = item.get("authorization_token") or item.get("token")
                if token:
                    server["authorization_token"] = token
                if server["url"] and server["name"]:
                    servers.append(server)

        single_url = os.getenv("MCP_SERVER_URL")
        single_name = os.getenv("MCP_SERVER_NAME", "default-mcp")
        if single_url:
            server = {"type": "url", "url": single_url, "name": single_name}
            token = os.getenv("MCP_AUTH_TOKEN")
            if token:
                server["authorization_token"] = token
            servers.append(server)
        return servers

    def tool_read(self) -> dict[str, Any]:
        return {
            "name": "Read",
            "description": "Read a file or list a directory inside the submitted workspace. Use this for local source, config, logs, and text artifacts. Paths are constrained to the workspace root. Optional start_line and limit return a line-numbered slice.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start_line": {"type": "integer"},
                    "limit": {"type": "integer"},
                },
                "required": ["path"],
            },
        }

    def tool_write(self) -> dict[str, Any]:
        return {
            "name": "Write",
            "description": "Create or overwrite a text file inside the submitted workspace. Use for explicit file creation tasks. Parent directories are created automatically; paths cannot escape the workspace root.",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        }

    def tool_edit(self) -> dict[str, Any]:
        return {
            "name": "Edit",
            "description": "Perform an exact string replacement in a workspace file. Use this for surgical edits. By default old_string must match exactly once; set replace_all true only when every occurrence should be replaced.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_string": {"type": "string"},
                    "new_string": {"type": "string"},
                    "replace_all": {"type": "boolean"},
                },
                "required": ["path", "old_string", "new_string"],
            },
        }

    def tool_glob(self) -> dict[str, Any]:
        return {
            "name": "Glob",
            "description": "Find files by glob pattern inside the workspace. Use patterns like '**/*.py' or 'docs/*.md'. Returns up to 500 workspace-relative paths.",
            "input_schema": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}},
                "required": ["pattern"],
            },
        }

    def tool_grep(self) -> dict[str, Any]:
        return {
            "name": "Grep",
            "description": "Search workspace files with a regular expression. Use include to restrict file names, for example '*.py'. Returns path:line matches.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"},
                    "include": {"type": "string"},
                    "ignore_case": {"type": "boolean"},
                    "max_results": {"type": "integer"},
                },
                "required": ["pattern"],
            },
        }

    def tool_bash(self) -> dict[str, Any]:
        return {
            "name": "Bash",
            "description": "Run a non-interactive shell command in the workspace. Use for tests, inspection, package commands, and simple automation. Returns stdout, stderr, and exit code.",
            "input_schema": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        }

    def tool_web_fetch(self) -> dict[str, Any]:
        return {
            "name": "WebFetch",
            "description": "Fetch a specific URL from the local runtime and return relevant text. If ANTHROPIC_WEBFETCH_USE_HAIKU is enabled, the fetched content is summarized with a Haiku sub-call before being returned to Opus. Use this when the user gives a URL or when a web_search result needs deeper reading.",
            "input_schema": {
                "type": "object",
                "properties": {"url": {"type": "string"}, "prompt": {"type": "string"}},
                "required": ["url"],
            },
        }

    def tool_task(self) -> dict[str, Any]:
        return {
            "name": "Task",
            "description": "Spawn a synchronous sub-agent by making a separate Anthropic Messages API call. Use for bounded research, critique, or parallel-style reasoning that can be summarized back to the main Opus agent.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "prompt": {"type": "string"},
                    "model": {"type": "string"},
                    "max_tokens": {"type": "integer"},
                },
                "required": ["prompt"],
            },
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
    print(OpusToolAgent().freeform(query))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
