# ty on the private repository: baseline

Measured 2026-11-21. Our own working document; keep it out of any upstream pull request.

This file holds counts only. The repository is private: no name, path, identifier, dependency or
diagnostic text from it appears here. Raw output stays in the session scratchpad.

## Setup

- ty: debug build of ruff `cd2d973241` (`main` on 2026-11-21), called `main` below.
- Project: one Django project, 1526 Python files outside its migrations. Migrations are excluded,
  as they are in the project's own type-checker configuration.
- Environments, built by `harness/make_env.sh` from the project's lock file at its pinned Python
  version, without resolving dependencies:

| Environment | Stub package |
|---|---|
| `types` | `django-types==0.24.0` |
| `stubs612` | `django-stubs==6.1.2` |
| `stubs` | `django-stubs` at `44457d47e03845c27b560936ef0455d5dfc7b7d8` (unreleased) |

- Ten locked packages come from private sources and are left out of every environment. ty reports
  170 `import-not-found` diagnostics for them in every run. They are listed on their own line
  under each table and excluded from every other number.
- The project's own Django and REST framework stub packages are removed from every environment, so
  each has exactly one Django stub package (plus `django-stubs-ext`, which `django-stubs` requires).
- Neither `django-stubs` version forced a different Django or Python version. The unreleased
  commit still reports its version as 6.1.2; the two environments were told apart by their
  contents.
- Runs: `harness/run_ty.sh`, which adds the source root as an extra search path because the
  project's first-party imports are rooted there. The rule for an unresolved import is
  `import-not-found` in this build, not `unresolved-import`.
- Reference run of the project's own type checker: not possible. It imports the project's settings
  module, which needs the packages that were left out. Skipped.

## Diagnostics per rule, ty `main`, without the private packages

### `main-types`

| Rule | Count |
|---|---:|
| `missing-attribute` | 2417 |
| `invalid-argument-type` | 1329 |
| `missing-union-attribute` | 559 |
| `not-subscriptable` | 337 |
| `incompatible-method-override` | 319 |
| `invalid-assignment` | 153 |
| `invalid-type-form` | 144 |
| `invalid-explicit-return` | 126 |
| `unused-type-ignore-comment` | 77 |
| `unsupported-operator` | 45 |
| `no-matching-overload` | 38 |
| `incompatible-attribute-override` | 32 |
| `not-iterable` | 24 |
| `deprecated` | 18 |
| `lost-keyword-for-regular-parameter` | 14 |
| `unknown-argument` | 13 |
| `too-many-positional-arguments` | 11 |
| `missing-module-member` | 7 |
| `abstract-class-instantiation` | 6 |
| `missing-typed-dict-key` | 6 |
| `missing-argument` | 5 |
| `not-callable` | 5 |
| `incompatible-mutable-override` | 4 |
| `unsupported-base` | 4 |
| `import-not-found` | 2 |
| `invalid-generator-return-type` | 2 |
| `invalid-implicit-return` | 2 |
| `invalid-parameter-default` | 2 |
| `parameter-already-assigned` | 1 |
| `redundant-cast` | 1 |
| **Total** | 5703 |

| `missing-attribute` name | Count |
|---|---:|
| `*_set` | 52 |
| `*_id` | 51 |
| `*_ptr` | 0 |
| `get_*_display` | 0 |
| `objects` | 15 |
| `other` | 2299 |
| **Total** | 2417 |

`import-not-found` for packages left out of the environment: 170

### `main-stubs612`

| Rule | Count |
|---|---:|
| `missing-attribute` | 2350 |
| `invalid-argument-type` | 1216 |
| `missing-union-attribute` | 438 |
| `not-subscriptable` | 209 |
| `incompatible-method-override` | 200 |
| `invalid-explicit-return` | 166 |
| `invalid-type-form` | 144 |
| `invalid-assignment` | 113 |
| `unused-type-ignore-comment` | 77 |
| `invalid-attribute-access` | 39 |
| `no-matching-overload` | 35 |
| `deprecated` | 28 |
| `lost-keyword-for-regular-parameter` | 27 |
| `unsupported-operator` | 27 |
| `incompatible-attribute-override` | 26 |
| `not-iterable` | 24 |
| `unknown-argument` | 14 |
| `not-callable` | 7 |
| `too-many-positional-arguments` | 7 |
| `abstract-class-instantiation` | 6 |
| `missing-typed-dict-key` | 6 |
| `missing-module-member` | 5 |
| `unsupported-base` | 4 |
| `missing-argument` | 3 |
| `import-not-found` | 2 |
| `invalid-generator-return-type` | 2 |
| `invalid-implicit-return` | 2 |
| `invalid-parameter-default` | 2 |
| `incompatible-mutable-override` | 1 |
| `parameter-already-assigned` | 1 |
| `possibly-missing-submodule` | 1 |
| `redundant-cast` | 1 |
| **Total** | 5183 |

