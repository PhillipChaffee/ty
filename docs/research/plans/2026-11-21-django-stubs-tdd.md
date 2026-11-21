# ty Django support on unreleased django-stubs: TDD implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ty's Django tests pass on unreleased django-stubs, one behaviour per branch, test
first, and rank the remaining gaps by running ty on a large private Django repository.

**Architecture:** A stack of small branches in the ruff fork on top of
`phillip/django-stubs-unreleased`, whose 24 failing assertions are the red tests. The maintainer's
draft commit is cherry-picked with his authorship for the foreign-key work; our fixes are separate
commits. A harness measures the private repository before and after the stack.

**Tech stack:** Rust (ruff `crates/ty_python_semantic`), mdtest (Markdown tests), `uv`, Python,
Django, django-stubs at `44457d47e03845c27b560936ef0455d5dfc7b7d8`.

**Spec:** `docs/research/django-stubs-switch.md` and `docs/research/django-stubs-switch-evidence/`
on this branch. Rules: `docs/research/django-contribution-guidelines.md`. Terms:
`docs/research/ty-glossary.md`.

## Global constraints

- Ruff work happens in `/home/user/ruff` (fork `PhillipChaffee/ruff`). Never push to `astral-sh`.
  Never open a pull request or write issue or pull request text; a person does that.
- Commits are authored as Phillip, with the address already set in each clone's git config. No
  agent attribution lines on ruff branches. Cherry-picked commits keep their original author.
- `/home/user/ruff` is a shallow clone. Never run `git fetch --depth` on one of our own branches
  and then amend; that produced a parentless commit once. After a push, record the remote with
  `git update-ref refs/remotes/origin/<branch> HEAD`.
- One behaviour per branch. No unrelated cleanup. Never hand-edit a lock file or snapshot. Never
  skip or delete a failing test; a gap we are not fixing becomes a `# TODO:` line that asserts
  today's result.
- **Privacy.** The Django repository used for measurement is private, and both forks are public.
  Nothing from it goes into git or into any message to an outside service: no repository name, no
  source, no file paths, no identifiers, no dependency list, no raw diagnostics. Only counts per
  rule and hand-minimised reproductions with invented names (`Book`, `Author`, `Review`). Raw
  output stays in the session scratchpad. It is called **the private repository** below.
- Test line numbers below are in `crates/ty_python_semantic/resources/mdtest/external/django.md`
  at commit `9cdccf6`.
- The test runner needs `uv` 0.13 or newer first on `PATH`.
- Django test command, called **DJANGO-TEST** below:
  `MDTEST_EXTERNAL=1 cargo test -p ty_python_semantic --test mdtest -- mdtest::external/django.md`
- Branch checks, called **CHECKS** below, all required before a push:
  `cargo fmt --all --check`;
  `CARGO_BUILD_WARNINGS=deny cargo clippy --workspace --all-targets --all-features`;
  `MDTEST_EXTERNAL=1 cargo test -p ty_python_semantic`;
  `uv run --only-dev --locked prek run --files <every changed file>`.

## Review focus

1. A foreign key whose target is a string (`"Author"`, `"self"`) with `null=True` must keep
   `| None` in its type. Test in Task 4.
2. A user-defined subclass of `ForeignKey` must behave like `ForeignKey`. Test in Task 5.
3. Projects that still have django-types installed must not get worse. Check in Task 8.
4. The constructor special case must not change results for non-Django code. Covered by the full
   crate test run in CHECKS; confirm zero non-Django diagnostic changes in Task 8.
5. Released django-stubs 6.1.2 gives `Unknown` fields. We do not fix that; Task 8 records the
   numbers so nobody mistakes it for a regression.

---

### Task 1: Get a checkout of the private repository

**Files:** none in git. Checkout at `$SCRATCH/private-repo`, where `$SCRATCH` is the session
scratchpad.

- [ ] **Step 1:** Ask Phillip which route to use: (a) a read-only access token for the git host,
  entered through the session's credential form, then a `--depth 1` clone into
  `$SCRATCH/private-repo`; or (b) attach the folder from his computer and run the harness there.
