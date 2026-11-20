# Guidelines for our ty Django contributions

Working rules for changes we make toward closing ty's Django gaps. Derived from three research
reports in this directory, dated 2026-11-20:

- `ty-vs-mypy-django.md`: what the gaps are
- `contributing-to-ty.md`: how the two repositories and their CI work
- `ty-django-pr-expectations.md`: what maintainers accept and decline

Evidence and citations live in those reports. This file only states the rules. Keep it out of any
upstream pull request; it is our own working document.

Words used here: **must** is a rule taken from Astral's written policy or CI. **Should** is our
own practice based on what has merged and what has been closed.

## 1. Ground rules

1. Type-checker code goes to `astral-sh/ruff` (crates `ty*`). Issues go to `astral-sh/ty`. Docs
   and packaging go to `astral-sh/ty`. This checkout is the docs and packaging repository.
2. One Django behaviour per pull request. Never bundle.
3. No code before agreement. Every change starts from an issue, and anything beyond a small bug
   fix needs a maintainer's go-ahead on that issue or on
   [astral-sh/ty#1018](https://github.com/astral-sh/ty/issues/1018).
4. The Django area has an owner (sharkdp). We fit around his work and his open drafts, and we do
   not compete with them.
5. A person writes every word that maintainers read. See section 2.
6. If a fix can live in the stubs (django-stubs), it goes there, not into ty.

## 2. Who does what: people and the coding agent

Astral's AI policy applies to us as outside contributors. Pull requests that break it are closed
by a bot, sometimes within the day and without human review.

| Task | Coding agent | Person |
|---|---|---|
| Explore code, explain how something works | Yes | Reads and understands the result |
| Draft Rust changes and mdtests | Yes | Must review every line and be able to explain it unaided |
| Run builds, tests, linters; minimise reproductions | Yes | Checks the results |
| Draft notes for our own use (this directory) | Yes | |
| Issue text in `astral-sh/ty` | No | Must write it personally |
| Pull request title and description | No | Must write it personally |
| Replies to reviewers, review comments | No | Must write them personally |
| Opening a pull request, pushing to an upstream PR branch, commenting upstream | No | Must do it personally |
| Explaining the ecosystem report | No | Must write it personally |

Rules that follow from the policy:

- The agent must never open, comment on, or reply in an upstream issue or pull request.
- Editing an agent's draft of a description is not enough. Write it from scratch in your own
  words. Keep it short; long, padded text is what gets flagged.
- If you include any AI-produced context in a comment, put it in a `>` quote block, say that it
  is AI output, and keep it brief.
- If you cannot explain a change without the agent's help, it is not ready to submit.
- Commits pushed to an upstream PR branch should not carry agent attribution lines unless you
  have decided to disclose them; the policy cares about communication, but do not let an agent
  author the commit message that becomes the squash title either.

## 3. Choosing what to work on

Current status of each gap. Recheck before starting; this goes stale quickly.

| Gap | Status | Our action |
|---|---|---|
| Multi-table `<parent>_ptr` | Fits the existing pattern; nobody has claimed it | First candidate. File issue, ask, then build |
| M2M `through` (class passed as object) | Fits the pattern; shares foreign-key plumbing with the stubs switch | Wait for the django-stubs switch, then ask |
| `name=` field renames | Partly fits; hiding the original attribute needs restructuring | Ask first |
| Per-model `DoesNotExist` | Mostly fits; low value | Low priority |
| `instance.pk = None` | Maintainer draft [astral-sh/ruff#30068](https://github.com/astral-sh/ruff/pull/30068) | Do not touch |
| String references in the same module, `"self"` | On the maintainer's list; overlaps draft [astral-sh/ruff#29731](https://github.com/astral-sh/ruff/pull/29731) | Coordinate; do not start alone |
| Constructor and `create()` keyword checks | On the maintainer's list | Coordinate; do not start alone |
| Reverse relations, `related_name`, `<model>_set` | On the list; needs a project-wide design | Issue and design discussion only |
| `"app.Model"` references | Needs an app registry | Issue and design discussion only |
| `filter()` lookup validation | No stated position | Issue only |
| `values()`, `values_list()`, `annotate()` shapes | No stated position | Issue only |
| Unannotated custom managers, `as_manager()`, `from_queryset()` | Looks like a stubs or general-inference matter | Report as an issue; consider a django-stubs fix |
| Settings types, `AUTH_USER_MODEL`, `get_user_model()`, `DEFAULT_AUTO_FIELD` | Needs settings knowledge; options were declined for pydantic | Issue only; do not build |
| `request.user` narrowing | Closed as a general narrowing duplicate | Not ours |

Selection rules:

- Should prefer gaps that remove a false positive over gaps that add precision.
- Should prefer gaps that fit the existing synthesized-member pattern.
- Must not open a pull request on an issue labelled `needs-decision` or `needs-design`.
- Must check for an open pull request on the same issue before starting and again before opening.
- Must not send test-only or parity-list pull requests.

## 4. Workflow for one change

1. **Reproduce.** Write a minimal Django model that shows the gap. Run it with the released ty
   and with real Django so you know the runtime truth. Keep the file outside the ruff checkout
   (inside it, ty assumes Python 3.7).
2. **Search.** Look for an existing issue and any linked pull requests in `astral-sh/ty` and
   `astral-sh/ruff`.
3. **File the issue** in `astral-sh/ty`, one gap per issue, written by a person: what you ran,
   what ty reported, what Django does, the ty version, and a playground link if possible.
4. **Ask.** On the issue or on ty#1018, say which gap you would like to take and ask whether to
   wait for the django-stubs switch. Wait for an answer.
5. **Check the stubs.** If the right fix is a stub change, take it to django-stubs and stop here.
6. **Sync.** Work on current ruff `main`, not the commit this repository pins. Check the state of
   drafts #29731 and #30068 and which stub package the Django tests pin today.
7. **Write the test first.** Add the mdtest section and confirm it fails without your change.
8. **Implement** following section 5.
9. **Run the checks** in section 7.
10. **Open the pull request** as a person, following section 8. Explain the ecosystem report once
    the bot posts it.
11. **Review.** Move to draft while reworking. Expect maintainers to push commits to your branch.
    Answer in your own words.
12. **After merge,** offer a separate docs update to `astral-sh/ty` for the Django page
    (section 9).

## 5. Code rules (ruff, `ty*` crates)

Django-specific pattern, from the existing module
(`crates/ty_python_semantic/src/types/dedicated/django.rs`):

- Must extend the name pre-filter in `synthesized_member` first. No type work may run before it;
  that function is reached for every undefined-member lookup on every class.
- Must keep per-model work in Salsa-tracked queries. Field metadata is per class, own body only;
  handle inheritance by walking the MRO and querying each base.
- Must return `None` when information is missing or an argument is not a literal. Never guess.
- Must let user declarations win over synthesis.
- Should build synthesized types from the stub types (look up the stub class and approximate it)
  and not hardcode `int`, `str` and so on.
- Should put behaviour that is not member lookup at the one relevant engine site behind a narrow
  `django::` predicate.
- Must not add foreign-key special-casing in the constructor binding; that code is slated for
  removal.
- Must not read settings, import or run user code, add a configuration option, or add anything
  plugin-shaped.
- Should write comments that state the Django runtime fact being modelled. Doc comments should
  carry a short Python example.

General ty rules:

| Rule | Level |
|---|---|
| `db` is the first parameter (second after `self`) | Must |
| Avoid `panic!`, `unreachable!`, `.unwrap()`, `.expect()`; encode the constraint in types | Must |
| No `std::fs`, `std::env::var`, `Path::exists` in ty crates; use the `System` trait | Must (clippy) |
| Methods that access `.node()` are `#[salsa::tracked]` | Should |
| No spare capacity in Salsa-cached collections; prefer boxed slices | Should |
| `#[expect(...)]` over `#[allow(...)]`; delete dead code | Should |
| Let chains over nested `if let` | Should |
| Imports at the top of the file; narrowest visibility that works | Should |
| No `test_` prefix on tests | Must |
| No std APIs newer than the workspace minimum Rust version (1.98 at the time of writing) | Must (CI) |
| Stay on the task; do not fix unrelated things in the same change | Must |

New diagnostics (only with prior agreement):

- Keep the message short enough for a narrow terminal; put detail in sub-diagnostics.
- Prefer a narrow rule to a broad one. Name it so `# ty: ignore[rule-name]` reads naturally.
- Add at least one snapshot mdtest and run `cargo dev generate-all`.

## 6. Test rules

- Must add mdtests for any change to inference or checking. For Django they go in
  `crates/ty_python_semantic/resources/mdtest/external/django.md`, as a new `##` or `###` section.
- Each section should open with one or two sentences on Django's runtime behaviour, in present
  tense ("We infer ..."), followed by a short self-contained `py` block.
- Must verify every assertion against real Django at runtime, and say so in the test plan.
- Should cover: the basic case, a nullable variant, a subclass, a user-declared override, a
  renamed field where relevant, and at least one negative case
  (`# error: [missing-attribute]`).
- Known gaps you are not fixing stay as `# TODO:` lines that assert today's wrong result. Do not
  delete or skip them.
- Use `# revealed: <type>` and `# error: [rule-code]`. Do not import `reveal_type`. Mark lines
  that exist to prove silence with `# ok`.
- Must not add tests that already pass before the change, or tests that depend on stub internals
  likely to change.
- Must not hand-edit snapshots. Regenerate, review the diff, and look for `.pending-snap` files.
- Must run the Django tests with `MDTEST_EXTERNAL=1`. Without it they are silently skipped and a
  green local run means nothing.
- Only touch `django.lock` if dependencies change, and regenerate it with the documented command.

## 7. Checks before opening a pull request

Run from the ruff checkout. These are taken from ruff's docs and CI; confirm against current
`main`.

```bash
cargo fmt --all --check
```

```bash
CARGO_BUILD_WARNINGS=deny cargo clippy --workspace --all-targets --all-features
```

```bash
MDTEST_EXTERNAL=1 cargo nextest run -p ty_python_semantic --test mdtest -- mdtest::external/django.md
```

```bash
INSTA_FORCE_PASS=1 INSTA_UPDATE=always MDTEST_UPDATE_SNAPSHOTS=1 cargo nextest run --workspace -E 'not binary(=file_watching)'
```

```bash
uv run --only-dev cargo insta review
```

```bash
cargo dev generate-all
```

```bash
uv run --only-dev --locked prek run --all-files
```

Also:

- [ ] Rebased on current `main`; no conflict with drafts #29731 and #30068.
- [ ] The new mdtest fails without the change and passes with it.
- [ ] Run the debug build on the reproduction file and on a real Django project; no new false
      positives.
- [ ] No orphaned `.snap` files.
- [ ] `cargo dev generate-all` produced no unexpected diff.

## 8. Pull request rules

- Title must start with `[ty]`. For this work use `[ty] Django: <imperative verb> ...`. The title
  becomes the squash commit and the changelog line, so make it describe the user-visible effect.
- Body: a short `## Summary` (the problem, then the behaviour after the change), a minimal Python
  example with expected types in comments, the issue link ("Towards astral-sh/ty#1018" or
  "closes astral-sh/ty#NNNN"), and a brief `## Test Plan` ("New Markdown tests, checked against
  Django's runtime behaviour"). Tick the AI-policy line in the template honestly.
- Say plainly if the change only partly fixes the issue.
- Where behaviour is a judgement call, state what mypy and pyrefly do.
- Aim for the size that merges: roughly 50 to 350 changed lines, tests included.
- Must not include docs, changelog, unrelated refactors, or drive-by fixes.
- When the ecosystem, conformance and memory reports arrive, read them and write a short
  explanation of every diagnostic change, grouped by cause. Any memory growth needs a reason.
- Do not apply labels; maintainers and automation handle them.

## 9. Changes to this repository (`astral-sh/ty`)

For docs follow-ups and anything else that belongs here:

- Initialise the submodule first: `git submodule update --init --recursive`.
- Never hand-edit the generated reference pages (`docs/reference/cli.md`, `configuration.md`,
  `rules.md`, `environment.md`, `ty-extensions.md`). They come from the ruff sources.
- The Django page is `docs/features/third-party/django.md`. Lead with supported features; keep
  the limitations list short. Use sentence-case headings.
- New pages must be added to `nav` in `mkdocs.yml`, or the strict docs build fails.
- Run before opening:

```bash
uv run --only-group dev --locked prek run --all-files --show-diff-on-failure --hook-stage manual
```

```bash
./scripts/autogenerate_files.sh
```

```bash
uv run --only-group=docs mkdocs build --strict -f mkdocs.yml
```

- Titles here are imperative, sentence case, with no prefix. The template has `## Summary` and an
  optional `## Notes to reviewers`.
- Docs go live at the next release, not on merge.
- Workflow or release-tooling changes follow the repository threat model
  (`agents/references/repository-threat-model.md`): actions pinned by full SHA, minimal
  permissions, no attacker-controlled code in privileged jobs.
- Note for our fork: files under `docs/` that are not in `nav` (including this directory) will
  trip the strict docs build. Do not include them in a branch meant for upstream.

## 10. Never do

- Open a pull request for a new capability without prior agreement.
- Bundle more than one behaviour, or add unrelated cleanup.
- Add a plugin mechanism, a configuration option, settings reading, or runtime introspection.
- Special-case something the stubs can express.
- Duplicate or collide with the maintainer's open drafts.
- Let an agent write or post anything maintainers will read.
- Hand-edit snapshots or generated files.
- Skip, disable, or delete a failing test to get CI green.
- Claim a pull request closes an issue it only partly fixes.
- Leave the ecosystem report unexplained.

## 11. Keep this file current

Recheck these before each new piece of work, and update the table in section 3:

- Has the django-stubs switch (#29731) merged, and which stub package do the tests pin?
- Has anything changed on ty#1018 (new plans, a request to wait, a parity list)?
- Has the maintainer said whether outside Django pull requests are welcome? As of 2026-11-20 this
  is not stated either way.
- Have the commands in section 7 changed in ruff's `AGENTS.md` or `crates/ty/CONTRIBUTING.md`?
