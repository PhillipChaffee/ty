## collectA - Code evidence for ty's django-types -> django-stubs switch

Refs fetched into `/home/user/ty/ruff` (checked-out commit `0528644c0d` untouched): `refs/scratch/main` = `cd2d973241` (2026-11-20), `refs/scratch/pr29731` = `00d0e60200`, `refs/scratch/pr30068` = `5057e05728`. Citations are for main unless noted. I did not build ty or run any mdtest; behaviour claims come from reading code and stubs.

### Answer
On main, ty's hard dependency on django-types is small: one `related_model` lookup in `django.rs`, plus the mdtest pin and one TODO. Everything else keys on module paths and class names that both stub packages share. PR #29731 is 5 files, +119/-32. It replaces the `related_model` lookup with a descriptor `__get__` call and adds a constructor special case for `ForeignKey`, because django-stubs' `ForeignKey.__init__` does not bind the field's type parameters from `to`. The PR is 492 commits behind main, conflicts textually in 2 files, and its auto-merged `django.rs` would not compile.

### 1. django-types dependencies on main
- **`related_model` lookup (the only stub-shape dependency in Rust)** - `crates/ty_python_semantic/src/types/dedicated/django.rs:359-369`. Comment: "django-types represents a foreign key declared with `null=True` as `ForeignKey[Author | None]`, so its `related_model` attribute has type `type[Author | None]`". Code: `field_ty.member(db, env, "related_model")` -> `to_instance_approximation` -> strip `None`, then look up `pk` or `to_field` on the model (370-379).
  - django-types (its `main` branch; the 0.24.0 tag 404'd): `class ForeignKey(ForeignObject[_M], Generic[_M])`, `related_model: type[_M]`, overloaded `__new__` with `to: type[_M] | str` and `null: Literal[False]`.
  - django-stubs fork at the pinned rev: `class ForeignKey(ForeignObject[_ST, _GT])`, a single non-overloaded `__init__(self, to: type[Model] | str, ..., null: bool = False)`, and `related_model` is a `cached_property -> type[Model]` (`related.pyi:73,164-188`). The model type is therefore lost.
- **Automatic primary key** - `django.rs:303-306` resolves `AutoField` in `django.db.models.fields` and uses its instance as a descriptor. django-stubs has `AutoField(..., IntegerField[_ST_Auto, _GT_Auto])` with typevar defaults `int | str` / `int`.
- **Explicit `id`/`pk` check** - `django.rs:272-280` skips `Model` itself. django-stubs declares `pk: Any` on `Model` (`base.pyi:69`), which this skip already tolerates.
- **Stub-agnostic logic** - field metadata (`null`, `primary_key`, `choices`, `to_field`, `name`) is read syntactically from call keywords (`django.rs:71-102`), not from stub types.
- **Known classes/modules** - `known.rs:166-169, 1216-1219, 1658-1660, 1894-1896, 1911` (`Model` in `django.db.models.base`, `Field`/`DateField` in `.fields`, `ForeignKey` in `.fields.related`); `ty_module_resolver/src/module.rs:280-285, 345-347, 382-384`; `slots.rs:180-183`. Both packages use these paths and names.
- **Other consumers** - `static_literal.rs:1877` (`django::synthesized_member`); `overrides/attributes.rs:466-475` (`Meta` exemption via `django::is_model`). Neither depends on stub shape.
- **No Django references** in `types/call/`, `attribute_write.rs`, `ty_ide`, `ty_python_core`, `ty_server`, `ty_project` on main.
- **mdtest** - `resources/mdtest/external/django.md:3` ("relies on the stubs from [django-types]"), `:11` (`dependencies = ["django-types==0.24.0"]`), `:54-55` (TODO plus `book.published = "1980-10-12"  # error: [invalid-assignment]`), `:592` (link). `django.lock:6-7,22,26` pins django-types 0.24.0 with types-psycopg2.

### 2. PR #29731
Base is `8d25f7d53b` (#29729, 2026-10-26); both commits by David Peter, 2026-10-26, empty bodies.

**Commit `8c694178fe` "Infer Django foreign key types from the target model"** (3 files, +42/-13)
- `call/bind.rs`: `Binding::parameter_type_by_name` changes from private to `pub(in crate::types)` (+1/-1).
- `call/bind/constructor.rs` (+13/-3), inside the per-overload class-argument combination, after the "end TODO" block:
  ```rust
  if let [write, read] = types.as_mut_slice()
      && (write.is_none() || read.is_none())
      && static_class_literal.is_some_and(|class| class.is_known(db, KnownClass::DjangoForeignKey))
      && let Some(model) = django::foreign_key_model_type(db, env, overload)
  { write.get_or_insert(model); read.get_or_insert(model); }
  ```
  This is new constructor special-casing; none existed before.
- `dedicated/django.rs` (+28/-9):
  - New `pub(in crate::types) fn foreign_key_model_type(db, env, binding: &Binding) -> Option<Type>` reads the bound `to` argument, takes `to_instance_approximation`, and unions with `None` when the bound `null` argument is `Literal[True]`. Doc comment: "django-stubs annotates `ForeignKey.__init__`'s `to` parameter as `type[Model] | str`."
  - The django-types comment and `.member("related_model")` are removed. The replacement builds an instance of the owning model and calls `field_ty.try_call_dunder_get(db, env, Some(instance), instance.to_meta_type(..))`, taking `.return_type` with `None` filtered out.

**Commit `00d0e60200` "Switch the Django mdtest to django-stubs field overloads"** (2 files, +77/-19)
- `django.md` (+8/-8):
  - Line 3: `[django-types]` -> `[django-stubs]`.
  - Line 11: `dependencies = ["django-stubs @ git+https://github.com/UnknownPlatypus/django-stubs.git@5f2e45ba31627b7c821a4247fe6cf82eb5d487d0"]`.
  - TODO removed; `book.published = "1980-10-12"  # error: [invalid-assignment]` -> `book.published = "1980-10-12"` (no error).
  - Regression: `# Date fields with null=True do not generate these methods.` plus two `# error: [unresolved-attribute]` lines on `article.get_next_by_reviewed()` / `get_previous_by_reviewed()` -> `# TODO: Report unresolved-attribute for both calls...` with no error.
  - Link target -> `https://github.com/typeddjango/django-stubs`.
  - No `# revealed:` line changed.
- `django.lock` (+69/-11): removes django-types 0.24.0 and types-psycopg2. Adds django-stubs 6.1.2 and django-stubs-ext 6.1.2 (both git sources at that rev), plus runtime `django` 6.1.2, asgiref, sqlparse, tzdata, types-pyyaml, typing-extensions. The runtime Django package is now installed in the test environment.

**Staleness and conflicts**
- 492 commits behind main. Main commits since the base that touch the Django files: `731a26b88f` (#29744 abstract models), `4160aece36` (#29769 Meta override), `19db56ae3e` (#29785 FK/OneToOne as primary key), `ce0077c3e5` (#29944, renames `unresolved-attribute` -> `missing-attribute`), `244668339a` (#30419).
- `git merge-tree` reports conflicts in:
  - `django.rs`: import block only.
  - `django.md`: the nullable-date hunk (main now says `# error: [missing-attribute]`) and the trailing link after main's new "Abstract models" section.
- `bind.rs` and `constructor.rs` auto-merge.
- **Semantic conflict:** #29785 extracted `foreign_key_id_type(db, env, field, specialization)` (main `django.rs:344-349`), which has no `class` parameter. The PR's auto-merged hunk references `class.apply_optional_specialization(...)` there, so it will not compile without rework. The function is now also called from `primary_key_member` (`:292`).
- **Likely gap:** the special case uses `is_known(DjangoForeignKey)`, an exact match. `OneToOneField(ForeignKey[_ST, _GT])` has its own non-overloaded `__init__(to: type[Model] | str, ...)` in django-stubs, so main's OneToOne primary-key tests (`django.md:214-266`, added after the PR base) are probably not covered. Inferred, not run.

### 3. PR #30068
`5057e05728` "[ty] Allow resetting automatic Django primary keys" (1 commit on base `324bcac22e`, 2026-11-05; 3 files, +62/-5; 312 commits behind main; not merged).
- `django.rs`: `primary_key_member` now returns a new `enum PrimaryKeyMember { Automatic(Type), Explicit(Type) }`; adds `pub(in crate::types) fn is_automatic_primary_key_member`.
- `attribute_write.rs` (~line 785): for an automatic `id`/`pk`, widens the descriptor's `__set__` domain with `None`.
- `django.md`: adds `book.pk = None`, `book.id = None`, and `book.pk = "invalid"  # error: [invalid-assignment]`.
- Merges cleanly into main. Merging it with #29731 conflicts in `django.rs` and `django.md`.
- It relies on `descriptor_setter_domain` of `AutoField`, so it is stub-shape sensitive: django-stubs' `_ST_Auto` defaults to `int | str`, which would make `book.pk = "invalid"` legal. What django-types declares for `AutoField` was not checked.

### 4. Open questions
1. Why do nullable date fields lose the `get_next_by_*` error under django-stubs? `date_navigation_method` still returns `None` on syntactic `null=True`, and the fork's `Model` has no `__getattr__`. Needs an mdtest run on the PR branch, or the PR discussion.
2. Is rev `5f2e45ba` the head of typeddjango/django-stubs#3763, what does that PR change (the `null: Literal[True]` overloads with `self: DateField[... | None, ... | None]`?), and will it merge and release?
3. Do unchanged `# revealed:` lines actually pass with django-stubs (e.g. `book.title -> str`, nullable `CharField -> str | None`, `book.author = None` error)? This depends on ty honouring `self`-annotated `__init__` overloads and typevar defaults.
4. String or lazy `to` references (`"app.Model"`, `"self"`): `foreign_key_model_type` returns nothing for a `str`. What does the field become?
5. Should `OneToOneField` (and `ManyToManyField`, which has `_To`/`_Through`) get the same treatment?
6. Users with django-types installed: both distributions install a top-level `django-stubs` directory. After the switch, `related_model` is no longer read, and the constructor hook only fires when class arguments are unsolved. Is dual support intended?
7. Does ty need the runtime `django` package now that the lock adds it? How does stub versus runtime resolution interact?
8. django-stubs expects its mypy plugin to remove `DoesNotExist`, `pk: Any` and similar from abstract models (`base.pyi:58-69`), and to supply reverse accessors and `objects` (via the `ModelBase.__getattr__` trick). What must ty re-implement?
9. Ecosystem impact and maintainer rationale are not in the code.

### Confidence & gaps
- **Confidence:** high for the diffs, citations and conflict analysis; medium for behavioural inferences (OneToOne gap, the `int | str` setter domain).
- **Unverified:** nothing was compiled or run. The django-types stubs were read from its `main` branch, not 0.24.0. PR descriptions, review comments, CI status and draft state were not read (git refs only). The `.diff` URL fallback was not needed.

### Sources
- `/home/user/ty/ruff` refs `refs/scratch/main`, `refs/scratch/pr29731`, `refs/scratch/pr30068`
- https://raw.githubusercontent.com/UnknownPlatypus/django-stubs/5f2e45ba31627b7c821a4247fe6cf82eb5d487d0/django-stubs/db/models/{base.pyi,fields/__init__.pyi,fields/related.pyi}
- https://raw.githubusercontent.com/sbdchd/django-types/main/django-stubs/db/models/fields/{related.pyi,__init__.pyi}
- Downloaded copies: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/collectA/dl/`