- [ ] **Step 2:** Read the project's dependency file and type-checker configuration from the
  checkout. Note, in the scratchpad only: the Python version, the Django version, the source
  root, the paths its current type checker excludes, which stub packages it installs, and which
  dependencies come from private package sources.
- [ ] **Step 3:** Verify: the source root contains `manage.py` or a settings module.

### Task 2: Measurement harness

**Files (ty fork, this branch):**
- Create: `docs/research/harness/make_env.sh`
- Create: `docs/research/harness/run_ty.sh`
- Create: `docs/research/harness/summarize.py`
- Create: `docs/research/harness/census.py`
- Create: `docs/research/private-repo-baseline.md` (counts only)

**Interfaces (produces):**
- `make_env.sh <repo-dir> <name> <stub-requirement> <skip-list-file>` creates
  `$SCRATCH/envs/<name>` with the Python version the project pins and its locked public
  dependencies, minus every Django-related stub package and minus the packages named in
  `<skip-list-file>` (the private ones, listed in a scratchpad file), plus `<stub-requirement>`.
- `run_ty.sh <ty-binary> <env-name> <label> <source-root> <exclude-glob>` runs
  `<ty-binary> check <source-root> --python $SCRATCH/envs/<env-name> --exclude <exclude-glob> --output-format concise`
  from the repository directory and writes `$SCRATCH/runs/<label>.txt`.
- `summarize.py <label> [<baseline-label>]` prints a Markdown table: diagnostics per rule, and for
  `missing-attribute` the counts per attribute-name shape (`*_set`, `*_id`, `*_ptr`,
  `get_*_display`, `objects`, other). With a baseline it adds a delta column. It never prints a
  file path, an identifier from the repository, or source text.
- `census.py <repo-dir> <source-root> <exclude-glob>` prints counts of Django features used, by
  regex: `ForeignKey(`/`OneToOneField(` with a class target, with a string target, with `"self"`;
  `related_name=`; `ManyToManyField(`; `through=`; `objects = ` custom managers; `.as_manager()`;
  `from_queryset(`; `.values(`; `.values_list(`; `.annotate(`; `get_user_model(`; `request.user`;
  `settings.`; `TextChoices`/`IntegerChoices`; `parent_link=`; `abstract = True`; `proxy = True`.

- [ ] **Step 1:** Write the four scripts with the interfaces above.
- [ ] **Step 2:** Build three environments: `types` (`django-types==0.24.0`), `stubs612`
  (`django-stubs==6.1.2`), `stubs`
  (`django-stubs @ git+https://github.com/typeddjango/django-stubs.git@44457d47e03845c27b560936ef0455d5dfc7b7d8`).
  Expected: each `uv pip list` shows the project's Django version and exactly one Django stub
  package. If a stub package forces a different Django or Python version, record that as a
  finding and keep going.
- [ ] **Step 3:** Build ty from ruff `origin/main` (`cargo build --bin ty`), copy to
  `$SCRATCH/bin/ty-main`. Run labels `main-types`, `main-stubs612`, `main-stubs`.
- [ ] **Step 4:** If the project's own type-checker setup installs without the private packages,
  run it once and record its error count per code as the reference. If it does not, write that
  down and skip.
- [ ] **Step 5:** Write `private-repo-baseline.md`: the three summary tables, the census, and the
  count of `unresolved-import` diagnostics caused by the skipped private packages (reported
  separately, excluded from every other number).
- [ ] **Step 6:** Verify privacy: `grep -c -E '\.py|/' docs/research/private-repo-baseline.md`
  counts only lines that are part of this plan's own vocabulary; read the file once in full and
  confirm it holds no path, name or identifier from the repository. Commit and push this branch.

### Task 3: Fix reading of literal keyword arguments

**Branch:** `phillip/stubs-01-literal-metadata` from `phillip/django-stubs-unreleased`.

**Files:**
- Modify: `crates/ty_python_semantic/src/types/dedicated/django.rs:79-94`
- Test: `django.md:415-416` (already failing)

- [ ] **Step 1:** Run DJANGO-TEST. Expected: lines 415 and 416 report
  `unmatched assertion: error: [missing-attribute]`.
