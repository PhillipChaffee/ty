# Switching ty's Django support from django-types to django-stubs: research synthesis

Research date: 2026-11-21. Our own working document; keep it out of any upstream pull request.
The scratch paths cited below are from a temporary session directory. Copies of the researcher
reports, the inference matrix, the probe file, the scratch patches and the failure lists are in
`docs/research/django-stubs-switch-evidence/` next to this file.


Evidence labels used throughout: **MEASURED** (a researcher ran ty or the test suite), **READ**
(seen in stubs, code, or web pages), **INFERRED** (reasoned, not checked). Report ids (S1-S3,
R1-R5) follow each claim. GitHub pages were read through a summarising fetcher, so quotes are
short fragments and may be truncated (S2, S3, R4).

## 1. Summary

- The switch is small in ty's Rust code but large in effect. Only one code path depends on the
  shape of django-types (the `related_model` lookup); the rest keys on names both packages share
  (READ, S1; MEASURED, R3).
- The django-stubs version that makes the switch workable is **not released**. PR
  typeddjango/django-stubs#3763 merged on 2026-11-19; the latest PyPI release is 6.1.2 of
  2026-10-05 (READ, S2, S3, R4).
- On released 6.1.2, ty infers `Unknown` for every field attribute, `id` and `pk`. On unreleased
  master, scalar fields match django-types, managers and querysets improve, and every
  ForeignKey/OneToOneField type becomes a silent `Any` unless ty special-cases it (MEASURED, R1).
- Swapping only the stub package under current ty code takes the Django test file from 124/124
  passing to 95 (master) or 58 (6.1.2) (MEASURED, R3).
- The maintainer's draft astral-sh/ruff#29731 still builds and passes at its own head, but is 492
  commits behind main. A scratch merge needed about 15 lines of mechanical rework plus about 6
  lines of real fixes to pass all current tests. None of this was pushed (MEASURED, R2).
- The research exposed a latent ty bug: field metadata such as `null=True` is read by comparing
  with a literal `True` in a way that fails when the stub annotates the parameter as
  `Literal[True]`. The same comparison guards `primary_key` and the `parent_link` check on our
  branch (MEASURED, R2, R3).
- Our `<parent>_ptr` synthesis is stub-independent; `<parent>_ptr_id` is as good as the parent's
  `pk` (MEASURED, R3).
- Users face real changes: uninstall django-types, runtime Django becomes a dependency of the
  stubs, manager imports and field annotations change, some checks get looser (READ, R4;
  MEASURED, R1).

## 2. What the switch is

A **stub package** supplies type information for a library that ships none. A **plugin** is
checker-specific code that computes types the stubs cannot express; ty has none ("ty does not
have a plugin system (yet?)", sharkdp, astral-sh/ty#1018, 2026-11-02; READ, S3).

| | django-types (sbdchd) | django-stubs (typeddjango) |
|---|---|---|
| Design | Fork of django-stubs "with the goal of removing the mypy plugin dependency" | Full support only with its mypy plugin; pyright, pyrefly, ty: "basic support, checked in CI" |
| Latest release | 0.24.0, 2026-04-22 | 6.1.2, 2026-10-05 |
| Releases, last 12 months | 2 | 15 |
| Downloads, last month | 1,633,070 | 14,872,850 |
| Requires | `types-psycopg2`; Python >=3.10 | `django`, `django-stubs-ext>=6.0.2`, `types-pyyaml`, `typing-extensions`; Python >=3.11 |

Sources: S2, S3, R4 (READ). Both install the same top-level `django-stubs/` directory, so they
cannot coexist in one environment (READ, S2).

**Why ty started on django-types.** ty's Django support merged on 2026-10-22 (ruff#29642).
sharkdp: "I didn't want to add special handling for those magic `_pyi_private_{set,get}_type`
fields"; "Really the only thing that was problematic with django-stubs are the constructors on
field classes like `CharField`" (READ, S3).

**Why django-stubs.** It has about 9 times the downloads, pyrefly recommends it, the Django
projects in upstream mypy_primer (zulip and others) install it, and its maintainers state the
intent to "support all type checkers stubs-only as best as possible" (READ, S3). sharkdp,
2026-11-02: "we plan to support `django-stubs` as the default stub package soon" (READ, S3, R4).

**What is and is not released.** #3763 (merged 2026-11-19 as `2c8f775`, 42 files, +3048/-514)
removes the `_pyi_private_*` hints except on `AutoField`, and gives each field defaulted type
parameters plus `__init__` overloads. No release, milestone, or version statement exists; the
README row reads "unreleased" (READ, S2, R4).

**Who is doing what.** sharkdp owns draft ruff#29731 (opened and last pushed 2026-10-26, no
reviewers, empty test plan). UnknownPlatypus authored #3763 and invited anyone to start
follow-ups, "especially the fk update." The ForeignKey follow-up PR is not opened (READ, S3, R4).

