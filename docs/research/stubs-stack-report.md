# ty Django support on unreleased django-stubs: stack report

Measured 2026-11-21. Our own working document; keep it out of any upstream pull request.

Result of running `plans/2026-11-21-django-stubs-tdd.md`, Tasks 1 to 8. Everything here is a draft
on our forks. No maintainer has agreed to any of it, nothing was pushed to or posted on an
upstream repository, and no pull request was opened.

Numbers for the private repository are counts only; see `private-repo-baseline.md` for how they
were measured.

## Branches

All in the ruff fork, stacked on `phillip/django-stubs-unreleased` (`9cdccf6`), which pins the
Django mdtest to django-stubs `44457d47e03845c27b560936ef0455d5dfc7b7d8` and starts with 24
failing assertions out of 85.

| Branch | Head | Commits | Assertions fixed | Still failing | Assertions in file |
|---|---|---|---:|---:|---:|
| `phillip/stubs-01-literal-metadata` | `f9766c6` | 1, ours | 2 | 22 | 85 |
| `phillip/stubs-02-foreign-key-target` | `d637930` | 1 cherry-picked (David Peter, `8c694178fe`), 2 ours | 15 | 7 | 88 |
| `phillip/stubs-03-relation-subclasses` | `25714d1` | 1, ours | 6 | 1 | 92 |
| `phillip/stubs-04-date-string` | `6ea7e39` | 1, ours | 1 (stale assertion removed) | 0 | 91 |
| `phillip/stubs-05-gap-tests` | `5416cf4` | 1, ours, tests only | n/a | 0 | 118 |

What each branch does:

- **01** reads `primary_key` and `null` with `as_bool_literal()` in `Field::from_definition`.
  Fixes the two nullable date navigation assertions.
- **02** cherry-picks the maintainer's draft commit with his authorship, resolved as in
  `django-stubs-switch-evidence/merge-resolution.patch`. Our two commits on top: read the foreign
  key `null` argument with `as_bool_literal()`; and return `Any | None` for a string reference
  with `null=True`, with three new assertions (`"Author"`, nullable `"Author"`, nullable `"self"`).
- **03** matches `ForeignKey` subclasses through the MRO (new `django::is_foreign_key`), which
  fixes the six `OneToOneField` assertions, and adds four assertions for user-defined subclasses.
- **04** removes the `invalid-assignment` assertion for an ISO date string.
- **05** adds 27 assertions under 18 `# TODO:` comments that record today's result for the top
  gaps.

Rust change for branches 01 to 04 together: 3 files, 69 insertions, 16 deletions. Every branch
passed `cargo fmt --all --check`, clippy on the whole workspace with warnings denied, and prek on
its changed files. `MDTEST_EXTERNAL=1 cargo test -p ty_python_semantic` passed in full on 04 and
05; on 01 to 03 its only failure was the Django mdtest, on exactly the lines listed as still
failing.

## What did not match the plan

1. **Task 5, user-defined subclass.** ty does not reject `class TrackedForeignKey(models.ForeignKey)`.
   It specializes `ForeignKey` with its default type arguments (`Any`), and the subclass has no
   type parameters for the constructor special case to fill, so the related model stays `Any`.
   The MRO scan cannot fix that. The test therefore uses a generic subclass
   (`class TrackedForeignKey[ST, GT](models.ForeignKey[ST, GT])`), which fails before the change
   and passes after it, and records the plain subclass as a TODO. Review focus 2 is only partly
   met: a plain subclass does not behave like `ForeignKey`.
2. **Task 4, the `null` comparison.** After the cherry-pick alone, the failing set was already the
   expected one. django-stubs types `ForeignKey`'s `null` parameter as `bool`, so the
   `as_bool_literal()` commit changes no test result today. It has no failing test of its own.
3. **Guidelines against plan.** Section 5 of the guidelines says not to add foreign-key
   special-casing to the constructor binding. The plan requires the maintainer's commit, which
   adds it. The plan was followed.
4. **Assertion count.** The file has 85 assertions on the base branch, not the 124 quoted in the
   research, which was counted on the parent link branch.
5. **Tooling.** `uv` on `PATH` was 0.11; 0.13.9 was installed into the scratchpad. The rule for an
   unresolved import is `import-not-found`. `run_ty.sh` passes the source root as an extra search
   path. The plan assumed the private packages could not be installed; they can, and the runs were
   repeated with them.