| `missing-attribute` name | Count |
|---|---:|
| `*_set` | 52 |
| `*_id` | 49 |
| `*_ptr` | 0 |
| `get_*_display` | 0 |
| `objects` | 15 |
| `other` | 2234 |
| **Total** | 2350 |

`import-not-found` for packages left out of the environment: 170

### `main-stubs`

| Rule | Count |
|---|---:|
| `missing-attribute` | 2352 |
| `invalid-argument-type` | 1220 |
| `missing-union-attribute` | 439 |
| `not-subscriptable` | 209 |
| `incompatible-method-override` | 200 |
| `invalid-assignment` | 175 |
| `invalid-explicit-return` | 168 |
| `invalid-type-form` | 144 |
| `unused-type-ignore-comment` | 77 |
| `no-matching-overload` | 43 |
| `unsupported-operator` | 40 |
| `deprecated` | 28 |
| `lost-keyword-for-regular-parameter` | 27 |
| `incompatible-attribute-override` | 26 |
| `not-iterable` | 25 |
| `unknown-argument` | 14 |
| `too-many-positional-arguments` | 7 |
| `abstract-class-instantiation` | 6 |
| `missing-typed-dict-key` | 6 |
| `missing-module-member` | 5 |
| `not-callable` | 5 |
| `unsupported-base` | 4 |
| `invalid-attribute-access` | 3 |
| `missing-argument` | 3 |
| `import-not-found` | 2 |
| `incompatible-mutable-override` | 2 |
| `invalid-generator-return-type` | 2 |
| `invalid-implicit-return` | 2 |
| `invalid-parameter-default` | 2 |
| `parameter-already-assigned` | 1 |
| `possibly-missing-submodule` | 1 |
| `redundant-cast` | 1 |
| **Total** | 5239 |

| `missing-attribute` name | Count |
|---|---:|
| `*_set` | 52 |
| `*_id` | 49 |
| `*_ptr` | 0 |
| `get_*_display` | 0 |
| `objects` | 15 |
| `other` | 2236 |
| **Total** | 2352 |

`import-not-found` for packages left out of the environment: 170

## Unreleased django-stubs against django-types, ty `main`, without the private packages

### `main-stubs` against `main-types`

| Rule | Count | Baseline | Delta |
|---|---:|---:|---:|
| `missing-attribute` | 2352 | 2417 | -65 |
| `invalid-argument-type` | 1220 | 1329 | -109 |
| `missing-union-attribute` | 439 | 559 | -120 |
| `not-subscriptable` | 209 | 337 | -128 |
| `incompatible-method-override` | 200 | 319 | -119 |
| `invalid-assignment` | 175 | 153 | +22 |
| `invalid-explicit-return` | 168 | 126 | +42 |
| `invalid-type-form` | 144 | 144 | +0 |
| `unused-type-ignore-comment` | 77 | 77 | +0 |
| `no-matching-overload` | 43 | 38 | +5 |
| `unsupported-operator` | 40 | 45 | -5 |
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
| **Total** | 5239 | 5703 | -464 |

| `missing-attribute` name | Count | Baseline | Delta |
|---|---:|---:|---:|
| `*_set` | 52 | 52 | +0 |
| `*_id` | 49 | 51 | -2 |
| `*_ptr` | 0 | 0 | +0 |
| `get_*_display` | 0 | 0 | +0 |
| `objects` | 15 | 15 | +0 |
| `other` | 2236 | 2299 | -63 |
| **Total** | 2352 | 2417 | -65 |

`import-not-found` for packages left out of the environment: 170 (baseline 170)

## Census of Django features

Counted by regular expression with `harness/census.py`. The numbers are occurrences in the 1526
files, tests included, so they show how much of each feature the project uses, not how many
diagnostics it causes.

| Feature | Occurrences |
|---|---:|
| Python files scanned | 1526 |
| `ForeignKey(`/`OneToOneField(` with a class target | 193 |
| `ForeignKey(`/`OneToOneField(` with a string target | 254 |
| `ForeignKey(`/`OneToOneField(` with `"self"` | 4 |
| `related_name=` | 456 |
| `ManyToManyField(` | 59 |
| `through=` | 13 |
| `objects = ` custom managers | 35 |
| `.as_manager()` | 5 |
| `from_queryset(` | 1 |
| `.values(` | 340 |
| `.values_list(` | 707 |
| `.annotate(` | 96 |
| `get_user_model(` | 69 |
| `request.user` | 523 |
| `settings.` | 231 |
| `TextChoices`/`IntegerChoices` | 147 |
| `parent_link=` | 0 |
| `abstract = True` | 23 |
| `proxy = True` | 0 |

