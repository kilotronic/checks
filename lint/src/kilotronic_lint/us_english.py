"""us-english: codespell's British-to-American list, on prose files (rewritten) and on commit messages (reported).

codespell reads a possessive ("organisation's") as one word that its list does not hold, so each entry is
added again in its possessive forms. The commit message is checked as git will store it: git's comment lines
and the `git commit -v` diff below the scissors line are dropped first, since git removes them after the hook.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import codespell_lib
from git_identity.commit_msg import cleaned

LIST = Path(codespell_lib.__file__).parent / "data" / "dictionary_en-GB_to_en-US.txt"


def possessives(entries: str) -> str:
    """Each `word->fix` entry again as `word's->fix's` (straight and curly apostrophes)."""
    out = []
    for line in entries.splitlines():
        word, sep, fix = line.partition("->")
        if not sep or "," in fix:  # an entry with several fixes or a reason is left to the builtin list
            continue
        for mark in ("'", "’"):
            out.append(f"{word}{mark}s->{fix}{mark}s")
    return "\n".join(out) + "\n"


def codespell(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as extra:
        extra.write(possessives(LIST.read_text(encoding="utf-8")))
    try:
        cmd = ["codespell", "--builtin", "en-GB_to_en-US", "-D", "-", "-D", extra.name, *args]
        return subprocess.run(cmd, input=stdin, capture_output=stdin is not None, text=True, check=False)
    finally:
        Path(extra.name).unlink()


def main(argv: list[str] | None = None) -> int:
    """Prose files: rewrite British spellings to American, as the formatters rewrite files."""
    files = sys.argv[1:] if argv is None else argv
    return codespell(["--write-changes", *files]).returncode if files else 0


def commit_msg_main(argv: list[str] | None = None) -> int:
    """The commit message: report British spellings, leave the message as written."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: kilotronic-us-english-commit-msg <commit message file>", file=sys.stderr)
        return 2
    text = cleaned(Path(args[0]).read_text(encoding="utf-8", errors="replace"))
    out = codespell(["-"], stdin=text)
    report = out.stdout.replace("-:", "commit message line ")
    sys.stdout.write(report)
    if out.returncode:
        if not report:
            sys.stderr.write(out.stderr)
        print("us-english: write the commit message in American English, then commit again.")
        return 1
    return 0
