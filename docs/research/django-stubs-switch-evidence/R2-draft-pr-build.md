## R2 - Empirical state of draft PR astral-sh/ruff#29731 (django-types → django-stubs) and cost of bringing it to main

Scratch root (all paths below): `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r2` (= `$S`). Nothing was pushed or posted. `/home/user/ruff` was not touched; `/home/user/ty/ruff` only gained two registered worktrees (`$S/pr`, `$S/merge`).

### Answer
- The PR head (00d0e60200) builds and its Django mdtest passes.
- A merge onto main (cd2d973241) has 2 textual conflicts and 2 compile errors, about 15 lines of mechanical Rust rework.
- After that mechanical fix, exactly two mdtest sections fail under django-stubs: "ForeignKey and OneToOneField as primary keys" (OneToOne lines only) and "Date navigation" (nullable date fields).
- Both have small root-cause fixes that I prototyped (about 6 lines in total). With them, every test on main passes under django-stubs at upstream 2c8f775.
- PR #30068 does not compile on main either (1 error). Once fixed, its None-widening works with django-stubs, but two of its own assertions fail because django-stubs' `AutoField` accepts `str`.

### What I ran
All builds used `CARGO_TARGET_DIR=$S/target` and the `uv` from the given venv first on PATH.

1. **PR head** (`git worktree add --detach $S/pr refs/scratch/pr29731`):
   - The PR's `rust-toolchain.toml` pins 1.99.0, which is not installed, so I built with `RUSTUP_TOOLCHAIN=1.100.0-x86_64-unknown-linux-gnu`. It compiled without errors.
   - `MDTEST_EXTERNAL=1 cargo test -p ty_python_semantic --test mdtest -- mdtest::external/django.md` gave `1 passed; 0 failed`. Log: `$S/pr-mdtest.log`.
   - `cargo build --bin ty` succeeded; binary copied to `$S/bin/ty-pr`.
   - The fork rev 5f2e45ba still installs by SHA, but it is no longer any ref head in the fork (`git ls-remote`), and upstream `refs/pull/3763/head` is now e868e4a, so the pin is an unreferenced commit.
2. **Probe**: `$S/probe/src/probe.py`, run as `ty check --python <venv> --output-format concise`.
   - Venvs: `$S/probe/venv-stubs` (django 6.1.3 + django-stubs master 44457d47), `venv-fork` (PR pin; output identical to master), `venv-types` (django-types 0.24.0).
   - Outputs: `$S/probe/{pr-stubs,pr-fork,pr-types}.out`, `merge-*.out`, `merge2-*.out`, `merge3-stubs.out`.
3. **Merge**: `git worktree add --detach $S/merge refs/scratch/main`, then `git merge --no-commit refs/scratch/pr29731`.
   - I resolved the conflicts, repinned to `typeddjango/django-stubs.git@2c8f77563617ce1e9a295beeadd48facd7d12af1`, and regenerated the lock with `MDTEST_EXTERNAL=1 MDTEST_UPGRADE_LOCKFILES=1 cargo test …` (the second documented command in `crates/ty_test/README.md`).
   - Mechanical resolution: `$S/merge-resolution.patch`; test log `$S/merge-mdtest.log`.
   - Resolution plus experimental fixes plus #30068: `$S/merge-experiments.patch`; test log `$S/merge3-mdtest.log`.

### Behaviour table (django-stubs master; probe line numbers)