## With the private packages

The ten packages from private sources turned out to be installable with the credential this
environment already has. All three kinds of source worked: two package registries on the project's
git host, git dependencies on the same host, and one public registry outside PyPI. A second set of
environments, `types-full`, `stubs612-full` and `stubs-full`, adds them through the optional
fifth argument of `harness/make_env.sh`. No package is left out of these environments, and no
`import-not-found` diagnostic for a private package remains.

The tables above are kept as the run without private packages. Comparisons always use the same
environment on both sides.

### `main-types-full`

| Rule | Count |
|---|---:|
| `missing-attribute` | 2417 |
| `invalid-argument-type` | 1336 |
| `missing-union-attribute` | 559 |
| `not-subscriptable` | 337 |
| `incompatible-method-override` | 319 |
| `invalid-assignment` | 157 |
| `invalid-type-form` | 144 |
| `invalid-explicit-return` | 127 |
| `unused-type-ignore-comment` | 77 |
| `unsupported-operator` | 45 |
| `no-matching-overload` | 38 |
| `incompatible-attribute-override` | 32 |
| `not-iterable` | 24 |
| `deprecated` | 18 |
| `lost-keyword-for-regular-parameter` | 14 |
| `unknown-argument` | 13 |
| `too-many-positional-arguments` | 11 |
| `missing-module-member` | 7 |
| `abstract-class-instantiation` | 6 |
| `missing-typed-dict-key` | 6 |
| `missing-argument` | 5 |
| `not-callable` | 5 |
| `incompatible-mutable-override` | 4 |
| `unsupported-base` | 4 |
| `import-not-found` | 2 |
| `invalid-generator-return-type` | 2 |
| `invalid-implicit-return` | 2 |
| `invalid-parameter-default` | 2 |
| `parameter-already-assigned` | 1 |
| `redundant-cast` | 1 |
| **Total** | 5715 |

| `missing-attribute` name | Count |
|---|---:|
| `*_set` | 52 |
| `*_id` | 51 |
| `*_ptr` | 0 |
| `get_*_display` | 0 |
| `objects` | 15 |
| `other` | 2299 |
| **Total** | 2417 |

`import-not-found` for packages left out of the environment: 0

### `main-stubs612-full`

| Rule | Count |
|---|---:|
| `missing-attribute` | 2350 |
| `invalid-argument-type` | 1222 |
| `missing-union-attribute` | 438 |
| `not-subscriptable` | 209 |
| `incompatible-method-override` | 200 |
| `invalid-explicit-return` | 167 |
| `invalid-type-form` | 144 |
| `invalid-assignment` | 116 |
| `unused-type-ignore-comment` | 77 |
| `invalid-attribute-access` | 39 |
| `no-matching-overload` | 35 |
| `deprecated` | 28 |
| `lost-keyword-for-regular-parameter` | 27 |
| `unsupported-operator` | 27 |
| `incompatible-attribute-override` | 26 |
| `not-iterable` | 24 |
| `unknown-argument` | 14 |
| `not-callable` | 7 |
| `too-many-positional-arguments` | 7 |
| `abstract-class-instantiation` | 6 |
| `missing-typed-dict-key` | 6 |
| `missing-module-member` | 5 |
| `unsupported-base` | 4 |
| `missing-argument` | 3 |
| `import-not-found` | 2 |
| `invalid-generator-return-type` | 2 |
| `invalid-implicit-return` | 2 |
| `invalid-parameter-default` | 2 |
| `incompatible-mutable-override` | 1 |
| `parameter-already-assigned` | 1 |
| `possibly-missing-submodule` | 1 |
| `redundant-cast` | 1 |
| **Total** | 5193 |

| `missing-attribute` name | Count |
|---|---:|
| `*_set` | 52 |
| `*_id` | 49 |
| `*_ptr` | 0 |
| `get_*_display` | 0 |
| `objects` | 15 |
| `other` | 2234 |
| **Total** | 2350 |

`import-not-found` for packages left out of the environment: 0

### `main-stubs-full`