## 3. What changes in the stubs

A field class is generic in a **set type** (what you may assign) and a **get type** (what you
read). A **PEP 696 default** is the value a type parameter takes when not given explicitly.

| Area | django-types 0.24.0 | django-stubs 6.1.2 | django-stubs master |
|---|---|---|---|
| Field type parameters | One per field | Two, no defaults | Two, with defaults (`CharField`: `str \| int` / `str`) |
| `null=True` | `__new__` overloads | Plugin only | `__init__` overloads with `self:` annotation and `null: Literal[True]` |
| `IntegerField` set type | `int \| Combinable` | n/a | `float \| int \| str` (plus `Combinable`) |
| `AutoField` | `IntegerField[int]` | Generic, no defaults | Defaults `int \| str` / `int` |
| `ForeignKey` | `Generic[_M]`; `to: type[_M] \| str`; `__new__` overloads for null | Same shape as master | `to: type[Model] \| str`, unlinked to type parameters, which default to `Any`; single `__init__`, `null: bool` |
| `related_model` on FK | Attribute `type[_M]` | Property `-> type[Model]` | Same |
| `Model.objects` | `ClassVar[BaseManager[Self]]` | Metaclass `__getattr__(name: Literal["objects"])` | Same |
| `Manager` | Subclass of `QuerySet` | Not a `QuerySet` | `Generic[_T_co, _QS_co]` |
| `.values()` | `ValuesQuerySet[...]` | `QuerySet[M, dict[str, Any]]` | Same |
| M2M manager | `ManyToManyRelatedManager` in `manager.pyi` | `ManyRelatedManager` in `related_descriptors.pyi` | Same |
| `get_user_model()` | `type[AbstractUser]` | `type[AbstractBaseUser]` | Same |
| `TextChoices.choices` | `Sequence[tuple[_EnumMemberT, str]]` | `list[tuple[str, _StrOrPromise]]` | Same |

All READ, S2 (line numbers in that report). Still `Any` or plugin-only on master: FK and
OneToOne targets and nullability, `<fk>_id`, `id`, `pk`, reverse accessors, `get_<field>_display`,
typed `Model.__init__`/`create`/`filter` kwargs, `values` row types, `from_queryset`,
`WithAnnotations`, the swappable user model (READ, S2).

Note: unreleased django-types main has itself moved toward django-stubs (metaclass `objects`,
two-parameter `QuerySet`), so the pinned 0.24.0 no longer represents that project's head
(READ, S2, R4).

## 4. What ty infers before and after

MEASURED by R1: ty main build `c068ccdd0`, Python 3.13.18, Django 6.1.3, 120 probes plus 38
follow-ups, no ty special-casing beyond current main.