| Construct | PR head | main+PR, mechanical | + prototype fixes | django-types (PR binary) |
|---|---|---|---|---|
| `Book.author` (class access) | `ForwardManyToOneDescriptor[ForeignKey[Author, Author]]` | same | same | `ForwardManyToOneDescriptor` |
| FK by class: `book.author` / `author_id` | `Author` / `int` | same | same | same |
| FK `null=True`: `editor` / `editor_id` | `Author \| None` / `int \| None` | same | same | same |
| FK to model with `CharField` pk: `publisher_id` | `str` | same | same | `str` |
| FK by string `"Author"`: value / `_id` | `Any` / `Any` | same | same | `Unknown` / `Unknown` |
| FK by string, `null=True`: value / `_id` | `Any` / `Any \| None` | same | same | `Unknown \| None` both |
| `OneToOneField(Author)`: value / `_id` | **`Any` / `Any`** | same | `Author` / `int` | `Author` / `int` |
| `OneToOneField(null=True)`: value / `_id` | **`Any` / `Any \| None`** | same | `Author \| None` / `int \| None` | same as fixed |
| OneToOne as pk: `profile.author` / `author_id` / `pk` | **`Any` ×3** | `Any` ×3 | `Author` / `int` / `int` | `Author` / `int` / `Author` (main binary: `int`) |
| FK as pk to `CharField`-pk model: `edition.pk` | `Publisher` (pre-#29785) | `str` | `str` | `Publisher` (main binary: `str`) |
| `ManyToManyField(Tag)` | `ManyRelatedManager[Tag, Any]` | same | same | `ManyToManyRelatedManager[Tag, Unknown]` |
| `CharField` / `IntegerField` / `DateField` / `DateTimeField` with `null=True` | `str \| None`, `int \| None`, `date \| None`, `datetime \| None` | same | same | same |
| `get_next_by_<nullable date>()` | **no error** | no error | `missing-attribute` | error |
| `book.cover = 1` (OneToOne) | **no error** | no error | error | error |
| `book.author = None` (non-null FK) | error | error | error | error |
| `book.id = "1"` | accepted (`int \| str \| Combinable`) | accepted | accepted | error |
| `book.pk = None` / `book.id = None` | error | error | accepted (with #30068) | error |
| Reverse `author.book_set` | unresolved | unresolved | unresolved | unresolved |

### Root causes (verified)
- **OneToOneField is not covered.** The special case uses the exact match `class.is_known(db, KnownClass::DjangoForeignKey)` (PR `constructor.rs`, hunk at ~515). `OneToOneField(ForeignKey[_ST, _GT])` therefore keeps the TypeVar defaults (`Any`). An MRO scan for `DjangoForeignKey` instead fixes value, `_id`, pk and assignment checking; this was tested.
- **Nullable `get_next_by_` lost its error.** `Field::from_definition` compares `definition_expression_type(..) == Type::bool_literal(true)` (main `django.rs:92-94`), and `bool_literal` builds a *promotable* literal (`types.rs:3469`).
  - django-stubs overloads `DateField.__init__` on `null: Literal[True]`. A debug print showed the stored argument type displays as `Literal[True]`, yet the equality fails.
  - Switching to `.as_bool_literal() == Some(true)` restores the error. So the cause is the promotable-vs-contextual literal distinction; I inferred that from the fix working and did not inspect the representation.
  - `ForeignKey.__init__` has plain `null: bool`, which is why FK nullability still worked. The same fragile comparison is in the PR's `foreign_key_model_type` and for `primary_key` (`django.rs:79-85`), which is currently harmless because the stubs use `primary_key: bool`.
- **String targets.** `foreign_key_model_type` returns `None` when `to` is a `str`, so even the `| None` is dropped from the value type for `null=True`.

### Rework list to bring #29731 onto main
1. `crates/ty_python_semantic/src/types/dedicated/django.rs`, import conflict (main lines 9-10): keep main's `place_from_bindings` and `nearest_enclosing_class`, and add the PR's `use crate::types::call::Binding;`.
2. `django.rs`, `foreign_key_id_type` (main 344-380): the PR's `__get__` replacement auto-merges but references `class`, which #29785 removed. This is a compile error I identified by reading, not by compiling.
   - Add a `class: StaticClassLiteral` parameter and update the two callers (`primary_key_member`, main line 292, passing `base`; `foreign_key_id_member`, line 340). About 6 lines.
   - The stale django-types comment at 359-363 is replaced by the PR's.
3. `crates/ty_python_semantic/src/types/call/bind/constructor.rs`: the PR hunk auto-merges after `let Some(types) = types else` (main line 504) but uses `static_class_literal`, which no longer exists.
   - Main's `instance_return_specialization` (382 onwards) binds `class_literal` at line 393; use `class_literal.is_known(..)`. One line.
   - The closure also gained an `explicit_return` parameter, which the hunk does not interact with.
4. `bind.rs`: the `parameter_type_by_name` visibility change (main line 9791) merges cleanly.
5. `resources/mdtest/external/django.md`, two conflicts:
   - Date navigation (main ~409-413): rule name is now `missing-attribute`; keep main's error assertions if fix 7 is applied, otherwise the PR's TODO.
   - File tail: keep all of main's "Abstract models" sections and swap the link reference to `[django-stubs]`.
   - Repin and regenerate `django.lock`.
6. Needed for main's #29785 tests (md lines 233-235 and 258-260 reveal `Any`): widen the ForeignKey check to subclasses, about 4 lines.
7. Needed for main's date-navigation assertions (md 412-413): `as_bool_literal()` comparison, 2 lines.

Results on main + PR at 2c8f775:
- Mechanical only (items 1-5): the abstract-model sections (Basic, Annotated abstract setting, Inherited Meta configuration, Multiple inheritance), automatic/custom/explicit pk, foreign-key IDs, choices, and ForeignKey-as-pk pass. Failures are OneToOne-as-pk (6 assertions) and nullable date navigation (2).
- With 6 and 7: all pass.

### PR #30068 under django-stubs
- It is based on 324bcac22e, 312 commits behind main.
- It does not compile on main: `ExplicitAttributeWriteRequirement::AssignableTo` gained an `origin: TypeOrigin` field (main `attribute_write.rs:248-252`), so the PR's new return needs `origin,` added. It also has a one-line conflict with #29731 at the `foreign_key_id_type` call.
- With that fixed, under django-stubs `book.pk = None` and `book.id = None` are accepted.
- Its assertions `book.pk = "invalid"` and `book.id = "invalid"  # error: [invalid-assignment]` (md 164-165) fail. django-stubs declares `AutoField` with `_ST_Auto_contra` default `int | str`, so the write domain is `int | str | Combinable | None`. Those two lines would need dropping, or ty would have to narrow the set type itself.
- Under django-types the same build gives `int | Combinable | None` and rejects `"1"`.

### Confidence and gaps
- **Confidence:** high for everything run; medium for the precise mechanism of the literal mismatch.
- Not done:
  - No full mdtest or workspace test run, clippy, or prek.
  - No check that the constructor special case or the MRO scan affects non-Django code or performance.
  - The un-resolved merge was not compiled; the two compile errors are from inspection.
  - The PR was not built with its pinned 1.99.0 toolchain.
  - The mdtest was not run against django-stubs master 44457d47 (only the probe was).
  - `Meta` invalid-override suppression (#29769) lives in `overrides/attributes.rs`; it was exercised only through the passing `django.md` sections.
  - User-defined non-generic `ForeignKey` subclasses were not probed.

### Sources
- `/home/user/ty/ruff` refs `refs/scratch/{pr29731,main,pr30068}`
- Worktrees `$S/pr` and `$S/merge`
- Logs `$S/pr-mdtest.log`, `$S/pr-build.log`, `$S/merge-mdtest.log`, `$S/merge3-mdtest.log`
- Patches `$S/merge-resolution.patch`, `$S/merge-experiments.patch`, `$S/pr30068.patch`
- Probe `$S/probe/src/probe.py`, `$S/probe/src/p2.py`, `$S/probe/*.out`
- Stubs: `$S/probe/venv-stubs/lib/python3.13/site-packages/django-stubs/db/models/fields/{__init__,related}.pyi`
- https://github.com/typeddjango/django-stubs (master 44457d47; 2c8f7756 = #3763)