6. **Task 5 placement.** The MRO test lives in `django.rs` as `is_foreign_key`, next to `is_model`,
   not inline in `constructor.rs`.

## Review focus

| # | Question | Result |
|---:|---|---|
| 1 | String reference with `null=True` keeps `\| None` | Yes: `Any \| None`, for `"Author"` and `"self"` |
| 2 | User-defined `ForeignKey` subclass behaves like `ForeignKey` | Generic subclass: yes. Plain subclass: no, TODO |
| 3 | django-types projects do not get worse | Private repository output is byte-identical between `main-types` and `stack-types` |
| 4 | No change for non-Django code | 0. Every diagnostic that differs under django-stubs names a model or a `None` union |
| 5 | django-stubs 6.1.2 | Recorded below; not fixed |

## Django mdtest by stub package

`phillip/stubs-04-date-string`, 91 assertions, header repinned in a scratch worktree and the lock
regenerated with `MDTEST_UPGRADE_LOCKFILES=1`. The header changes were not committed.

| Stub package | Passing | Failing | Other lines with an unexpected diagnostic |
|---|---:|---:|---:|
| django-stubs `44457d47` (unreleased) | 91 | 0 | 0 |
| `django-types==0.24.0` | 84 | 7 | 3 |
| `django-stubs==6.1.2` | 43 | 48 | 1 |

- django-types: all ten lines are in tests this stack added or changed for django-stubs: the date
  string, the `ForeignKey` subclasses (django-types has one type parameter) and the string
  references. No assertion that exists on `main` fails.
- 6.1.2: 46 of the 48 reveal `Unknown`; the other two are assignment checks that no longer report.

## Private repository, before and after

`main` is ruff `cd2d973241`; `stack` is `phillip/stubs-04-date-string`.

| Environment | `main` | `stack` | Added | Removed |
|---|---:|---:|---:|---:|
| `types` (django-types 0.24.0) | 5703 | 5703 | 0 | 0 |
| `stubs612` (django-stubs 6.1.2) | 5183 | 5565 | not split | not split |
| `stubs` (unreleased django-stubs) | 5239 | 5621 | 401 | 19 |

No rule's count rises under `stack-types` compared with `main-types`.

The rise under django-stubs is the stack working, not a regression in ty: foreign keys that were
`Any` now have their model type, so code that reads an attribute of a nullable foreign key without
a `None` check is reported (243 `missing-union-attribute`), as are wrong argument types (97
`invalid-argument-type`) and attributes that do not exist on the related model (41
`missing-attribute`). It does mean that the switch plus the foreign-key work produces more
diagnostics for this project than either django-types or today's `main` on django-stubs.

### With the private packages installed

Added after the first report: the ten private packages install with the environment's existing
credential, so every run was repeated on fuller environments (see `private-repo-baseline.md`).
The conclusions do not change.

| Environment | `main` | `stack` | Added | Removed |
|---|---:|---:|---:|---:|
| `types-full` (django-types 0.24.0) | 5715 | 5715 | 0 | 0 |
| `stubs612-full` (django-stubs 6.1.2) | 5193 | 5575 | 450 | 68 |
| `stubs-full` (unreleased django-stubs) | 5250 | 5632 | 401 | 19 |

- `main-types-full` and `stack-types-full` are byte-identical.
- Under both django-stubs environments, every diagnostic that differs names a model class of the
  project, Django's `Model`, or a `None` union.
- The project's own type checker now starts, but stops on 58 errors in the project before
  checking, so there is still no reference count.

The tables below are from the first run, without the private packages.

### `stack-types` against `main-types`

Identical output: 5703 diagnostics in both runs, with the same count for every rule, and 170
`import-not-found` diagnostics for the packages left out of the environment in both.

### `stack-stubs` against `main-stubs`