| Class | Probe | django-types 0.24.0 | Released 6.1.2 | Master `44457d47` |
|---|---|---|---|---|
| Unchanged | Scalar fields, with and without `null=True` | `str`, `int \| None`, ... | **`Unknown`** | Same as django-types |
| Unchanged | `book.id`, `book.pk` | `int` | **`Unknown`** | `int` |
| Better | `.all()` / `.filter()` | `BaseManager[Author]` | `QuerySet[Author, Author]` | Same as 6.1.2 |
| Better | `objects = BookManager()` | `BaseManager[Book]` | `BookManager` | `BookManager` |
| Better | `as_manager().all()` | `Manager[Book]` | `QuerySet[Book, Book]` | `BookQuerySet` |
| Better | `author.objects` on instance | No error | missing-attribute | missing-attribute |
| Silently Any | `book.author` (FK by class) | `Author` | `Unknown` | `Any` |
| Silently Any | Nullable FK | `Author \| None` | `Unknown` | `Any` |
| Silently Any | `book.author_id` | `int` | `Any` | `Any` |
| Silently Any | OneToOne; `pk` via OneToOne | `Author`; `int` | `Unknown`; `Any` | `Any`; `Any` |
| New false positive | `<fk>_id` with `to_field` | `str` | missing-attribute | missing-attribute |
| New error | `get_user_model()().username` | `str` | missing-attribute | missing-attribute |
| New error | `Book.cheap_ones.cheap()` | `Unknown`, silent | missing-attribute | missing-attribute |
| Looser | `book.title = 3`, `book.pages = "abc"` | invalid-assignment | Not checked | Accepted |
| Looser | `book.published = "2020-01-01"` | invalid-assignment | Not checked | Accepted (intended) |
| Annotation | `title: models.CharField[str]` | Fine | invalid-type-arguments | Fine |

Same in all three: string-named FK targets are not resolved (`Unknown` or `Any`), no constructor
keyword checking, no reverse accessors, `settings.X` is `Any` (MEASURED, R1).

Workaround under django-stubs: annotate `fk: models.ForeignKey[Author, Author]`; the value type
and assignments are then checked, but `<fk>_id` stays `Any`. One-parameter `ForeignKey[Author]`
works in all three environments (MEASURED, R1).

## 5. What ty's code depends on

**Stub-independent** (driven by syntax and class structure; MEASURED, R3): model detection,
`Meta.abstract`/`proxy`, presence of `id`/`pk`, `name=` override, existence of `get_*_display`
and date navigation methods, `<parent>_ptr` existence and type, suppression rules. Field metadata
(`null`, `primary_key`, `choices`, `to_field`, `name`) is read from call keywords,
`django.rs:71-102` (READ, S1).

**Stub-sensitive points.** File is
`crates/ty_python_semantic/src/types/dedicated/django.rs`. Line numbers differ by tree: S1 and R2
cite main `cd2d973241`; R3 cites our branch `25bb62e`; S3 and R4 cite `:396` and `:396-400` in
our checkout.

| Dependency | Main (S1, R2) | Our branch (R3) | Effect under django-stubs |
|---|---|---|---|
| `related_model` lookup for `<fk>_id` | 359-369 | 400-405 | Returns `type[Model]`; `pk` on `Model` is `Any` |
| `to_field` lookup on that model | 370-379 | 407-411 | Attribute not found, so `<fk>_id` is missing |
| Automatic `AutoField` instance | 303-306 | 340-343 | `Unknown` on 6.1.2; `int` on master |
| `== Type::bool_literal(true)` metadata checks | 79-85, 92-94 | 92-94 | Fails for `Literal[True]` parameters |
| `<parent>_ptr_id` is parent `pk` | n/a | 466-469 | Follows scalar `pk` |

Shared names are unaffected: `known.rs:166-169, 1216-1219, 1658-1660, 1894-1896, 1911`;
`ty_module_resolver/src/module.rs:280-285, 345-347, 382-384`; `slots.rs:180-183` (READ, S1).
Test pin: `resources/mdtest/external/django.md:11` and `django.lock` (READ, S1).

**Swap experiment** (MEASURED, R3; an **mdtest** is ty's Markdown test file with inline
assertions; this one has 124: 88 `revealed`, 36 `error`; ty code unchanged at `25bb62e`):

