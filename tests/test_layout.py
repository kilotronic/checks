"""The one-repository layout: each tool in its own folder, one hook manifest, one package for the hooks."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = [
    "lint",
    "git-identity",
    "secret-scan",
    "data-leak-check",
    "vendored-license-check",
    "red-on-logic",
]
MANIFEST = (ROOT / ".pre-commit-hooks.yaml").read_text()


def scripts(pyproject: Path) -> dict[str, str]:
    return tomllib.loads(pyproject.read_text()).get("project", {}).get("scripts", {})


def hooks() -> list[dict[str, str]]:
    """Each hook in the manifest as its top-level keys, with the tool heading it sits under."""
    found, tool = [], None
    for line in MANIFEST.splitlines():
        if m := re.match(r"# === (\S+)$", line):
            tool = m.group(1)
        elif m := re.match(r"- id: (\S+)$", line):
            found.append({"id": m.group(1), "tool": tool})
        elif found and (m := re.match(r"  (\w+): (.*)$", line)):
            found[-1][m.group(1)] = m.group(2)
    return found


def test_each_tool_is_a_folder_with_its_action() -> None:
    for tool in TOOLS:
        assert (ROOT / tool / "action.yml").is_file(), tool


def test_hook_ids_are_unique() -> None:
    ids = [h["id"] for h in hooks()]
    assert len(ids) == 29
    assert len(ids) == len(set(ids))


def test_every_hook_sits_under_a_tool_heading() -> None:
    assert {h["tool"] for h in hooks()} <= set(TOOLS)
    assert all(h["tool"] for h in hooks())


def test_script_hooks_run_a_file_in_their_tools_folder() -> None:
    for h in hooks():
        if h["language"] == "script":
            path = h["entry"].split()[0]
            assert path.startswith(f"{h['tool']}/"), h["id"]
            assert (ROOT / path).is_file(), h["id"]


def test_the_root_package_carries_every_hook_tools_commands() -> None:
    union: dict[str, str] = {}
    for tool in TOOLS:
        own = ROOT / tool / "pyproject.toml"
        if (
            tool != "red-on-logic" and own.is_file()
        ):  # red-on-logic is an Action only, with no hook
            union |= scripts(own)
    assert scripts(ROOT / "pyproject.toml") == union


def test_python_and_node_hooks_run_a_command_the_root_installs() -> None:
    own = set(scripts(ROOT / "pyproject.toml"))
    own |= set(json.loads((ROOT / "package.json").read_text())["bin"])
    for h in hooks():
        command = h["entry"].split()[0]
        if h["language"] in ("python", "node") and "additional_dependencies" not in h:
            assert command in own, h["id"]


def test_the_root_package_names_each_tool_package_that_exists() -> None:
    wheel = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["hatch"][
        "build"
    ]["targets"]["wheel"]
    for path in wheel["packages"]:
        assert (ROOT / path / "__init__.py").is_file(), path


def test_no_action_writes_an_input_into_a_run_script() -> None:
    # An input is the caller's text; written into a run: script it becomes shell code. Pass it
    # through env: and use "$NAME".
    for tool in TOOLS:
        action = (ROOT / tool / "action.yml").read_text()
        for n, line in enumerate(action.splitlines(), 1):
            stripped = line.strip()
            if "${{ inputs." in line and (
                stripped.startswith("run:") or not re.match(r"[\w-]+: ", stripped)
            ):
                raise AssertionError(f"{tool}/action.yml:{n}: {stripped}")
