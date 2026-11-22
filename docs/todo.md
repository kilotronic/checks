# To do

Known faults in the tools, one entry each. Remove an entry in the pull request that fixes it.

## git-identity lets an allowed bot's merge carry a Claude-Session line

In a public repository, git-identity refuses a commit whose message has a `Claude-Session:` line, but not when
the commit is an allowed bot's own update (for example a squash merge by the agents App). `action.sh` returns as
soon as the bot check passes, before it reaches the session-line check, so a squash merge that copies a
`Claude-Session:` line from the pull request reaches main unrefused. The session-line check should run whatever
the bot check decides. Test first: a bot-authored squash commit carrying the line, in a public repository, is
refused.

## The hooks install on Python 3.9 but three tools need 3.11

The root `pyproject.toml` says `requires-python = ">=3.9"`, but git-identity, data-leak-check and
vendored-license-check need Python 3.11 (vendored-license-check imports `tomllib`). On 3.9 or 3.10 the hooks
install without complaint and then crash at every commit. Raise the floor to 3.11, or make the three tools run on
the older versions.

## red-on-logic passes an empty diff, and `.github/` wins over code-paths

Two cases in the "skipped: no source changes" rule:

- A pull request whose diff is empty now passes as having no source changes; before the rule it failed. Decide
  whether an empty diff should pass, and pin that in a test.
- A file under `.github/` counts as not source before the caller's `code-paths` input is checked, so a caller
  that names a `.github/` path as code still gets "skipped". The README says `code-paths` decides; check it
  first.

## us-english misses plural possessives

"organisations'" (a plural possessive) is not rewritten. The possessive forms the hook adds to codespell's list
cover `'s` and `’s` only.

## us-english reports a broken codespell config as a spelling problem

If codespell itself fails (a repository's `.codespellrc` that it can't parse, say), the commit-message hook says
"write the commit message in American English", which sends the author to the wrong fix. Tell a codespell error
apart from a finding by its exit code and say what failed.

## us-english refuses a commit message that names a British identifier

A message such as "rename `initialise()` to `initialize()`" is refused, even with the old name in backticks.
Skip backtick spans in the commit message the way the prose hook skips them in files.