| Rule | Count |
|---|---:|
| `missing-attribute` | 2352 |
| `invalid-argument-type` | 1226 |
| `missing-union-attribute` | 439 |
| `not-subscriptable` | 209 |
| `incompatible-method-override` | 200 |
| `invalid-assignment` | 179 |
| `invalid-explicit-return` | 169 |
| `invalid-type-form` | 144 |
| `unused-type-ignore-comment` | 77 |
| `no-matching-overload` | 43 |
| `unsupported-operator` | 40 |
| `deprecated` | 28 |
| `lost-keyword-for-regular-parameter` | 27 |
| `incompatible-attribute-override` | 26 |
| `not-iterable` | 25 |
| `unknown-argument` | 14 |
| `too-many-positional-arguments` | 7 |
| `abstract-class-instantiation` | 6 |
| `missing-typed-dict-key` | 6 |
| `missing-module-member` | 5 |
| `not-callable` | 5 |
| `unsupported-base` | 4 |
| `invalid-attribute-access` | 3 |
| `missing-argument` | 3 |
| `import-not-found` | 2 |
| `incompatible-mutable-override` | 2 |
| `invalid-generator-return-type` | 2 |
| `invalid-implicit-return` | 2 |
| `invalid-parameter-default` | 2 |
| `parameter-already-assigned` | 1 |
| `possibly-missing-submodule` | 1 |
| `redundant-cast` | 1 |
| **Total** | 5250 |

| `missing-attribute` name | Count |
|---|---:|
| `*_set` | 52 |
| `*_id` | 49 |
| `*_ptr` | 0 |
| `get_*_display` | 0 |
| `objects` | 15 |
| `other` | 2236 |
| **Total** | 2352 |

`import-not-found` for packages left out of the environment: 0

### Reference run of the project's own type checker

With the private packages present, the project's type checker starts and loads the settings
module. It then stops before checking: 58 errors in 23 files, of which 56 are `import-untyped`
and 1 is `syntax` (an invalid `type: ignore` comment), with the note that errors prevented further
checking. The remaining error has no code. There is therefore still no per-code reference count.
The project's configuration was not changed to get past this.

## Ranked gaps after the stack

Measured with ty built from ruff fork branch `phillip/stubs-04-date-string` and the unreleased
django-stubs environment (run `stack-stubs`, 5621 diagnostics). The five diagnostic counts are the
same with the private packages installed (run `stack-stubs-full`, 5632 diagnostics). Diagnostics were grouped by cause
with a scratch script that reads the project's model declarations; the grouping is approximate.
Gaps that produce a diagnostic come first, by count. Gaps that are silent (`Any` or `Unknown`
with no diagnostic) follow, by census count.

| Rank | Gap | Diagnostics | Census occurrences | Test in `django.md` (branch `phillip/stubs-05-gap-tests`) |
|---:|---|---:|---:|---|
| 1 | Reverse accessors (`related_name`, `<model>_set`, `%(class)s` names, one-to-one) | 844 | 456 (`related_name=`) | "Foreign key IDs" (existing TODO), "Reverse accessors" |
| 2 | User model: `get_user_model()` and `request.user` | 256 | 69 and 523 | "User model" |
| 3 | `id` on a value annotated with an abstract model | 46 | 23 (`abstract = True`) | "Primary key of an abstract model's subclasses" |
| 4 | A `Choices` class passed as `choices` | 29 | 147 (`TextChoices`/`IntegerChoices`) | "Choices classes" |
| 5 | Custom `QuerySet` methods through `as_manager()` and `from_queryset()` | 13 | 6 | "Custom `QuerySet` methods on managers" |
| 6 | `values()` and `values_list()` row types | silent | 1047 | "`values()` and `values_list()`" |
| 7 | String references, including `"self"` (value and `<field>_id`) | silent | 258 | "String references" |
| 8 | Attributes added by `annotate()` | not counted separately | 96 | "Annotations" |

Notes on the counts:

- Rank 1 counts `missing-attribute` diagnostics whose attribute name matches a reverse accessor
  that a relation in the project declares for that model.
- Rank 2 counts every diagnostic whose message names `AbstractBaseUser` or `AnonymousUser`.
- Rank 4 is 1 `invalid-argument-type` plus 28 `no-matching-overload` and `invalid-assignment`
  diagnostics on fields that also carry a field annotation. The single-argument case in the test
  is the minimal form.
- Not ranked, because they are below the top eight: `ManyToManyField` (59 occurrences; the related
  manager is typed, `through` is `type[Any]`) and `through=` (13).
- Not Django gaps, but large: 152 diagnostics come from a third-party package's model attribute
  that has no stubs; 271 `missing-attribute` and `invalid-type-form` diagnostics come from model
  classes that a project decorator turns into `type[Model]`; 32 are `id` on one model for which no
  cause was found.