| Stub package | Pass | Fail |
|---|---|---|
| django-types 0.24.0 | 124 | 0 |
| django-stubs master `44457d4` | 95 | 29 |
| django-stubs 6.1.2 | 58 | 66 |

The 29 failures on master by cause: FK/OneToOne target `Any` (8); `<field>_id` `Any` (5);
`<field>_id` with `to_field` missing (3); `pk` through a relation key (4); `book.author = None`
unchecked (1); date-string assignment now legal, an improvement (1); nullable date navigation,
the literal bug (2); explicit parent link fields, ordinary OneToOne causes (5).

On 6.1.2 the 66 are: scalar values `Unknown` (23), automatic `id`/`pk` `Unknown` (7), scalar
assignment checks lost (3), relations (21), multi-table section (12). The literal bug does not
occur there because 6.1.2 has `null: bool`.

## 6. State of the maintainer's draft (#29731)

**What it does** (READ, S1; base `8d25f7d53b`, 5 files, +119/-32, two commits of 2026-10-26):

- Adds a constructor special case in `call/bind/constructor.rs`: when `ForeignKey`'s type
  arguments are unsolved, take them from the `to` argument, unioned with `None` if `null=True`
  (new `foreign_key_model_type` in `django.rs`).
- Replaces the `related_model` lookup with a call to the field's `__get__`.
- Repins the mdtest to
  `git+https://github.com/UnknownPlatypus/django-stubs.git@5f2e45ba31627b7c821a4247fe6cf82eb5d487d0`.
- sharkdp's inline note says the special case "could be removed" with upstream FK work (S3).

**Measured at PR head** (R2): builds; `external/django.md` passes. FK by class gives `Author` /
`int`, nullable gives `Author | None` / `int | None`, FK to a `CharField` key gives `str`. The
same binary under django-types 0.24.0 gives the same FK results.

**What it does not cover** (MEASURED, R2): `OneToOneField` (value, `_id`, `pk` all `Any`;
`book.cover = 1` unchecked); nullable date navigation (error lost; the draft marks it TODO);
string targets (value `Any`, and `| None` dropped for `null=True`); reverse accessors.

**Staleness** (READ, S1): 492 commits behind main. Main has since gained #29744 (abstract
models), #29769 (Meta override), #29785 (FK/OneToOne as primary key), #29944 (rename
`unresolved-attribute` to `missing-attribute`), #30419.

**Rework list.** All of the following comes from a scratch worktree and patches under
`/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r2`. Nothing was pushed
or posted (R2).

1. `django.rs` imports: keep main's, add `use crate::types::call::Binding;`.
2. `django.rs` `foreign_key_id_type` (main 344-380): the merged hunk references `class`, removed
   by #29785. Add a `class: StaticClassLiteral` parameter and update two callers (main 292, 340).
   About 6 lines. The compile error was identified by reading (INFERRED, R2).
3. `constructor.rs`: `static_class_literal` no longer exists; use `class_literal` (main 393).
4. `bind.rs`: the visibility change merges cleanly.
5. `django.md`: two conflicts (rule rename in date navigation; link after "Abstract models").
   Repin and regenerate `django.lock`.

With 1-5 only, tests fail on OneToOne-as-key (6 assertions) and nullable date navigation (2).

**Two extra fixes that make all current tests pass at upstream `2c8f775`** (MEASURED, R2):

6. Match `ForeignKey` subclasses (scan the class's ancestors) instead of the exact class. About
   4 lines.
7. Compare with `.as_bool_literal() == Some(true)` instead of `== Type::bool_literal(true)`. 2
   lines.

Not done: no full workspace tests, clippy, or prek; no check of effects on non-Django code or
performance; mdtest not run against master `44457d47` (R2).

**Interaction with #30068** ("Allow resetting automatic Django primary keys", `5057e05728`, 312
commits behind main; READ, S1; MEASURED, R2): it does not compile on main (needs `origin,` for a
new `TypeOrigin` field, main `attribute_write.rs:248-252`) and conflicts with #29731 in one line.
Once fixed, `book.pk = None` and `book.id = None` are accepted under django-stubs. Its two
assertions that `book.pk = "invalid"` and `book.id = "invalid"` error then fail, because
`AutoField`'s set type default is `int | str`.