| Rule | Count | Baseline | Delta |
|---|---:|---:|---:|
| `missing-attribute` | 2393 | 2352 | +41 |
| `invalid-argument-type` | 1309 | 1220 | +89 |
| `missing-union-attribute` | 682 | 439 | +243 |
| `not-subscriptable` | 209 | 209 | +0 |
| `incompatible-method-override` | 200 | 200 | +0 |
| `invalid-assignment` | 181 | 175 | +6 |
| `invalid-explicit-return` | 170 | 168 | +2 |
| `invalid-type-form` | 144 | 144 | +0 |
| `unused-type-ignore-comment` | 77 | 77 | +0 |
| `no-matching-overload` | 43 | 43 | +0 |
| `unsupported-operator` | 41 | 40 | +1 |
| `deprecated` | 28 | 28 | +0 |
| `lost-keyword-for-regular-parameter` | 27 | 27 | +0 |
| `incompatible-attribute-override` | 26 | 26 | +0 |
| `not-iterable` | 25 | 25 | +0 |
| `unknown-argument` | 14 | 14 | +0 |
| `too-many-positional-arguments` | 7 | 7 | +0 |
| `abstract-class-instantiation` | 6 | 6 | +0 |
| `missing-typed-dict-key` | 6 | 6 | +0 |
| `missing-module-member` | 5 | 5 | +0 |
| `not-callable` | 5 | 5 | +0 |
| `unsupported-base` | 4 | 4 | +0 |
| `invalid-attribute-access` | 3 | 3 | +0 |
| `missing-argument` | 3 | 3 | +0 |
| `import-not-found` | 2 | 2 | +0 |
| `incompatible-mutable-override` | 2 | 2 | +0 |
| `invalid-generator-return-type` | 2 | 2 | +0 |
| `invalid-implicit-return` | 2 | 2 | +0 |
| `invalid-parameter-default` | 2 | 2 | +0 |
| `parameter-already-assigned` | 1 | 1 | +0 |
| `possibly-missing-submodule` | 1 | 1 | +0 |
| `redundant-cast` | 1 | 1 | +0 |
| **Total** | 5621 | 5239 | +382 |

| `missing-attribute` name | Count | Baseline | Delta |
|---|---:|---:|---:|
| `*_set` | 52 | 52 | +0 |
| `*_id` | 49 | 49 | +0 |
| `*_ptr` | 0 | 0 | +0 |
| `get_*_display` | 0 | 0 | +0 |
| `objects` | 15 | 15 | +0 |
| `other` | 2277 | 2236 | +41 |
| **Total** | 2393 | 2352 | +41 |

`import-not-found` for packages left out of the environment: 170 (baseline 170)

### `stack-stubs612` against `main-stubs612`

| Rule | Count | Baseline | Delta |
|---|---:|---:|---:|
| `missing-attribute` | 2391 | 2350 | +41 |
| `invalid-argument-type` | 1305 | 1216 | +89 |
| `missing-union-attribute` | 681 | 438 | +243 |
| `not-subscriptable` | 209 | 209 | +0 |
| `incompatible-method-override` | 200 | 200 | +0 |
| `invalid-explicit-return` | 168 | 166 | +2 |
| `invalid-type-form` | 144 | 144 | +0 |
| `invalid-assignment` | 119 | 113 | +6 |
| `unused-type-ignore-comment` | 77 | 77 | +0 |
| `invalid-attribute-access` | 39 | 39 | +0 |
| `no-matching-overload` | 35 | 35 | +0 |
| `deprecated` | 28 | 28 | +0 |
| `unsupported-operator` | 28 | 27 | +1 |
| `lost-keyword-for-regular-parameter` | 27 | 27 | +0 |
| `incompatible-attribute-override` | 26 | 26 | +0 |
| `not-iterable` | 24 | 24 | +0 |
| `unknown-argument` | 14 | 14 | +0 |
| `not-callable` | 7 | 7 | +0 |
| `too-many-positional-arguments` | 7 | 7 | +0 |
| `abstract-class-instantiation` | 6 | 6 | +0 |
| `missing-typed-dict-key` | 6 | 6 | +0 |
| `missing-module-member` | 5 | 5 | +0 |
| `unsupported-base` | 4 | 4 | +0 |
| `missing-argument` | 3 | 3 | +0 |
| `import-not-found` | 2 | 2 | +0 |
| `invalid-generator-return-type` | 2 | 2 | +0 |
| `invalid-implicit-return` | 2 | 2 | +0 |
| `invalid-parameter-default` | 2 | 2 | +0 |
| `incompatible-mutable-override` | 1 | 1 | +0 |
| `parameter-already-assigned` | 1 | 1 | +0 |
| `possibly-missing-submodule` | 1 | 1 | +0 |
| `redundant-cast` | 1 | 1 | +0 |
| **Total** | 5565 | 5183 | +382 |

