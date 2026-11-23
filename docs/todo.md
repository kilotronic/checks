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

## Make zizmor blocking once repos are clean

lint's zizmor check is report-only: it prints its findings and never fails. Make it blocking in a later release,
once the repositories that pin these tools no longer trip it. A trial over the owner's 53 consuming repositories
(151 workflow and action files, zizmor 1.32.0 offline) found, besides the two audits now off as duplicates of
pinned and workflow-safety:

1. Fix first, the high findings: `template-injection` (29 findings in 8 repositories; pass the value through
   `env:` and use `"$NAME"`) and `dangerous-triggers` (4 in 4: drop `pull_request_target` / `workflow_run` or
   prove the job never touches the pull request's code).
2. Then `github-env` (4), `cache-poisoning` (3), `github-app` (9, narrow the token's permissions),
   `use-trusted-publishing` (3) and `adhoc-packages` (2).
3. `artipacked` is the loudest (159 in 37), mostly read-only CI where the token never leaves the job: add
   `persist-credentials: false` to every checkout, a mechanical change a script can make.
4. The style audits (`self-repository`, 38) and the one `obfuscation` finding (this repository's own test
   denylist, on purpose) are turned off or ignored in `lint/src/zizmor.yml` rather than fixed.

Then make the step fail on what is left, with the high findings as the floor, and decide whether to turn on the
online audits (impostor commits, known-vulnerable actions, ref confusion), which need a token. Turning off
`excessive-permissions` also loses its job-level check (2 findings in the trial), which workflow-safety does not
make; give workflow-safety that rule before or with the switch. And settle the config: lint passes its own
`lint/src/zizmor.yml`, so a repository's `zizmor.yml` is ignored; before zizmor can fail a build, a repository
needs a reasoned way to turn off an audit that doesn't fit it.