## 7. Bugs and risks the research exposed

| # | Finding | Evidence |
|---|---|---|
| 1 | **Literal-`True` comparison.** `Field::from_definition` tests `== Type::bool_literal(true)`, which builds a promotable literal. When the stub parameter is `null: Literal[True]`, the argument infers as `Bool(true, LiteralFlags(0x0))`; for `null: bool` it is `Bool(true, PROMOTABLE)`. Result: `get_next_by_<nullable>()` is wrongly synthesized. | MEASURED, R3 (debug print); fix MEASURED, R2. R2 inferred the mechanism; R3 observed it, so R3 is better supported. |
| 2 | The same `==` guards `primary_key` and, on our branch, `parent_link`. Both work today only because the stubs type those parameters `bool`. | READ, R2, R3 |
| 3 | `OneToOneField` is not covered by the draft's exact-class match. | INFERRED, S1; MEASURED, R2 |
| 4 | `<field>_id` with `to_field` becomes a false missing-attribute with unchanged ty code. | MEASURED, R1, R3. Not probed on the draft. |
| 5 | String targets: `foreign_key_model_type` returns nothing, so `null=True` loses `\| None` on the value. | MEASURED, R2 |
| 6 | Metaclass `__getattr__`: `Author.nonexistent` reports invalid-attribute-access ("Expected `Literal["objects"]`, found `Literal["nonexistent"]`") and still reveals `Manager[Author]`. | MEASURED, R1 |
| 7 | `AutoField` accepts `str`: `book.id = "1"` is legal. | MEASURED, R2 |
| 8 | Runtime Django enters the test environment (lock adds `django`, `asgiref`, `sqlparse`, `tzdata`, others). The Django mdtest takes about 47s instead of 3s. | MEASURED, R3; READ, S1 |
| 9 | The draft's pinned commit `5f2e45ba` still installs by hash but is no longer the head of any ref in the fork. | MEASURED, R2 |
| 10 | Scalar checks loosen (`title = 3` accepted). This is the stubs' choice, not a ty bug. | MEASURED, R1 |
| 11 | Ecosystem run on the draft: 9 added, 5 removed, 4 changed `unresolved-attribute` in zulip; unexplained. | READ, S3 |

## 8. What users would have to change

| Area | Change | Source |
|---|---|---|
| Install | Uninstall django-types first; `pip install django-stubs` (no `[compatible-mypy]`). Python >=3.11. Runtime `django` and `django-stubs-ext` come along. | READ, R4 |
| Scalar annotations | `CharField[str]` works on master but is invalid-type-arguments on 6.1.2. | MEASURED, R1 |
| Annotated nullable fields | `x: models.IntegerField = models.IntegerField(null=True)` is rejected upstream. | READ, S2, R4 |
| ForeignKey annotations | `ForeignKey[Book]` still works; nullable is `ForeignKey[Book \| None]`. | READ, R4; MEASURED, R1 |
| Reverse managers | Import from `django_stubs_ext.db.models.manager`; `ManyToManyRelatedManager` becomes `ManyRelatedManager`. Neither side's path resolves under the other. | MEASURED, R1; READ, R4 |
| Managers and querysets | `Manager` is no longer a `QuerySet`; `ValuesQuerySet` is gone. | READ, S2 |
| User model | `get_user_model()` is `type[AbstractBaseUser]`; `.username` needs narrowing. | MEASURED, R1 |
| Choices | `.choices`, `.values`, `.label` types change. | MEASURED, R1 |
| Custom Field subclasses | Must declare type parameter defaults or redefine overloads. | READ, R4 |
| Hand-written `id: int`, `<fk>_id: int` | Redundant but harmless. | INFERRED, R4 |

