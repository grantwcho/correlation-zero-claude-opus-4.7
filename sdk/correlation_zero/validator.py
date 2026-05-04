import importlib.util
import inspect
import sys
from pathlib import Path

import yaml

from .agent_base import Agent
from .schemas import AgentQuery, ResponseFormat


REQUIRED_MANIFEST_FIELDS = [
    "schema_version",
    "agent_id",
    "name",
    "response_formats",
]


def load_manifest(repo_dir: Path) -> dict:
    manifest_path = repo_dir / "manifest.yaml"
    if not manifest_path.exists():
        raise ValueError("Missing manifest.yaml")

    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle) or {}

    if not isinstance(manifest, dict):
        raise ValueError("manifest.yaml must parse to an object")

    return manifest


def validate_manifest_data(manifest: dict) -> list[str]:
    errors: list[str] = []

    for field_name in REQUIRED_MANIFEST_FIELDS:
        if field_name not in manifest:
            errors.append(f"manifest.yaml is missing required field: {field_name}")

    if "metrics" in manifest and not isinstance(manifest.get("metrics"), list):
        errors.append("manifest.yaml field 'metrics' must be a list")

    if "response_formats" in manifest:
        response_formats = manifest.get("response_formats")
        if not isinstance(response_formats, list):
            errors.append("manifest.yaml field 'response_formats' must be a list")
        elif response_formats != [ResponseFormat.FREEFORM.value]:
            errors.append("manifest.yaml field 'response_formats' must be exactly: [freeform]")

    return errors


def load_agent_module(repo_dir: Path):
    agent_path = repo_dir / "agent.py"
    if not agent_path.exists():
        raise ValueError("Missing agent.py")

    spec = importlib.util.spec_from_file_location("submitted_agent", agent_path)
    if spec is None or spec.loader is None:
        raise ValueError("Could not import agent.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_agent(module) -> Agent:
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, Agent) and obj is not Agent:
            return obj()
    raise ValueError("agent.py must define a subclass of correlation_zero.Agent")


def build_test_query(manifest: dict) -> AgentQuery:
    metrics = manifest.get("metrics", [])
    if not isinstance(metrics, list):
        metrics = []

    return AgentQuery(
        query_id="local-test",
        prompt="Return a short response that proves the agent can handle a platform query.",
        context={
            "agent_id": manifest.get("agent_id"),
            "agent_name": manifest.get("name"),
            "validation": True,
        },
        metrics=metrics,
    )


def validate_freeform(agent: Agent, manifest: dict) -> list[str]:
    query = build_test_query(manifest)

    try:
        result = agent.freeform(query)
    except Exception as exc:
        return [f"freeform(query) raised an exception: {exc}"]

    if not isinstance(result, str):
        return ["freeform(query) must return a string"]

    return []


def validate_repo(repo_dir: Path) -> list[str]:
    manifest = load_manifest(repo_dir)
    module = load_agent_module(repo_dir)
    agent = build_agent(module)

    errors = validate_manifest_data(manifest)

    if manifest.get("agent_id") and getattr(agent, "AGENT_ID", None) != manifest["agent_id"]:
        errors.append("AGENT_ID must match manifest.yaml agent_id")

    errors.extend(validate_freeform(agent, manifest))
    return errors


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    repo_dir = Path(argv[0]).resolve() if argv else Path.cwd()

    try:
        errors = validate_repo(repo_dir)
    except Exception as exc:
        print(f"x {exc}")
        return 1

    if errors:
        for error in errors:
            print(f"x {error}")
        return 1

    print("All checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