- [ ] **Step 2:** In `Field::from_definition`, replace the two `== Type::bool_literal(true)`
  comparisons (`primary_key`, `null`) with `.as_bool_literal() == Some(true)`. Do not touch the
  `abstract` comparison at line 200; it reads a binding, not a call argument.
- [ ] **Step 3:** Run DJANGO-TEST. Expected: 415 and 416 no longer listed; 22 lines still fail.
- [ ] **Step 4:** Run CHECKS, commit as
  `[ty] Django: read literal field arguments regardless of promotion`, push.

### Task 4: Infer the target model of a foreign key

**Branch:** `phillip/stubs-02-foreign-key-target` from Task 3's branch.

**Files:**
- Modify: `crates/ty_python_semantic/src/types/dedicated/django.rs`
- Modify: `crates/ty_python_semantic/src/types/call/bind/constructor.rs` (near line 504)
- Modify: `crates/ty_python_semantic/src/types/call/bind.rs:9791`
- Test: `django.md`

**Interfaces (produces):**
`pub(in crate::types) fn foreign_key_model_type<'db>(db: &'db dyn Db, env: &ProgramEnvironment<'db>, binding: &Binding<'db>) -> Option<Type<'db>>`
in `django.rs`. It returns the instance type of the `to` argument, unioned with `None` when the
`null` argument is the literal `True`.

- [ ] **Step 1:** Fetch the maintainer's commit from the public upstream repository
  (`git fetch https://github.com/astral-sh/ruff 8c694178fe`; take the full hash from
  `docs/research/django-stubs-switch-evidence/S1-code-and-draft-pr.md`), then cherry-pick it.
  Resolve conflicts exactly as
  `docs/research/django-stubs-switch-evidence/merge-resolution.patch` does: keep main's imports
  and add `use crate::types::call::Binding;`; in `constructor.rs` use `class_literal` where the
  draft says `static_class_literal`; give `foreign_key_id_type` a
  `class: StaticClassLiteral<'db>` parameter and pass it from both callers. Keep the original
  author on the commit.
- [ ] **Step 2:** In `foreign_key_model_type`, use `.as_bool_literal() == Some(true)` for `null`
  (separate commit, ours).
- [ ] **Step 3:** Add a failing test under `## Foreign key IDs`, new subsection
  `### String references`, verified against Django at runtime first:

```py
from django.db import models

class Author(models.Model):
    pass

class Book(models.Model):
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    editor = models.ForeignKey("Author", null=True, on_delete=models.SET_NULL)

def _(book: Book):
    # TODO: Should be `Author`.
    reveal_type(book.author)  # revealed: Any
    # TODO: Should be `Author | None`.
    reveal_type(book.editor)  # revealed: Any | None
```

- [ ] **Step 4:** Run DJANGO-TEST; `book.editor` reveals `Any`. Make `foreign_key_model_type`
  return `Any | None` for a string target with `null=True` so the test passes. Resolving the
  string itself is out of scope.
- [ ] **Step 5:** Run DJANGO-TEST. Expected fixed: 241, 242, 243, 265, 266, 267, 288, 289, 291,
  292, 295, 336, 338, 357, 359. Expected still failing: 57, 236, 237, 238, 261, 262, 263. If the
  set differs, stop and record the difference before changing anything.
- [ ] **Step 6:** Run CHECKS, push.

### Task 5: Treat subclasses of `ForeignKey` the same way

**Branch:** `phillip/stubs-03-relation-subclasses` from Task 4's branch.

**Files:**
- Modify: `crates/ty_python_semantic/src/types/call/bind/constructor.rs` (the special case from
  Task 4)
- Test: `django.md:236-238, 261-263` (already failing)

- [ ] **Step 1:** Add a failing test in `### Automatic primary key` under `## Foreign key IDs`:

```py
class TrackedForeignKey(models.ForeignKey):
    pass

class Chapter(models.Model):
    book = TrackedForeignKey(Book, on_delete=models.CASCADE)

def _(chapter: Chapter):
    reveal_type(chapter.book)  # revealed: Book
```

  If ty rejects the unparameterised base class, declare it as
  `class TrackedForeignKey(models.ForeignKey[Book, Book])` and say so in the commit message.
