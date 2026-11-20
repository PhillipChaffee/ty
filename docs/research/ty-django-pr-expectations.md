# What Astral would want (and not want) in a PR that closes ty's Django gaps

Research date: 2026-11-20. Local working artifact; not meant to be committed.
Companion to `ty-vs-mypy-django.md` (the gaps) and `contributing-to-ty.md` (the process).

Cites of the form `django.rs:N` and `django.md:N` are in astral-sh/ruff at `0528644c0`:
`crates/ty_python_semantic/src/types/dedicated/django.rs` and
`crates/ty_python_semantic/resources/mdtest/external/django.md`.

## Summary

There is no single "PR that fixes the gaps" that would be accepted. Every Django change merged so
far is one Django behaviour per PR, 12 to 210 lines of Rust plus an mdtest section of similar
size, written by the maintainer (sharkdp). The gaps split into three groups: a few that fit the
existing pattern, several that need a design discussion first, and some that belong upstream in
django-stubs. The maintainer is mid-switch from `django-types` to `django-stubs` and is deferring
fixes until that lands, so coordinate on
[astral-sh/ty#1018](https://github.com/astral-sh/ty/issues/1018) before writing code.

No outside Django PR has been merged yet. The one substantial outside attempt
([astral-sh/ruff#24388](https://github.com/astral-sh/ruff/pull/24388)) was closed on 2026-11-03:
"We've begun adding some Django support, but we are taking a slightly different approach."

## What a merged Django PR looks like

| PR | Rust +/- | mdtest +/- | Other files |
|---|---|---|---|
| #29642 `id`/`pk` | +210/-3 | +186 | `django.lock` (new) |
| #29651 `get_FOO_display` | +98/-13 | +62 | none |
| #29653 `get_next_by_FOO` | +77/-5 | +52 | none |
| #29664 FK `_id` | +84/-2 | +89 | none |
| #29744 abstract models | +73/-2 | +152 | none |
| #29769 `Meta` override | +12/-1 | -6 | none |
| #29785 FK/O2O as pk | +18/-3 | +54 | none |

## What they would want included

| Ingredient | Detail | Evidence |
|---|---|---|
| One behaviour per PR | Title `[ty] Django: <verb> ...` | All seven merged PRs |
| A linked issue | "Towards astral-sh/ty#1018" or "closes ty#NNNN" | #29651, #29744, #29785 |
| Summary with a minimal Python example | Expected types in comments; before/after where relevant | #29785 body: "(previously Book)" |
| mdtests in `external/django.md` | New `##` section; 1-2 sentences on Django's runtime behaviour, then a self-contained `py` block | `django.md:140-154`, `:394-415` |
| Assertions verified against real Django | "New Markdown tests. I checked against Django runtime behavior." | [#29664](https://github.com/astral-sh/ruff/pull/29664) |
| Negative and edge cases | Missing attribute errors, subclasses, `Self`, `name=` renames, MRO order | `django.md:181`, `:156-164`, `:433-444`, `:555-590` |
| Known gaps kept as `# TODO:` assertions | Assert today's wrong result; do not omit | `django.md:54-55`, `:75`, `:301-307` |
| Built on stub types, not hardcoded types | e.g. look up `AutoField` and approximate, do not write `int` | `django.rs:303-306` |
| Name pre-filter extended first | "so that we can return quickly for almost all attribute names" | `django.rs:226-234` |
| Per-class, Salsa-tracked metadata; inheritance by MRO walk | | `django.rs:117-151`, `:282-296` |
| Missing information returns `None`, never a guess | Non-literal keyword arguments are treated as absent | `django.rs:79-102` |
| User declarations win over synthesis | | `django.rs:270-280` |
| Comments that explain Django runtime facts | Doc comments carry a Python example | `django.rs:246-262` |
| Precedent from other checkers | `Meta` change justified as "similar to mypy and pyrefly" | [#29769](https://github.com/astral-sh/ruff/pull/29769) |
| Ecosystem diff explained in your own words | Outside author: "These are true positives." Merged next day | [#29305](https://github.com/astral-sh/ruff/pull/29305) |
| Edge cases handled or explicitly deferred | dcreager: edge cases "could be handled in follow-on PRs" | [#29785](https://github.com/astral-sh/ruff/pull/29785) |
| On by default, no switch | carljm: "special handling for pydantic should be on-by-default" | [ty#2403](https://github.com/astral-sh/ty/issues/2403) |
| Goal framed as removing false positives | carljm: "understand just enough of the API to avoid false positive errors" | [ty#1070](https://github.com/astral-sh/ty/issues/1070) |

Files a PR touches: `django.rs` and `django.md` always. `known.rs`, `slots.rs` and
`ty_module_resolver/src/module.rs` only for a new known class. `django.lock` only if dependencies
change. `cargo dev generate-all` output only for a new rule.

## What they would not want included

| Do not include | Strength | Evidence |
|---|---|---|
| A plugin system or plugin-like hook | Explicit | carljm: "We do not plan to add a plugin system." ([ty#2551](https://github.com/astral-sh/ty/issues/2551)) |
| Special-casing for what stubs can express | Explicit + closed PR | carljm: "it's a massive plus for the entire ecosystem if Django can be supported adequately using native type system features in django-stubs" (#24388) |
| More FK special-casing in the constructor binding | Explicit | sharkdp in #29731: "This special-casing could be removed with" the stubs PR |
| New detection mechanisms or architecture without prior design agreement | Explicit | sharkdp: "before someone goes ahead and implements this, I think there needs to be a larger design discussion" ([ty#2719](https://github.com/astral-sh/ty/issues/2719)) |
| Library-specific configuration options | Explicit (pydantic) | sharkdp: "Instead of adding a configuration setting, I'm thinking about adding a dedicated lint rule." ([ty#3966](https://github.com/astral-sh/ty/issues/3966)) |
| Several behaviours bundled in one PR | Observed | No merged Django PR does this; #24388 (broad) was closed |
| Test-only or parity-list PRs ahead of the roadmap | Explicit, Nov 2025 | sharkdp: "having extended tests in this area is probably just going to increase maintenance burden." ([#21308](https://github.com/astral-sh/ruff/pull/21308)) |
| Work before the name pre-filter, or untracked per-model work | Inferred | Django's own source is now a benchmark project (`79403d513`); #24388's memory report flagged ~583 kB from a new model query |
| Guessing when arguments are not literals | Observed | `django.rs:79-102` |
| Running or importing user code, reading settings at check time | Inferred; no maintainer statement | Nothing in `django.rs` does it |
| Docs or changelog edits in the ruff PR | Observed | None of the seven did; the docs page was written separately ([ty#4879](https://github.com/astral-sh/ty/pull/4879)) |
| AI-written description or replies; agent-opened PRs | Explicit policy | See `contributing-to-ty.md` section 4 |
| Tests that depend on stub internals likely to change | Closed PR | #29179 |
| Duplicating the open drafts | Observed | `pk = None` is [#30068](https://github.com/astral-sh/ruff/pull/30068); FK target inference is in [#29731](https://github.com/astral-sh/ruff/pull/29731) |

## Gap by gap

| Gap | Fits the existing pattern? | Maintainer position | Recommendation |
|---|---|---|---|
| `instance.pk = None` | Claimed by draft #30068 | In progress | Do not target |
| `<parent>_ptr` for multi-table inheritance | Yes (suffix filter + MRO walk) | None stated | Best first candidate; file an issue, then ask |
| `name=` field renames | Partly; hiding the original attribute needs restructuring | TODOs exist (`django.md:122-135`) | Ask first; small |
| Per-model `DoesNotExist` | Mostly | None stated | Low value; stubs already give a usable type |
| M2M `through` (class passed as object) | Yes | None stated | Wait for the stubs switch (same FK plumbing) |
| String refs, same module and `"self"` | Plausible, by extending `foreign_key_model_type` in #29731 | On sharkdp's list | Coordinate; collides with the draft |
| String refs `"app.Model"` | No; needs an app registry | On the list, no design | Design discussion first |
| Reverse relations | No; needs a project-wide model index | On the list, no design; TODO tests exist (`django.md:296-318`) | Design discussion first. pyrefly shipped same-file only |
| Constructor / `create()` keyword checks | Constructor has precedent (pydantic field-to-parameter synthesis) | "Precise constructor signatures" is on the list | Coordinate; high false-positive risk |
| `filter()` lookup validation | No; string DSL across relations | None stated | Ask first; likely far off |
| `values()` / `values_list()` / `annotate()` shapes | No; call-site special-casing | None stated | Ask first |
| Unannotated custom managers, `as_manager`, `from_queryset` | Not a missing-member problem; touches general inference | None stated | Report as an issue; may be a stubs fix |
| `_meta.get_field` | No; call special-casing | None stated | Low value |
| `DEFAULT_AUTO_FIELD`, settings types, `AUTH_USER_MODEL`, `get_user_model()` | No; needs settings-module configuration | None stated; config options were declined for pydantic | Do not build without an agreed design |
| `request.user` narrowing | General narrowing issue | carljm closed as duplicate of ty#1479 | Not a Django PR |

## Upstream-first opportunities

These belong in django-stubs, which the maintainers of both projects prefer.

- Remaining field get/set and nullability follow-ups from
  [typeddjango/django-stubs#3763](https://github.com/typeddjango/django-stubs/pull/3763) (FK
  overloads, `FilePathField`, `Any`-typed fields).
- Field input types such as ISO date strings (the TODO at `django.md:54-55`).
- django-stubs maintainer ngnpope: "Our intent is that `django-stubs` will support all type
  checkers stubs-only as best as possible."

## Suggested order of work

1. File one issue per gap in astral-sh/ty with a minimal reproduction. This is what sharkdp asked
   for: "It would help a lot to get specific feedback about what is not working yet."
2. Comment on ty#1018 naming the one gap you want to take and asking whether to wait for #29731.
3. Start with an in-pattern gap (`<parent>_ptr` is the cleanest), written against whichever stub
   package the tests pin at that time.
4. Send stub-level fixes to django-stubs in parallel.
5. Leave reverse relations, `"app.Model"` references and anything settings-driven until a
   maintainer has agreed a design.
6. After a ruff PR merges, offer a separate docs PR to astral-sh/ty for
   `docs/features/third-party/django.md`. The page is already behind (abstract models, `Meta`
   overrides and FK-as-pk are not listed).

## Unverified and open

- No maintainer has said outside Django PRs are welcome or unwelcome. sharkdp asked for feedback,
  not PRs.
- Whether sharkdp wants contributors to wait for the django-stubs switch is inferred from "this
  will be easier to fix once we rely on `django-stubs`"
  ([ty#4932](https://github.com/astral-sh/ty/issues/4932)), not stated as a request.
- Quotes were read through a summarising fetcher that truncates; check wording at the source
  before relying on it. Collapsed review threads and 19 hidden items on ty#1018 were not read.
- The feasibility column is inference from reading the code. Nothing was built or prototyped.
- Why unannotated `objects = BookManager()` reveals `BaseManager[Book]` was not traced.
- The "test-only PRs" statement is from November 2025 and may be outdated.
- No position was found on settings-module configuration; the pydantic precedent only suggests a
  lean against options.

## Sources

- ruff at `0528644c0`: `django.rs`, `django.md`, `types/class/static_literal.rs:1741-1752,1877`,
  `types/overrides/attributes.rs:466-474`, `types/dedicated/pytest/fixtures.rs:130-207`
- Commits `30be8844b`, `2fa2ecbbf`, `9dfc6ee97`, `005a31333`, `8d25f7d53`, `731a26b88`,
  `4160aece3`, `19db56ae3`, `79403d513`; draft branches for #29731 and #30068
- astral-sh/ruff PRs #21308, #24388, #29305, #29367, #29642, #29664, #29744, #29769, #29785
- astral-sh/ty issues #1018, #1070, #2296, #2403, #2551, #2719, #3966, #4932; PR #4879
- typeddjango/django-stubs #3763, #3343
- https://pyrefly.org/en/docs/django/
- `docs/features/third-party/django.md`, `CHANGELOG.md` in this repository
