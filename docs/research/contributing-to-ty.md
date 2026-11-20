# Contributing to ty: process and best practices

Research date: 2026-11-20. Local working artifact; not meant to be committed.

Contributing to ty splits into two paths, because the ty repository holds only docs, packaging and release tooling. All Rust type-checker source lives in `astral-sh/ruff` (crates `ty*`), where code PRs go, while issues go to `astral-sh/ty`.

## 1. Summary

- **Two repos.** Code PRs go to `astral-sh/ruff`; issues, docs and packaging changes go to `astral-sh/ty` (`README.md:58-67`, `CONTRIBUTING.md:4-13`).
- **AI policy is enforced.** AI may help write code, but PR bodies, issues and replies must be your own words, and autonomous agent PRs are banned. 131 ruff PRs carry `bot:ai-policy-close`; #29858 was closed the day it opened with no human review.
- **Discuss before building.** "Please do not open pull requests for new features without prior discussion... we will often close these pull requests immediately." (`ruff: CONTRIBUTING.md:35-38`)
- **mdtests are required.** "Any ty pull request to improve ty's type inference or type checking logic should include mdtests demonstrating the effect of the change" (`ruff: crates/ty/CONTRIBUTING.md:124-125`).
- **Outside PRs are rare but land fast.** About 2.5% of ty commits since 2026-09-01 come from outside the regular group. Narrow, issue-linked fixes with mdtests merged in 0 to 3 days.
- **Django is one maintainer's active work.** sharkdp wrote all seven merged Django commits and both open drafts, and has asked for specific bug reports. No maintainer has said outside Django PRs are welcome or unwelcome.

## 2. Which repo for which change