- [ ] **Step 2:** Run DJANGO-TEST; the new line and 236-238, 261-263 fail.
- [ ] **Step 3:** Replace the exact `is_known(db, KnownClass::DjangoForeignKey)` test with a scan
  of the class's MRO for `KnownClass::DjangoForeignKey`.
- [ ] **Step 4:** Run DJANGO-TEST. Expected still failing: line 57 only.
- [ ] **Step 5:** Run CHECKS, commit as `[ty] Django: infer targets for ForeignKey subclasses`,
  push.

### Task 6: Accept the date-string assignment

**Branch:** `phillip/stubs-04-date-string` from Task 5's branch.

**Files:**
- Modify: `django.md:56-57`

- [ ] **Step 1:** Confirm at runtime that Django accepts `book.published = "1980-10-12"`.
- [ ] **Step 2:** Delete the
  `# TODO: django-types should allow ISO-formatted date strings as input.` line and the
  `# error: [invalid-assignment]` comment; keep the assignment.
- [ ] **Step 3:** Run DJANGO-TEST. Expected: `1 passed`.
- [ ] **Step 4:** Run CHECKS, commit as
  `[ty] Django: accept ISO date strings for date fields with django-stubs`, push.

### Task 7: Turn the private repository's top gaps into tests

**Branch:** `phillip/stubs-05-gap-tests` from Task 6's branch. Fork-only; test-only changes are
not sent upstream.

**Files:**
- Modify: `django.md` (new `##` sections at the end, before the link line)

- [ ] **Step 1:** Build ty from Task 6's branch as `$SCRATCH/bin/ty-stack`; run label
  `stack-stubs`; run `summarize.py stack-stubs main-stubs` and
  `summarize.py stack-stubs main-types`.
- [ ] **Step 2:** From the summary and the census, list the gap categories by diagnostic count,
  then by census count for gaps that produce no diagnostic. Take the top eight.
- [ ] **Step 3:** For each, write a minimal model with invented names, confirm the behaviour
  against Django at runtime, and add it to `django.md` as `# TODO:` lines that assert today's
  result, using the glossary's terms for section titles.
- [ ] **Step 4:** Run DJANGO-TEST (`1 passed`), CHECKS, push. Append the ranked list, with counts
  only, to `docs/research/private-repo-baseline.md` and push the ty fork branch.

### Task 8: Regression report

**Files:**
- Create: `docs/research/stubs-stack-report.md` (ty fork, this branch)

- [ ] **Step 1:** Run labels `stack-types` and `stack-stubs612` with `ty-stack`.
- [ ] **Step 2:** Run DJANGO-TEST on Task 6's branch three times with the test header pinned to
  `django-types==0.24.0`, `django-stubs==6.1.2` and the unreleased commit, in a scratch worktree,
  regenerating the lock each time with `MDTEST_UPGRADE_LOCKFILES=1`. Record passing and failing
  assertion counts. Do not commit those header changes.
- [ ] **Step 3:** Write the report: per branch, assertions fixed; private-repository diagnostics
  per rule for `main-*` against `stack-*`; any diagnostic rule whose count rises under
  `stack-types` compared with `main-types` (expected: none); the count of non-Django diagnostics
  changed (expected: 0).
- [ ] **Step 4:** Verify privacy as in Task 2 Step 6. Commit and push.

### Task 9: Decide what goes upstream (Phillip)

- [ ] **Step 1:** Read `stubs-stack-report.md` and the branch diffs.
- [ ] **Step 2:** File an issue in astral-sh/ty for the literal-argument bug (Task 3), in your own
  words, with the minimal example from `django.md:398-416` and the note that it needs unreleased
  django-stubs to reproduce.
- [ ] **Step 3:** Tell the maintainer on astral-sh/ruff#29731 or astral-sh/ty#1018 what was
  measured (the report's facts) and ask how he wants help: findings only, a rebase of his draft,
  or separate pull requests.
- [ ] **Step 4:** Tell the agent which branches to reshape for upstream, if any. Until then every
  branch in this plan is a draft on the fork.