**Third-party stubs** (READ, R4): `djangorestframework-stubs` 3.18.2 requires `django-stubs>=6.1.2`
and collides with django-types today; after the switch it becomes co-installable.
`djangorestframework-types` 0.9.0 (2024-10-10) is stale. `django-filter-stubs` 0.1.3 requires
django-stubs. Packages that subclass fields or use `_pyi_private_*` need migration (django-mysql
is named in #3763).

**Editor tooling** (READ, R4): Pylance bundles django-types, not django-stubs (Microsoft
statement of 2024-06-18, pylance-release#6029); it can be overridden with
`python.analysis.stubPath`. S3 could not confirm basedpyright's bundling.

## 9. What ty's docs and tests would need

Lines of `docs/features/third-party/django.md` in astral-sh/ty that become wrong (READ, R4):

- Line 3 and Setup (70-75): package name and `uv add --dev django-types`.
- Line 79: the note that django-stubs support is "planned"; invert it.
- Line 47 (`book.title = 3  # error: [invalid-assignment]`) and "Assignments" (92-96): false,
  since the `CharField` set type is `str | int`.
- Lines 102-110: the `ForeignKey[Book]` example still parses; a nullable example needs
  `Book | None`.
- Line 112 (reverse relations): add the `django_stubs_ext` manual declaration.
- Likely new limitations: `WithAnnotations`, `from_queryset`, custom Field subclasses,
  `get_user_model()`.

**Effect on docs PR #5081.** No researcher read its diff (gap). It edits this same page, so any
text it adds about setup, assignments, or the FK limitation is written against django-types and
needs a second pass at switch time (INFERRED).

**Tests.** Repin `django.md:11` and regenerate the lock. Update assertions for date strings. Our
branch's test lines differ by one from main's (R2: OneToOne 233-235 and 258-260, date navigation
412-413; R3: 234-241 and 259-265, 413-414). Candidate new cases: `Literal[True]` metadata,
OneToOne, `to_field`, string targets, `AutoField` assignment. django-stubs' own suite
(`tests/assert_type`, 165 files) runs ty 0.0.105 in CI; the plugin suites in `tests/typecheck`
never run under ty (READ, R5).

## 10. Upstream dependencies and timing

- **Release.** None scheduled. ngnpope, 2026-11-13: "Maybe we should have a single breaking
  release that gets everything sorted?" The next version is probably a major (INFERRED, R4).
- **ForeignKey overloads.** Listed as a follow-up to #3763; not opened as of 2026-11-21. Master
  still has a single non-overloaded `__init__` (READ, R4).
- **`_ST`/`_GT` order.** ngnpope: "It's a shame that the first type var is for the setter and the
  second for the getter." Deferred, unresolved (READ, R4, S3).
- **django-types.** No statement on deprecation or merging back. 41 unreleased commits since
  0.24.0, several named "sync with django-stubs" (READ, R4). UnknownPlatypus hopes the projects
  can merge back together (READ, S3).
- **pyrefly** recommends django-stubs and still reads `_pyi_private_*` (pyrefly#5532); master
  keeps a shim on `AutoField` for it (READ, R4).
- **Upstream's record of ty gaps** (R5): 243 lines carry `# ty: ignore`. R5 counts 98
  type-assertion-failure entries among 247 rule entries; S2 and R4 report 96, which matches R5's
  stripped run on ty 0.0.107 (96 of 242 diagnostics). Pyright has 254 ignore lines, pyrefly 173.
  137 of the 243 are deliberate negative tests; 106 are real divergence: Choices attributes
  (about 52), `choices=<Choices class>` (8, astral-sh/ty#4551), `apps.get_model` (8), nullable
  Field subclasses (11), forward FK (3), implicit `id` (1). Nothing was fixed between ty 0.0.105
  and 0.0.107 (MEASURED, R5).

## 11. Decisions the maintainers have to make

1. **One package or both?** sharkdp has said nothing about supporting both (READ, R4). Evidence
   for feasibility: the draft binary gave correct FK results under django-types 0.24.0 (MEASURED,
   R2). Evidence for cost: two test environments, and django-types main drifts from 0.24.0
   (INFERRED, R4).
2. **Detect which is installed?** Both ship `django-stubs/`, so detection must use stub shape:
   field arity, `__new__` versus `self`-annotated `__init__`, `ManyRelatedManager` existence,
   `ModelBase.__getattr__` (INFERRED, R4).
3. **When to switch.** Options: wait for the release (ngnpope, 2026-10-23: "Probably worth waiting
   until the field changes land"); pin a git commit in tests only; or switch docs now. Evidence
   against switching docs before a release: users on 6.1.2 get `Unknown` everywhere (MEASURED,
   R1, R3).
4. **What to do for 6.1.2.** Options: document a minimum version; emit a diagnostic; read
   `_pyi_private_*` (the approach of closed ruff#29675, which sharkdp did not want; READ, S3).
5. **ForeignKey special-casing in ty or wait for upstream overloads?** Without it, relations are
   `Any` (MEASURED, R1). Even with overloads, `<fk>_id`, `to_field`, and string targets need ty
   logic (INFERRED from R1, R3).
6. **Extend the special case to subclasses?** Required for main's OneToOne tests (MEASURED, R2).
   User-defined non-generic FK subclasses were not probed.
7. **Narrow `AutoField`'s set type?** Otherwise `book.id = "x"` is legal and #30068's assertions
   must drop (MEASURED, R2).
8. **Accept looser scalar assignments?** `title = 3` passes under master (MEASURED, R1).
9. **Metaclass `__getattr__` diagnostics.** Special-case or leave the confusing message (R1).
10. **Test cost.** About 47s versus 3s for the Django mdtest (MEASURED, R3).

## 12. What this means for our work

**Parent-link branch** (MEASURED, R3, at `25bb62e`):

- Stub-independent under both django-stubs versions: all `<parent>_ptr` types, all
  missing-attribute assertions (proxy, abstract, wrong name, explicit `parent_link`), `Meta.proxy`
  inheritance. `parent_link_member` (`django.rs:434-473`) never touches field stubs.
- `<parent>_ptr_id`: all seven assertions pass on master; all seven are `Unknown` on 6.1.2.
- The five explicit `parent_link=True` assertions fail under both, for ordinary OneToOne reasons.
- Risk: the `parent_link` check uses the fragile `==` comparison (finding 2). Using
  `as_bool_literal()` on the branch is within its own scope and avoids a future break.
- Released ty 0.0.107 reports missing-attribute for `book_ptr` (R1), so the feature is still new.

**Docs PR #5081**: see section 9. Keeping it scoped to behaviour that holds under both packages
would reduce later rework (INFERRED).

**Ranked contributions that do not compete with the draft:**

| Rank | Action | Evidence | Needs maintainer agreement first? |
|---|---|---|---|
| 1 | File the literal-comparison bug as an astral-sh/ty issue, with a minimal reproduction. | R2, R3 | No. It reproduces only with unreleased stubs, so say so. Check for duplicates. |
| 2 | Report the measured findings on #29731 or ty#1018: OneToOne gap, rework list, `to_field`, string targets, `AutoField`, test time, stale pin. | R1, R2, R3 | Ask sharkdp where he wants it; do not push code to his draft. |
| 3 | Offer to rebase or extend the draft. | R2 patches | Yes, explicitly. |
| 4 | Contribute the ForeignKey overloads follow-up, or FK test cases, to django-stubs. | R4: not opened; invited by UnknownPlatypus | Coordinate with django-stubs maintainers; tell sharkdp, since it affects his special case. |
| 5 | Fix `as_bool_literal()` in ty as a one-behaviour PR. | R2: 2 lines | Yes; it touches code the draft also edits. |
| 6 | Issue for the metaclass `__getattr__` message. | R1 | No, but it only appears under django-stubs. |
| 7 | Verify fixes as they land by rerunning the probes. | R1, R2 scratch | No. |

A person must write all issue and PR text. Scratch patches are evidence, not submissions.

## 13. Open questions and gaps

- Next django-stubs version and date; whether it waits for FK overloads or the `_ST`/`_GT` swap.
- Whether ty will support django-types during a transition, and for how long.
- Full review threads of #3763 (including sharkdp's `related.pyi` comments), all of ty#1018's
  comments, ruff#29732, typeddjango Discussions, pylance-release#8083, zuban Django docs: not
  loaded. The #29731 description and CI status: only the diff and bot summary were seen.
- The diff of docs PR #5081 was not read.
- The 9 added zulip diagnostics on the draft (`named_user_group`) are unexplained.
- Whether `<fk>_id` with `to_field` works on the draft; `ManyToManyField` beyond one probe;
  `"app.Model"` targets in the mdtest; user-defined FK subclasses: not tested.
- Effect of `Any` versus `Unknown` on other ty diagnostics: not examined.
- Whether #4932 (`pk = None`) is fixed by the switch alone: no; it needed #30068 (R2).
- No full test suite, clippy, or performance run on the merged scratch tree.
- S1 read django-types from its main branch (the 0.24.0 tag returned 404); S2 read the 0.24.0
  wheel and is the better source for that version. R3 did not open the django-types stub.
- `request.user` in django-types 0.24.0: R1 measured `AbstractUser | AnonymousUser`; R4 had it
  open.
- Lockfile Django version: S1 and S3 read 6.1.2 in the draft's lock; R3's regenerated locks have
  6.1.3. These are different lock dates, not a contradiction.
- Pyright and pyrefly were not run; mypy was not compared.

## 14. Sources

**ty and ruff**
- https://github.com/astral-sh/ruff/pull/29731 (head `00d0e60200`), /pull/30068 (`5057e05728`),
  /pull/29642, /pull/29675; main `cd2d973241`; our branch `25bb62e`; ty builds `c068ccdd0`, 0.0.105,
  0.0.107
- https://github.com/astral-sh/ty/issues/1018, /4932, /4977, /4551 (not looked up)
- https://raw.githubusercontent.com/astral-sh/ty/main/docs/features/third-party/django.md
- `/home/user/ruff/crates/ty_python_semantic/src/types/dedicated/django.rs`
- `/home/user/ruff/crates/ty_python_semantic/resources/mdtest/external/django.md`
- `/home/user/ruff/crates/ty_test/README.md`; refs in `/home/user/ty/ruff`

**Stub packages**
- https://github.com/typeddjango/django-stubs (master `44457d4`; #3763 = `2c8f775`; release 6.1.2)
- https://github.com/typeddjango/django-stubs/pull/3763
- https://github.com/sbdchd/django-types (main `25e39e1`; release 0.24.0), /issues/361, /pull/424
- https://pypi.org/pypi/django-stubs/json, https://pypi.org/pypi/django-types/json

**Other checkers and ecosystem**
- https://pyrefly.org/en/docs/django/, https://github.com/pyrefly-org/pyrefly/issues/5532
- https://github.com/microsoft/pylance-release/issues/6029
- https://raw.githubusercontent.com/hauntsaninja/mypy_primer/master/mypy_primer/projects.py

**Local evidence**
- Reports: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/reports/`
  (S1, S2, S3, R1-R5)
- `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/out/matrix.md` and
  `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/probe.py`
- `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r2/merge-resolution.patch`
- `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r2/merge-experiments.patch`
- `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r2/pr30068.patch`
- `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r3/master.failures.txt`
- `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r3/rel612.failures.txt`
- `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r5/strip107.txt`
- `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/collectB/` (stub
  clones and wheels)

## TL;DR

The switch is cheap in ty's code but depends on an unreleased django-stubs, loses all relation
types without ty special-casing, and exposed a real ty bug in literal comparison. The most useful
non-competing step is to report the measured findings and the bug to the maintainer and ask where
he wants help.