| Change | Where | Source |
| --- | --- | --- |
| Type-checker, CLI, LSP, IDE code (Rust) | PR to `astral-sh/ruff`, crates `ty*` | `README.md:65-67` |
| Bug reports, feature requests, questions | Issue in `astral-sh/ty` (ruff's issue chooser redirects there) | `README.md:58-59`; `ruff: .github/ISSUE_TEMPLATE/config.yml:3-5` |
| Hand-written docs under `docs/`, including `typing-faq.md`, `editor-settings.md`, `exit-codes.md` | PR to `astral-sh/ty` | `.pre-commit-config.yaml:3-7` |
| `docs/reference/{cli,configuration,rules,environment}.md` | Rust doc comments in ruff; the files are copied from `ruff/crates/ty/docs/` | `scripts/autogenerate_files.sh:22-25`; `CONTRIBUTING.md:19-24` |
| `docs/reference/ty-extensions.md` | Docstrings in `ruff/crates/ty_vendored/ty_extensions/__init__.pyi` | `scripts/generate_ty_extensions_docs.py:14-15,22-23` |
| Packaging, CI, scripts in the ty repo | PR to `astral-sh/ty` | `CONTRIBUTING.md:10-13` |
| Releases | Astral team only | `CONTRIBUTING.md:139` |
| Vulnerabilities | Email `security at astral dot sh` | `SECURITY.md:5` |

A merged ruff PR reaches users only at the next ty release, because the submodule "is only updated on release" (`CONTRIBUTING.md:26-28`). Its title and labels become the changelog entry (`pyproject.toml:194-217`).

## 3. Before you write code

Most rejected outside PRs were closed on direction, so the choice of issue matters more than the code.

- **Small fixes:** "For small changes (e.g., bug fixes), feel free to submit a PR." (`ruff: crates/ty/CONTRIBUTING.md:14-18`)
- **Larger changes** (new diagnostics, functionality, config options): open an issue in `astral-sh/ty` or discuss on Discord first (same cite).
- **Unlabeled issues:** "Please check in with us before starting work on an issue that has not been labeled as appropriate for community contribution." (`ruff: CONTRIBUTING.md:25-27`)
- **Closed labels:** "Please do not open pull requests for issues with these labels." This covers `needs-decision` and `needs-design` (`ruff: CONTRIBUTING.md:31-33`).
- **Competing PRs:** "If an open pull request already addresses the issue, do not submit a competing one without maintainer agreement." Check before starting and again before opening (`ruff: AGENTS.md:7-9`).
- **Linked PRs:** read the issue discussion and sidebar; closed attempts hold review context (`ruff: CONTRIBUTING.md:42-45`).
- **Claiming:** say you are working on a labeled issue (`ruff: CONTRIBUTING.md:29-31`). No further claim procedure was observed.
- **What works in practice:** successful outside PRs fix a specific existing ty issue, often one the author filed (88ee6e53e fixes ty#4708).

Label counts in `astral-sh/ty` on 2026-11-20 (https://github.com/astral-sh/ty/labels):

| Label | Open issues | Meaning for you |
| --- | --- | --- |
| `help wanted` | 7 (#206, #921, #953, #1771, #2171, #2276, #2644; #2644 is assigned) | Open for contribution |
| `good first issue` | 0 | Not a usable signal |
| `bug` | not counted | "ready for contributions" (`ruff: crates/ty/CONTRIBUTING.md:19-21`) |
| `needs-decision` / `needs-design` | 33 / 13 | Do not open PRs |
| `wish` | 92 | "Not on the current roadmap" |
| `library` / `django` / `pydantic` | 38 / 2 / 9 | Library-support work |

## 4. AI-use policy

The policy applies to external contributors and is required by `ruff: CONTRIBUTING.md:49-52`: "If your contribution does not follow the policy, it will be closed." Its text is at https://raw.githubusercontent.com/astral-sh/.github/main/AI_POLICY.md.

| | Rule (exact quotes) |
| --- | --- |
| Allowed | "We support using AI (i.e., LLMs) as tools for coding. However, you remain responsible for any code you publish" |
| Forbidden | "**AI should not be used to generate comments when communicating with maintainers**... We may hide any comments that we believe are AI generated." |
| Forbidden | "**Do not copy responses from the AI when replying to questions from maintainers.**" |
| Forbidden | "**We do not allow autonomous agents to be used for contributing to our projects**. We will close any pull requests that we believe were created autonomously." |
| Required | Issues described "in your own words" |
| Required | "be able to explain the proposed changes in your own words. This includes the pull request body and responses to questions." |
| Required | "we require a human in the loop who understands the work produced by AI." |
| Disclosure | AI context in comments "must be in a quote block (e.g., using `>`) and disclosed as such"; "Do not share long snippets." |
| Non-native speakers | "Write in your native language, and include the AI translation in a quote block beneath it." |

**Enforcement**
- Two labels, `bot:ai-policy-comment` and `bot:ai-policy-close`, dispatch the shared `astral-sh/github-actions/ai-policy` action (`.github/workflows/ai-policy.yml:20-24,54-59`; `ruff: .github/workflows/ai-policy.yml:18-24,54-59`).
- Comment versus close behaviour is inferred from the label names; the action source was not read.
- #29858 was bot-closed the day it opened: "We support using AI (i.e., LLMs) while coding. However, AI should not be used to communicate with maintainers."
- #30186 was flagged and moved to draft. ntBre wrote: "It's not about reviewing the text yourself"; the concern is "the very verbose and unhelpful content that LLMs love to include."
- All-time totals in ruff are 131 `bot:ai-policy-close` and 25 `bot:ai-policy-comment`.

**Consequence for a Claude Code user**
- The agent may help write code and tests. You must understand every line and be able to explain it.
- You write the PR description, issue text and every reply yourself. Editing an agent draft is not enough, per the #30186 comment.
- The agent must not open PRs, post comments or reply on your behalf.
- Ruff ships agent skills for this workflow: `/plugin marketplace add ./.agents`, then `/plugin install ty-skills@ruff-agent-skills` (`ruff: CONTRIBUTING.md:54-66`).

## 5. Path 1: the ty repository

This path covers docs, packaging and CI.

- **Setup:** clone, then `git submodule update --init --recursive` (`CONTRIBUTING.md:34-42`). You need uv (`CONTRIBUTING.md:46-47`). Builds also need a Rust toolchain, because Maturin builds from `ruff/crates/ty/Cargo.toml` (`pyproject.toml:174-179`).
- **Your checkout:** the submodule is not initialized, so builds and `autogenerate_files.sh` fail until you run the command above.
- **Docs preview:** `uv run --only-group=docs mkdocs serve -f mkdocs.yml` (`CONTRIBUTING.md:112-119`).
- **New pages:** add them to `nav` in `mkdocs.yml`; `omitted_files: warn` fails the strict build (`mkdocs.yml:159-162`).
- **Generated files:** never hand-edit the five generated reference files. CI reruns `./scripts/autogenerate_files.sh` and fails on any diff (`.github/workflows/ci.yaml:104-131`).
- **Markdown:** mdformat, markdownlint, typos; line length 100 (`.pre-commit-config.yaml:30-44,113-117`; `.editorconfig:5-9`).
- **Checks to run before a PR** (commands are from docs and CI, not executed):
  - `uv run --only-group dev --locked prek run --all-files --show-diff-on-failure --hook-stage manual` (`ci.yaml:75-102`)
  - `./scripts/autogenerate_files.sh`, expecting no diff
  - `uv run --only-group=docs mkdocs build --strict -f mkdocs.yml` (`ci.yaml:133-149`)
- **PR form:** `## Summary` and an optional `## Notes to reviewers` (`.github/PULL_REQUEST_TEMPLATE.md:1-20`). Titles are imperative, sentence case, no prefix, for example "Document baseline support (#4897)".
- **Docs go live on release, not on merge** (`CONTRIBUTING.md:127-129`).
- **Workflow changes:** pin actions by full SHA, set `persist-credentials: false`, keep top-level permissions minimal (`ci.yaml:3-4,29,31`). The core rule is "Privileged workflows do not execute attacker-controlled code or promote attacker-controlled artifacts before review or explicit authorization" (`agents/references/repository-threat-model.md:28-29`).
- **Bug reports:** search first, then give a minimal reproduction, the command and settings, and a play.ty.dev link if possible (`.github/ISSUE_TEMPLATE/1_bug_report.yaml:9-29`).

## 6. Path 2: type-checker code in ruff

### Setup and dev loop

- **Tools:** Rust toolchain pinned to 1.100.0 (`ruff: rust-toolchain.toml:2`), uv, nextest recommended (`ruff: crates/ty/CONTRIBUTING.md:25-47`).
- **Run:** `cargo run --bin ty -- check --project /path/to/project/` (`ruff: crates/ty/CONTRIBUTING.md:54`). Use debug builds, not `--release` (`ruff: AGENTS.md:158`).
- **Where the code is:** `ty_python_semantic` holds "the vast majority of ty's code"; `ty_test` is the mdtest framework (`ruff: crates/ty/CONTRIBUTING.md:94-115`).
- **Reproductions:** keep temporary files outside the checkout. Inside it, ruff's `requires-python = ">=3.7"` makes ty assume Python 3.7 (`ruff: AGENTS.md:198`).

### Coding conventions

| Area | Rule | Cite |
| --- | --- | --- |
| `db` | "This should always be the first argument (or second after `self`)." | `ruff: crates/ty/CONTRIBUTING.md:147-149` |
| Panics | "Try hard to avoid patterns that require `panic!`, `unreachable!`, `.unwrap()` or `.expect()`. Instead, try to encode those constraints in the type system." | `ruff: AGENTS.md:232` |
| Salsa | "Methods that access `.node()` should usually be `#[salsa::tracked]`, or ty's incrementality will suffer" | `ruff: AGENTS.md:208-215` |
| Memory | For Salsa-cached values, "avoid retaining excess collection capacity. Prefer boxed slices" | `ruff: AGENTS.md:219-221` |
| File system | No `std::fs::*`, `std::env::var`, `Path::exists` in ty crates; use the `System` trait | `ruff: clippy.toml:32-47` |
| Lints | Prefer `#[expect()]` over `allow`; delete dead code | `ruff: AGENTS.md:234` |
| Control flow | Prefer let chains over nested `if let` | `ruff: AGENTS.md:233` |
| Imports | Top of file, never inside functions; narrow visibility by default | `ruff: AGENTS.md:228-229` |
| Tests | No `test_` prefix | `ruff: AGENTS.md:237` |
| Scope | "Avoid expanding the task to unrelated issues, but do not confuse keeping the task focused with minimizing the size of the implementation." | `ruff: AGENTS.md:231` |
| Diagnostics | "**Keep error messages concise.** Think about how the diagnostic will look on a narrow terminal screen." A new diagnostic needs a snapshot mdtest | `ruff: .agents/skills/adding-ty-diagnostics/SKILL.md:10,20-25` |
| New rules | "Avoid broad rules that catch many different kinds of errors" | `ruff: crates/ty/CONTRIBUTING.md:153-156` |

### Tests

| Kind | Location | Use when |
| --- | --- | --- |
| mdtest | `crates/ty_python_semantic/resources/mdtest/**.md` | Any inference or checking change |
| External-library mdtest | `resources/mdtest/external/*.md` plus `.lock` | Django, pydantic, numpy support |
| CLI integration (insta) | `crates/ty/tests/cli/*.rs` | Config, rule selection, exit codes |
| LSP e2e | `crates/ty_server/tests/e2e/*.rs` | Server requests |
| Property tests (`#[ignore]`) | `src/types/property_tests.rs` | After touching `is_subtype_of` and similar (`ruff: crates/ty/CONTRIBUTING.md:135-137`) |
| Benchmarks | `crates/ruff_benchmark` | Hangs: "Prefer microbenchmarks over tests" (`ruff: AGENTS.md:225`) |

**mdtest rules**
- Assert with `# revealed: <exact display>` and `# error: [rule-code] "substring"`. Do not import `reveal_type` (`ruff: crates/ty_test/README.md:48-51,66-69,73-90`).
- Each header section is its own test with a fresh database (`README.md:249-279`).
- Write short blocks with prose in present tense, ordered from basic to specialised. Mark intentional no-diagnostic lines with `# ok` (`ruff: AGENTS.md:124-148`).
- Put tests in the existing file for that behaviour. Mirror generic cases under `generics/legacy/` and `generics/pep695/` (same cite).
- Reviewers treat tests that already pass on the base commit as usually unnecessary (`ruff: .agents/skills/review-ty-changes/SKILL.md:167-173`).
- Known-wrong results use a `# TODO:` comment above the current assertion. This is observed practice, not a written rule (`ruff: crates/ty_python_semantic/resources/mdtest/external/django.md:54-55,75,86`).
- Never hand-edit snapshots; regenerate and review (`ruff: AGENTS.md:116-120`).

Minimal example:

````markdown
# Invalid assignment

## Same file

We reject assigning a `str` to a variable declared as `int`:

```py
x: int = "foo"  # error: [invalid-assignment]
reveal_type(1)  # revealed: Literal[1]
```

## Cross-file

```py
from b import y

x: int = y  # error: [invalid-assignment]
```

`b.py`:

```py
y = "foo"
```
````

**External-library tests**
- The header `toml` block needs `python-version`, `python-platform` and `[project] dependencies` (`django.md:5-12` pins `django-types==0.24.0`).
- The framework runs `uv sync --locked` against the sibling `.lock` file (`ruff: crates/ty_test/README.md:368-379`).
- These tests are skipped unless `MDTEST_EXTERNAL=1` (`ruff: crates/ty_test/src/lib.rs:142-143`). CI sets it (`ruff: .github/workflows/ci.yaml:36`), so green locally does not mean green in CI.
- Regenerate lockfiles with `uv run crates/ty_python_semantic/mdtest.py -e external/` (`README.md:389-400`).

### Pre-PR checklist

```bash
cargo fmt --all --check
CARGO_BUILD_WARNINGS=deny cargo clippy --workspace --all-targets --all-features
INSTA_FORCE_PASS=1 INSTA_UPDATE=always MDTEST_UPDATE_SNAPSHOTS=1 \
  cargo nextest run --workspace -E 'not binary(=file_watching)'
# one mdtest file:
#   cargo nextest run -p ty_python_semantic --test mdtest -- mdtest::<path under resources/mdtest>
# external-library mdtests (inferred: the documented lockfile command without the upgrade flag):
MDTEST_EXTERNAL=1 cargo test -p ty_python_semantic --test mdtest mdtest__external
uv run --only-dev cargo insta review          # then check for .pending-snap files
cargo dev generate-all                        # after rule, option, CLI or env-var changes
uv run --only-dev --locked prek run --all-files
```

Sources: `ruff: AGENTS.md:68,77-80,116-120,153,230,236`; `ruff: crates/ty/CONTRIBUTING.md:61-63,75`; `ruff: .github/workflows/ci.yaml:343`. None of these were executed during research.

### CI gates

"Required" means listed in `required-checks-passed` (`ruff: .github/workflows/ci.yaml:1758-1772`).

| Job | What it checks | Required |
| --- | --- | --- |
| cargo-fmt, cargo-clippy | Format; clippy with warnings denied, including the wasm target (`:343,377,390-392`) | yes |
| hawk | `cargo hawk check -D warnings` (`:425`); appears to audit dead code and visibility (inferred from `hawk.toml:1-36`) | yes |
| cargo-test-linux | insta + nextest with `--unreferenced reject`, doctests, `cargo doc -D warnings` including private items in ty crates (`:475-514`) | yes |
| cargo-test-wasm, cargo-build-msrv, cargo-deny | wasm tests; MSRV 1.98 build; licence and ban checks (`:607-644,1184-1190`) | yes |
| prek, docs, scripts, python-package | Hooks, including "mdtest format" over Python blocks (`:1309`) | yes |
| cargo-test-other (Windows, macOS), cargo-shear | (`:551-582,1204`) | no |
| fuzz-ty | New panics versus merge base (`:998-1027`) | no |
| CodSpeed benchmarks, ty-completion-evaluation | (`:1227-1229,1493,1703`) | no |

Generated docs and schema are checked by `ruff_dev` unit tests inside cargo-test-linux, which fail with "please run `cargo dev generate-all`" (`ruff: crates/ruff_dev/src/generate_ty_schema.rs:36,63-68`).

### Ecosystem, conformance and memory reports

- **Trigger:** changes under `crates/ty*/**`, excluding `**.md`, `**.snap` and the IDE, server, test and wasm crates. An mdtest-only PR gets none (`ruff: .github/workflows/ty-ecosystem-analyzer.yaml:12-37`).
- **Ecosystem:** it fails only on new panics or timeouts (`:261,297-299`). Diagnostic diffs are not a gate, but you must explain them (`ruff: CONTRIBUTING.md:434-439`).
- **How to explain a diff:** group changes by cause, show minimised examples, ignore flaky and `unknown-rule` changes, link ty issues (`ruff: .agents/skills/summarise-ecosystem-results/SKILL.md:10,32-35,43-44`). On #29305 the author's whole answer was "These are true positives."
- **Reproduce one project:** `uv run scripts/setup_primer_project.py <project> <dir>` (`ruff: crates/ty/CONTRIBUTING.md:141-143`).
- **Conformance:** it classifies results as improved or regressed and looks informational; no failing exit was found (`ruff: scripts/conformance.py:103,958-964`).
- **Memory:** it runs over flake8, sphinx, prefect and trio (`ruff: .github/workflows/memory_report.yaml:88-90,115-119`). No threshold was confirmed.

## 7. PR conventions and review

- **Title:** "Include the text `[ty]` at the beginning of your pull request title" (`ruff: crates/ty/CONTRIBUTING.md:78-79`). 690 of 730 recent ty commits follow this.
- **Merge style:** all 730 end in `(#NNNNN)` with single parents, which indicates squash merging (inference). The title becomes the commit and changelog line.
- **Template:** `## Summary` and an optional `## Notes to reviewers`, plus a checklist that includes AI-policy compliance (`ruff: .github/PULL_REQUEST_TEMPLATE.md:4-22`).
- **Summary content:** link the issue and state the problem and approach, "thorough but also succinct" (`ruff: CONTRIBUTING.md:410-423`). Describe observable behaviour before implementation (`ruff: AGENTS.md:53-59`).
- **Labels and reviewers:** a script adds the `ty` label and fixes the title prefix (`ruff: scripts/pull_request_labels_and_title.py:18-22,55-75`). Reviewers are assigned round-robin from path pools (`ruff: .github/pr-reviewer-pools.toml:10-44`). Maintainers likely set changelog labels for outsiders (inference from "If you have permission", `ruff: AGENTS.md:25`).
- **During review:** move the PR back to draft while reworking it; resolve or thumbs-up addressed comments (`ruff: CONTRIBUTING.md:443-450`).

Size and speed (ruff `origin/main`, 2026-09-01 to 2026-11-20, 710 human commits):

| Metric | Value |
| --- | --- |
| Median diff | 134 lines (quartiles 54 / 134 / 352) |
| Median files touched | 3 |
| Commits touching semantic source that also change an mdtest | 69% (385/554) |
| Outside commits (n=18) | median 145 lines, 72% with mdtest |
| Time to merge, outside PRs | Same day to 3 days for 8 of 9; 22 days for #29588 (1,212 lines) |

Reviewer checklist, condensed from `ruff: .agents/skills/review-ty-changes/SKILL.md:109-211`:

1. Motivation is sound: does it admit unsafe code or reject valid code?
2. The change agrees with runtime Python behaviour.
3. It was compared with mypy, pyright, pyrefly, pycroscope and zuban, as evidence, not proof.
4. It conforms to the typing spec, or the divergence is justified.
5. A narrower change or a different design would not serve better.
6. Salsa invalidation, panics, performance and memory growth are sound.
7. Tests cover negative and boundary cases, with no redundant tests.
8. Ecosystem impacts are assessed independently; the PR description is "claims to verify, not proof".

Maintainers often push commits to your branch. carljm on #29441: "Looks great; pushed a few minor updates. Will merge if CI still looks good." charliermarsh pushed four commits to #29125 before merging (433704ea7).

## 8. What gets PRs closed

| PR | Outcome | Reason |
| --- | --- | --- |
| #29858 (hover docstrings) | Bot-closed the day it opened | AI-written communication; no human review |
| #30186 (classmethod check) | Flagged, moved to draft | Verbose LLM-style content |
| #27415 (recursive `__call__`) | Closed after 8 weeks | Hard depth limit rejected. sharkdp: "Maybe you could do some research on existing patterns here." |
| #29394 (generic-alias narrowing) | Closed same day by carljm | "It's not clear what the best direction here is" |
| #29275 (float true division) | Declined same day | AlexWaygood: "I'd want to see a bit more motivation here before adding special-casing like this." |
| #29179 (heapq test) | Author closed | "Typeshed's stdlib stubs can change at a moment's notice" |

Stale outside PRs (#23369, #23684, #24222) were closed in October without merging.

## 9. Django-specific guidance

- **Owner:** sharkdp wrote all seven merged Django commits (30be8844b, 2fa2ecbbf, 9dfc6ee97, 005a31333, 731a26b88, 4160aece3, 19db56ae3) in 12 days.
- **Pattern to copy:** each PR is one feature, titled `[ty] Django: ...`, with "New Markdown tests" and a link to ty#1018, ty#4822 or ty#4847.
- **In flight:** draft #29731 "Switch Django support to django-stubs" (opened 2026-10-26, no activity since) and draft #30068. Current mdtests pin `django-types==0.24.0`, so work written against them may need rework.
- **What he asked for** (ty#1018, 2026-11-02): "It would help a lot to get specific feedback about what is not working yet." "This is where I need most help."
- **His planned list:** `django-stubs` as default, reverse foreign-key and one-to-one accessors, stringified lazy relationships, precise model constructor signatures.
- **Precedent:** he merged outside Pydantic PRs #29305 and #29367 within two days.
- **Status:** ty#1018 is open and unassigned, and was removed from the "ty-1.1" milestone on 2026-11-18.

Recommended sequence (inference from the evidence above):

1. File specific issues in `astral-sh/ty`, one gap each, with a minimal reproduction. This is the help he asked for.
2. Before coding anything, especially items on his list, ask on ty#1018 or the specific issue.
3. If agreed, send small single-feature PRs titled `[ty] Django: ...`, with mdtests in `external/django.md`. Run them with `MDTEST_EXTERNAL=1` and verify assertions against Django's runtime behaviour, as #29642 did.
4. Check the state of #29731 before starting and again before opening.

## 10. Common pitfalls

1. Opening a code PR in `astral-sh/ty`, or an issue in ruff.
2. Letting an agent write the PR body or replies.
3. Building a feature, or a fix for a `needs-design` issue, without prior agreement.
4. Adding a narrow special case without motivation from real code (#29275).
5. Hand-editing snapshots or generated reference docs.
6. Forgetting `cargo dev generate-all` after rule, option, CLI or env-var changes.
7. Skipping `MDTEST_EXTERNAL=1`, so external tests are silently skipped locally.
8. Repro files inside the checkout running as Python 3.7.
9. Using `std::fs` or `Path::exists` in ty crates, or std APIs newer than MSRV 1.98.
10. Leaving orphaned `.snap` files; `--unreferenced reject` fails CI (`ruff: ci.yaml:475`).
11. Tests that depend on typeshed stdlib stub details (#29179), or that already pass on the base.
12. Not explaining the ecosystem report, or claiming the PR closes an issue it only partly fixes (#29293).

## 11. Conflicts and stale docs found

- **Test plan.** `ruff: CONTRIBUTING.md:405-406` says the template has "the summary and the test plan"; the template has no such section. Merged PRs still use `## Test Plan`. The ty repo removed it in c2e9b05. Including a short test plan matches practice.
- **Considered alternatives.** `ruff: CONTRIBUTING.md:412` says they "can also be helpful to include"; `ruff: AGENTS.md:57` says to omit discarded alternatives unless the reader needs them. Not resolved.
- **`good first issue`.** `ruff: CONTRIBUTING.md:12-23` recommends it; zero exist in `astral-sh/ty`.
- **`help wanted` meaning.** The ty guide calls it "beginner-friendly tasks" (`ruff: crates/ty/CONTRIBUTING.md:19-21`); the label description is "Contributions especially welcome".
- **Report comments on fork PRs.** The workflows publish comments only for same-repo branches (`ruff: ty-ecosystem-analyzer.yaml:303-306`), yet outside PR #29305 received bot report comments. A separate `publish-pull-request-report.yml` may explain this; it was not traced. Check the job summary if no comment appears.
- **Property tests "run once daily".** No such workflow was found in ruff. It lives in the ty repo: `.github/workflows/daily_property_tests.yml:7-9`, against ruff `main`. This one is resolved.
- **Stale prettier instruction.** `CONTRIBUTING.md:131-135` says to run prettier on Markdown; hooks run prettier on YAML only and mdformat on Markdown (`.pre-commit-config.yaml:30-38,50-52`).
- **Missing file.** `CONTRIBUTING.md:121-125` references `docs/requirements.in`, which does not exist.
- **Minor ty-repo leftovers.** `ci.yaml:60` uses an undefined `env.PYTHON_VERSION`; `ci.yaml:98` skips hooks that do not exist here; `scripts/autogenerate_files.sh:7` misnames itself.
- **Crate list.** `ty_python_core`, `ty_site_packages` and `ty_completion_bench` exist but are missing from the ty guide.

## 12. Open questions and unverified points

- Branch-protection rules and required approvals in both repos are not visible in files.
- Squash merging is inferred from commit shape, not from settings.
- The AI-policy action's exact behaviour, and how to get a bot-closed PR reopened, are unknown.
- What dispatches the label, reviewer and AI-policy workflows is unknown; all are `workflow_dispatch` only.
- CodSpeed and memory-report thresholds are unknown, as is whether the conformance job can fail.
- hawk's purpose is inferred; local ty benchmark flags are unverified.
- Whether outside Django PRs are welcome has not been stated by any maintainer.
- Core-team membership is inferred from commit volume. `lerebear` shows as `CONTRIBUTOR` but merges PRs and is in the reviewer pools.
- Inline review threads on several PRs, and 19 collapsed items on ty#1018, were not readable.
- Whether maintainers answer in a ty Discord channel is unverified; Discussions were not checked.
- No written PR-size limit, commit-message convention, DCO or CLA was found.
- `ruff: docs/rule-proposals.md` and the `triage-ty-issue` skill were not read.
- No commands were executed; all are taken from docs and CI.

## 13. Sources

**ty repo (`/home/user/ty`)**
- `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `SECURITY.md`, `pyproject.toml`, `mkdocs.yml`
- `agents/references/repository-threat-model.md`
- `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/*`
- `.github/workflows/{ci.yaml,ai-policy.yml,daily_property_tests.yml}`
- `.pre-commit-config.yaml`, `.editorconfig`
- `scripts/{autogenerate_files.sh,generate_ty_extensions_docs.py}`
- Commits c2e9b05 and 5ad2863

**ruff at 0528644c0**
- `crates/ty/CONTRIBUTING.md`, `CONTRIBUTING.md`, `AGENTS.md`
- `crates/ty_test/README.md`, `crates/ty_test/src/lib.rs`
- `crates/ty_python_semantic/resources/mdtest/external/django.md`
- `.github/PULL_REQUEST_TEMPLATE.md`, `.github/pr-reviewer-pools.toml`, `.github/CODEOWNERS`
- `.github/workflows/{ci.yaml,ty-ecosystem-analyzer.yaml,typing_conformance.yaml,memory_report.yaml,ai-policy.yml}`
- `.agents/skills/{review-ty-changes,adding-ty-diagnostics,summarise-ecosystem-results,minimizing-ty-ecosystem-changes}/SKILL.md`
- `scripts/{pull_request_labels_and_title.py,pull_request_reviewers.py,conformance.py,setup_primer_project.py}`
- `clippy.toml`, `Cargo.toml`, `rust-toolchain.toml`, `hawk.toml`, `crates/ruff_dev/src/generate_*.rs`
- `git log origin/main --since=2026-09-01 -- 'crates/ty*'`

**Web**
- https://raw.githubusercontent.com/astral-sh/.github/main/AI_POLICY.md
- https://github.com/astral-sh/ruff/pull/ followed by 29588, 29305, 29293, 29441, 29125, 29275, 29394, 29179, 27415, 29858, 30186, 29731, 30068, 29642
- https://github.com/astral-sh/ty/issues/1018
- https://github.com/astral-sh/ty/labels
- https://github.com/astral-sh/ty/contribute

## TL;DR

Code goes to `astral-sh/ruff` with a `[ty]` title, mdtests and a description you wrote yourself; issues and docs go to `astral-sh/ty`. For Django, file specific issues and ask on ty#1018 before writing code, because sharkdp is mid-switch to `django-stubs`.
