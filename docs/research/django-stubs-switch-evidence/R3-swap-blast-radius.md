## R3 - Blast radius of swapping django-types for django-stubs with ty's Rust code unchanged

### Answer
With only the stub package swapped, the Django mdtest (124 assertions: 88 `revealed`, 36 `error`) goes from 124/124 passing to:

| Package | Pass | Fail | Multi-table section (39 assertions) |
|---|---|---|---|
| `django-types==0.24.0` (baseline) | 124 | 0 | 39 pass |
| django-stubs master `44457d4` | 95 | 29 | 34 pass, 5 fail |
| `django-stubs==6.1.2` (released) | 58 | 66 | 27 pass, 12 fail |

- **On master**, everything that breaks is relation-related (ForeignKey/OneToOneField), plus one exposed ty bug in date navigation and one TODO that resolves itself.
- **On 6.1.2**, every scalar field value type also collapses to `Unknown`, because the field type variables have no defaults there.
- **The multi-table inheritance logic from our branch is stub-independent.** Its only failures are inherited from scalar or relation typing, not from the `_ptr` synthesis.

### Setup, commands, versions
- Worktree at `25bb62e` (detached), built with `CARGO_TARGET_DIR=<scratch>/r3/target`, uv 0.13 venv first on PATH.
- Baseline: `MDTEST_EXTERNAL=1 cargo test -p ty_python_semantic --test mdtest -- mdtest::external/django.md` gave `1 passed`.
- Master run: header changed to `dependencies = ["django-stubs @ git+https://github.com/typeddjango/django-stubs.git@44457d47e03845c27b560936ef0455d5dfc7b7d8"]`. `git ls-remote` confirms this is current master, identical to the local clone.
- Released run: header changed to `dependencies = ["django-stubs==6.1.2"]`.
- Lock regeneration (README "Lockfiles", `crates/ty_test/src/external_dependencies.rs:77`): the same cargo command with `MDTEST_UPGRADE_LOCKFILES=1` added.
- Both new locks pull in real `django 6.1.3`, `django-stubs 6.1.2`, `django-stubs-ext 6.1.2`, `asgiref 3.13.0`, `sqlparse 0.6.1`, `types-pyyaml`, `typing-extensions 4.16.0` and `tzdata`. On master, `django-stubs-ext` comes from the git `ext` subdirectory. The old lock had only `django-types` and `types-psycopg2`.
- The run takes about 47s instead of 3s, since the real Django is copied into the in-memory filesystem.

### Failures on django-stubs master (29)

**A. ForeignKey/OneToOne target not inferred (8): lines 234, 239, 259, 263, 286, 289, 334, 355.**
- Expected `Book` / `Author` / `Author | None`; actual `Any`.
- The stub declares `to: type[Model] | str` (`related.pyi:164-166`), and the type variables default to `Any` (`related.pyi:43-44`), so the field is `ForeignKey[Any, Any]` and `__get__` returns `_GT_co` (`related.pyi:120`).
- ty has no code for this; it relied entirely on django-types.

**B. `<field>_id` degrades to `Any` (5): lines 235, 240, 287, 336, and 290 (`Any | None`, expected `int | None`).**
- `foreign_key_id_type` reads `related_model` (`django.rs:400-405`), which is now a property returning `type[Model]` (`related.pyi:71`).
- It then looks up `pk` on bare `Model`, which is declared `pk: Any` (`base.pyi:69`).
- A probe shows that even an explicit `ForeignKey[Author, Author]` gives `typed_id: Any`, because `related_model` is not generic.

**C. `<field>_id` with `to_field` becomes a false `missing-attribute` (3): lines 260, 264, 357.**
- Expected `str`; actual `Unknown` plus "has no attribute `book_id`".
- `Model` has no `isbn`, so the lookup at `django.rs:407-411` returns `None`. This is worse than B because it is a new false positive.

**D. `pk` through a relation primary key (4): lines 236, 241, 261, 265.**
- Expected `UUID` / `str`; actual `Any`.
- `primary_key_member` (`django.rs:328-331`) calls `foreign_key_id_type`, giving `Any` as in B. With `to_field` it falls back to `field.ty`, which is also `Any`.

**E. Relation assignment check lost (1): line 293.**
- `book.author = None` no longer errors, because the set type is `Any`.

**F. Date-string assignment (1): line 55.**
- The expected `invalid-assignment` is gone because the stub allows `str | date` (`fields/__init__.pyi:1317`). The existing TODO resolves; this is an improvement.

**G. Date navigation on nullable fields (2): lines 413, 414.**
- `get_next_by_reviewed()` is now wrongly synthesized as `(**kwargs: Any) -> Article`. This is a latent ty bug, not a stub gap.
- `django.rs:92-94` tests `definition_expression_type(..) == Type::bool_literal(true)`.
- Master's scalar `__init__` overloads declare `null: Literal[True]` (`fields/__init__.pyi:310`). I confirmed with a temporary debug print (since reverted) that the argument then infers as `Bool(true, LiteralFlags(0x0))`.
- For ForeignKey, where the parameter is `null: bool` (`related.pyi:178`), it infers as `Bool(true, PROMOTABLE)`, so the equality holds there and line 290 still gets `| None`.
- The fix is to compare with `as_bool_literal()`-style matching. The same fragile `==` is used for `primary_key` and `parent_link`, which currently work only because those parameters are typed `bool`.

