"""us-english: codespell's British-to-American list, on prose files (rewritten) and on commit messages (reported).

codespell reads a possessive ("organisation's") as one word that its list does not hold, so each entry is
added again in its possessive forms. The commit message is checked as git will store it: git's comment lines
and the `git commit -v` diff below the scissors line are dropped first, since git removes them after the hook.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path


def british_list() -> Path:
    # Imported here: the hook's environment has codespell (its additional dependency); lint's own does not.
    import codespell_lib

    return (
        Path(codespell_lib.__file__).parent / "data" / "dictionary_en-GB_to_en-US.txt"
    )


def possessives(entries: str) -> str:
    """Each `word->fix` entry again as `word's->fix's` (straight and curly apostrophes)."""
    out = []
    for line in entries.splitlines():
        word, sep, fix = line.partition("->")
        if (
            not sep or "," in fix
        ):  # an entry with several fixes or a reason is left to the builtin list
            continue
        for mark in ("'", "’"):
            out.append(f"{word}{mark}s->{fix}{mark}s")
    return "\n".join(out) + "\n"


def codespell(
    args: list[str], stdin: str | None = None, capture: bool = False
) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    ) as extra:
        extra.write(possessives(british_list().read_text(encoding="utf-8")))
    try:
        cmd = [
            "codespell",
            "--builtin",
            "en-GB_to_en-US",
            "-D",
            "-",
            "-D",
            extra.name,
            *args,
        ]
        return subprocess.run(
            cmd,
            input=stdin,
            capture_output=capture or stdin is not None,
            text=True,
            check=False,
        )
    finally:
        Path(extra.name).unlink()


# Code and link targets in Markdown and reStructuredText are left as written: codespell rewrites a whole line,
# so they are swapped for placeholders in a copy, the copy is fixed, and they are put back.
CODE = re.compile(
    r"(?ms)^[ \t]*(```|~~~).*?^[ \t]*\1[^\n]*$"  # fenced blocks
    r"|``[^`]+``|`[^`\n]+`"  # inline code (rST's double backticks too)
    r"|\]\([^)\s]*\)|<https?://[^>\s]+>|https?://\S+"  # link targets and bare URLs
)


def _mask(text: str) -> tuple[str, list[str]]:
    kept: list[str] = []

    def hold(m: re.Match[str]) -> str:
        kept.append(m.group(0))
        return f"KTKEEP{len(kept) - 1}KTKEEP" + "\n" * m.group(0).count("\n")

    return CODE.sub(hold, text), kept


def _unmask(text: str, kept: list[str]) -> str:
    return re.sub(r"KTKEEP(\d+)KTKEEP\n*", lambda m: kept[int(m.group(1))], text)


def main(argv: list[str] | None = None) -> int:
    """Prose files: rewrite British spellings to American, as the formatters rewrite files."""
    files = sys.argv[1:] if argv is None else argv
    rc = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name in files:
            path = Path(name)
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
            masked, kept = _mask(text)
            copy = Path(tmp) / f"{abs(hash(name))}{path.suffix}"
            copy.write_text(masked, encoding="utf-8", errors="surrogateescape")
            out = codespell(["--write-changes", str(copy)], capture=True)
            sys.stdout.write(out.stdout.replace(str(copy), name))
            sys.stderr.write(out.stderr.replace(str(copy), name))
            fixed = _unmask(
                copy.read_text(encoding="utf-8", errors="surrogateescape"), kept
            )
            if fixed != text:
                path.write_text(fixed, encoding="utf-8", errors="surrogateescape")
                rc = rc or 1
            rc = rc or out.returncode
    return rc


def commit_msg_main(argv: list[str] | None = None) -> int:
    """The commit message: report British spellings, leave the message as written."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(
            "usage: kilotronic-us-english-commit-msg <commit message file>",
            file=sys.stderr,
        )
        return 2
    # git-identity's cleanup, the same one its commit-msg hook uses; the hooks install every tool together.
    from git_identity.commit_msg import cleaned

    text = cleaned(Path(args[0]).read_text(encoding="utf-8", errors="replace"))
    out = codespell(["-"], stdin=text)
    report = re.sub(r"(?m)^(\d+): ", r"commit message line \1: ", out.stdout)
    sys.stdout.write(report)
    if out.returncode:
        if not report:
            sys.stderr.write(out.stderr)
        print(
            "us-english: write the commit message in American English, then commit again."
        )
        return 1
    return 0
