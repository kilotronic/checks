"""us-english-commit-msg: codespell's British-to-American list on the commit message git will store.

git's comment lines and the `git commit -v` diff below the scissors line are dropped first (git removes them
after the hook runs), so a commit that fixes a British spelling is not refused for the diff it shows.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from git_identity.commit_msg import cleaned

# Words split on letters, digits and hyphens only, so a possessive ("organisation's") is still checked.
ARGS = ["--builtin", "en-GB_to_en-US", r"--regex=[\w\-]+"]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: kilotronic-us-english-commit-msg <commit message file>", file=sys.stderr)
        return 2
    path = args[0]
    text = cleaned(Path(path).read_text(encoding="utf-8", errors="replace"))
    out = subprocess.run(
        ["codespell", *ARGS, "-"], input=text, capture_output=True, text=True, check=False
    )
    report = out.stdout.replace("-:", "commit message line ", -1)
    if report:
        sys.stdout.write(report)
    if out.returncode:
        if not report:
            sys.stderr.write(out.stderr)
        print("us-english: write the commit message in American English, then commit again.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