**H. Multi-table "Explicit parent link" (5): lines 780, 794, 805, 820 (cause A) and 781 (cause B).**

**Passing on master:** Basic model reveals and scalar assignment checks (59, 60), Nullable fields (106-107, via the `self`-annotated overloads), Field names, all non-relation primary-key sections, Choices, the rest of Date navigation, all Abstract/Meta sections, and all `<parent>_ptr` / `_ptr_id` assertions.

### Failures on released django-stubs 6.1.2 (66)
The relation failures are the same lines as A-E and H, but the target reveals as `Unknown` instead of `Any`. Group G does not occur, because 6.1.2 has no `Literal[True]` overloads (`null: bool`). The additional failures all come from `_ST`/`_GT` having no defaults in 6.1.2 (`fields/__init__.pyi:53-55` at tag `6.1.2`). The mypy plugin reads `_pyi_private_get_type` instead (e.g. lines 340-341), so ty sees `CharField[Unknown, Unknown]`.

- **Scalar value types become `Unknown` (23):** lines 43, 44, 45, 106, 107, 177, 178, 192, 210, 211, 257, 381, 475, 476, 480, 481, 482, 583, 584, 585, 587, 588, 589.
- **Automatic `id`/`pk` become `Unknown` (7):** lines 152, 153, 163, 473, 474, 497, 498. `django.rs:340-343` synthesizes an `AutoField` instance, which is `AutoField[Unknown, Unknown]`; on master it is `AutoField[int | str, int]`.
- **Scalar assignment checks lost (3):** lines 55, 59, 60.
- **Relations (21):** the lines of groups A-E above.
- **Multi-table (12):** the five explicit-link lines, plus `_ptr_id` lines 612, 628, 630, 648, 669, 671, 706, which are `Unknown` because the parent's `pk` is `Unknown`.

### Multi-table inheritance section (our branch)
- **Stub-independent under both versions:** all `<parent>_ptr` reveals (`Book`, `AudioBook`, `Product`, `Ebook`), all `missing-attribute` assertions for proxy, abstract, wrong-name and explicit-`parent_link` cases, and `Meta.proxy` inheritance. `parent_link_member` (`django.rs:434-473`) builds the parent instance type from class bases and `Meta`, and never touches field stubs.
- **`<parent>_ptr_id`:** this is `parent.pk` (`django.rs:466-469`), so it is exactly as good as scalar `pk`. All seven pass on master and all seven are `Unknown` on 6.1.2.
- **Explicit `parent_link=True` fields:** 780, 794, 805, 820 and 781 fail under both versions. They are ordinary OneToOneField accesses (causes A and B), not parent-link logic. The suppression of `book_ptr` in those blocks still passes.

### Stub-independent versus stub-sensitive
- **Independent (AST and class-structure driven):** model detection, `Meta.abstract`/`proxy`, presence or absence of `id`/`pk`, the `name=` override, the existence of `get_*_display` and of `get_next_by_*` / `get_previous_by_*` for non-nullable date fields, `_ptr` existence and type, and the suppression rules.
- **Sensitive:**
  - every type that flows through a field's `__get__`/`__set__` (scalar values, `pk`, the automatic `AutoField`, `_ptr_id`);
  - the `related_model` lookup, which is unusable with django-stubs in any version;
  - relation target inference, which is absent in django-stubs;
  - the literal-equality metadata checks, which depend on the parameter annotation.

### Confidence and gaps
- **Confidence:** high; all counts come from actual runs.
- **Not done:** I did not open the django-types stub to cite its `related_model: type[_M]` line; that shape is taken from your brief. Every other citation in this report was read directly.
- **Not tested:** `ManyToManyField`, managers/querysets beyond one probe, and string `to="app.Model"` references, since django.md does not cover them.
- **Probe extras (master):** class-level access gives `_FieldDescriptor[DateField[str | date, date]]`, and `Article.objects` is `Manager[Article, QuerySet[Article, Article]]`.

### State
The worktree was removed. `/home/user/ruff` is clean on `phillip/django-parent-link` at `25bb62e`. The debug edit existed only in the removed worktree.

### Sources
- Stub checkout: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/collectB/stubs-main` (`django-stubs/db/models/fields/related.pyi`, `fields/__init__.pyi`, `base.pyi`; tag `6.1.2` via `git show`)
- `/home/user/ruff/crates/ty_python_semantic/src/types/dedicated/django.rs`
- `/home/user/ruff/crates/ty_python_semantic/resources/mdtest/external/django.md`
- `/home/user/ruff/crates/ty_test/README.md`

Files are in `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r3`:
- baseline.log
- master.log
- master.failures.txt
- rel612.log
- rel612.failures.txt
- probe_body.md
- probe.master.log
- probe.612.log
- probe.master.debug.log
- django.master.md
- django.master.lock
- django.612.md
- django.612.lock