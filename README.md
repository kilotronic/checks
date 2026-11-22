# checks

The shared check tools, in one repository: each tool in its own folder, every tool released together. A repository
pins one commit of this repository for all of them.

| Tool                                                       | What it refuses                                                                                                      | Action | Hooks |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------ | ----- |
| [lint](lint/README.md)                                     | Shell and workflow findings (shellcheck, actionlint), unpinned actions and images, unsafe workflows; format and lint | yes    | yes   |
| [git-identity](git-identity/README.md)                     | Placeholder and machine-default git authors, emails outside your domains, bad commit subjects                        | yes    | yes   |
| [secret-scan](secret-scan/README.md)                       | Secrets in the commits a pull request or push brings in (gitleaks and trufflehog)                                    | yes    | yes   |
| [data-leak-check](data-leak-check/README.md)               | A denylist of private terms in changes, commit messages and authors                                                  | yes    | yes   |
| [vendored-license-check](vendored-license-check/README.md) | Vendored files without a declared, allow-listed license                                                              | yes    | yes   |
| [red-on-logic](red-on-logic/README.md)                     | A pull request's new tests that don't fail on the base branch's code                                                 | yes    | no    |

## As GitHub Actions

Each tool is an Action in its own folder. Pin the release's commit, with its tag in a comment:

```yaml
- uses: kilotronic/checks/lint@<commit of the release> # v1.0.0
- uses: kilotronic/checks/secret-scan@<commit of the release> # v1.0.0
```

## As pre-commit or prek hooks

One entry lists the hooks you use, from any of the tools. Every hook id is the one the tool had on its own:

```yaml
repos:
  - repo: https://github.com/kilotronic/checks
    rev: <commit of the release> # frozen: v1.0.0
    hooks:
      - id: shellcheck
      - id: pinned
      - id: git-identity
      - id: secret-scan
      - id: data-leak-check
```

The hooks are defined in [.pre-commit-hooks.yaml](.pre-commit-hooks.yaml), under one heading per tool.

## What a repository may skip

Each tool lists the checks a repository may skip in its own `<tool>/skippable.txt`, one id per line, optionally
followed by `opt-in` (a check that runs only when a repository turns it on). The tool reads it, and so does the
owner's settings sweep, at the commit a repository pins.

## Releases

One version for the repository: `vX.Y.Z` tags, never moved or deleted, and no moving major tags. A release notes
which tools changed. Before this repository, each tool was its own repository (kilotronic/lint and the others);
their histories are kept here, under each tool's folder.

## Development

Each tool's tests run from its folder, as its README says; `tests/` at the root checks the layout. CI runs them
all.

MIT