| `missing-attribute` name | Count | Baseline | Delta |
|---|---:|---:|---:|
| `*_set` | 52 | 52 | +0 |
| `*_id` | 49 | 49 | +0 |
| `*_ptr` | 0 | 0 | +0 |
| `get_*_display` | 0 | 0 | +0 |
| `objects` | 15 | 15 | +0 |
| `other` | 2275 | 2234 | +41 |
| **Total** | 2391 | 2350 | +41 |

`import-not-found` for packages left out of the environment: 170 (baseline 170)

### `stack-stubs` against `main-types`

| Rule | Count | Baseline | Delta |
|---|---:|---:|---:|
| `missing-attribute` | 2393 | 2417 | -24 |
| `invalid-argument-type` | 1309 | 1329 | -20 |
| `missing-union-attribute` | 682 | 559 | +123 |
| `not-subscriptable` | 209 | 337 | -128 |
| `incompatible-method-override` | 200 | 319 | -119 |
| `invalid-assignment` | 181 | 153 | +28 |
| `invalid-explicit-return` | 170 | 126 | +44 |
| `invalid-type-form` | 144 | 144 | +0 |
| `unused-type-ignore-comment` | 77 | 77 | +0 |
| `no-matching-overload` | 43 | 38 | +5 |
| `unsupported-operator` | 41 | 45 | -4 |
| `deprecated` | 28 | 18 | +10 |
| `lost-keyword-for-regular-parameter` | 27 | 14 | +13 |
| `incompatible-attribute-override` | 26 | 32 | -6 |
| `not-iterable` | 25 | 24 | +1 |
| `unknown-argument` | 14 | 13 | +1 |
| `too-many-positional-arguments` | 7 | 11 | -4 |
| `abstract-class-instantiation` | 6 | 6 | +0 |
| `missing-typed-dict-key` | 6 | 6 | +0 |
| `missing-module-member` | 5 | 7 | -2 |
| `not-callable` | 5 | 5 | +0 |
| `unsupported-base` | 4 | 4 | +0 |
| `invalid-attribute-access` | 3 | 0 | +3 |
| `missing-argument` | 3 | 5 | -2 |
| `import-not-found` | 2 | 2 | +0 |
| `incompatible-mutable-override` | 2 | 4 | -2 |
| `invalid-generator-return-type` | 2 | 2 | +0 |
| `invalid-implicit-return` | 2 | 2 | +0 |
| `invalid-parameter-default` | 2 | 2 | +0 |
| `parameter-already-assigned` | 1 | 1 | +0 |
| `possibly-missing-submodule` | 1 | 0 | +1 |
| `redundant-cast` | 1 | 1 | +0 |
| **Total** | 5621 | 5703 | -82 |

| `missing-attribute` name | Count | Baseline | Delta |
|---|---:|---:|---:|
| `*_set` | 52 | 52 | +0 |
| `*_id` | 49 | 51 | -2 |
| `*_ptr` | 0 | 0 | +0 |
| `get_*_display` | 0 | 0 | +0 |
| `objects` | 15 | 15 | +0 |
| `other` | 2277 | 2299 | -22 |
| **Total** | 2393 | 2417 | -24 |

`import-not-found` for packages left out of the environment: 170 (baseline 170)

## Glossary check

The changed test prose and Rust comments were checked against `ty-glossary.md`, including its
"Words to avoid" section. Section titles with no existing ty term, taken from Django's
documentation and reported here for a decision: "User model", "Choices classes", "Custom
`QuerySet` methods on managers", "Annotations", and "Primary key of an abstract model's
subclasses". `is_foreign_key` follows `is_model`.

## Not done

- The project's own type checker gave no reference count: it stops on errors in the project before
  checking.
- The full workspace test suite, `prek run --all-files` and `cargo dev generate-all` were not run;
  the plan's checks cover the `ty_python_semantic` crate and the changed files.
- The diagnostics that differ under `stubs612` were split into added and removed only for the run
  with private packages.
- No ecosystem, memory or performance run.
- 32 `missing-attribute` diagnostics for `id` on one model of the private repository have no
  explanation yet.
