## R5 - ty's gaps with django-stubs, as recorded by upstream's `# ty: ignore` comments

Clone: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/collectB/stubs-main` (44457d4). Paths below are relative to it; test paths are relative to `tests/assert_type/`.

### 1. Configuration
- CI: `.github/workflows/test.yml:229-254`, job `run-ty`, Python 3.12, `uv sync --no-dev --group ty`, then `ty check tests/assert_type`.
- Pin: `pyproject.toml:71-75`, `ty==0.0.105` (pyright 1.1.414, pyrefly 1.4.1 at `:63-70`).
- ty config is only `pyproject.toml:130-135`: `[tool.ty.terminal] error-on-warning = true` and `[tool.ty.analysis] respect-type-ignore-comments = false`. No rules are disabled and no paths excluded; there is no `ty.toml`.
- `.github/workflows/remove-unused-ignores.yml:17-33` runs `uv run ty check --fix tests/assert_type || true` on `renovate/ty-*` branches, so stale ignores are stripped at each ty bump.
- `README.md:11-14`: mypy "full and complete support ... with our custom mypy plugin"; pyright, pyrefly, ty each "basic support, checked in CI".
- `README.md:455`: "pyright, pyrefly and ty see `Product.objects` as an unparametrized `Manager` here" (for `from_queryset` + `WithAnnotations`).
- `README.md:660`: "pyright, pyrefly and ty do not run the plugin, so under those you declare them yourself" (reverse accessors, as `RelatedManager[Model]`).
- ty only checks the 165 `.py` files in `tests/assert_type`. The 62 mypy-plugin YAML suites in `tests/typecheck` are never run under ty.

### 2. Counts
243 lines carry `# ty: ignore`, all in `tests/assert_type` (plus one doc example at `CONTRIBUTING.md:131`), with 247 rule entries.

| Rule | Count |
|---|---|
| type-assertion-failure | 98 |
| invalid-argument-type | 60 |
| invalid-assignment | 35 |
| no-matching-overload | 20 |
| missing-attribute | 9 |
| invalid-explicit-return | 4 |
| unsupported-operator, incompatible-property-override, deprecated | 3 each |
| incompatible-mutable/method/attribute-override | 2 each |
| unknown-argument, not-subscriptable, missing-typed-dict-key, invalid-attribute-access | 1 each |

Top files: `db/models/test_enums.py` 49, `contrib/admin/test_options.py` 14, `fields/test_custom_fields` 13, `fields/test_fields_base` 10, then `test_ordering`, `test_aggregates`, `fields/test_fields_nullable`, `apps/test_registry` at 8 each.

137 of the 243 lines also carry a mypy `# type: ignore`. Those are deliberate negative tests (bad arguments, bad assignments) where every checker is meant to error, so they are not ty gaps. The remaining 106 lines are where ty diverges from mypy+plugin: 81 type-assertion-failure, 9 invalid-argument-type, 9 invalid-assignment, 3 invalid-explicit-return, 4 other.

### 3. Categorised gaps
Counts are from my hand grouping of those 106 lines and sum to about 108, so treat each as within one or two. "ty infers" values come from running ty 0.0.107 on a scratch copy with the ty ignores stripped.

| Category | Count | Example and what ty infers | Reason stated in code? |
|---|---|---|---|
| `Choices` `.labels` / `.choices` / `.label` / `.values` / `.value` | 52 | `db/models/test_enums.py:178` expects `list[str]`, ty gives `list[str \| _StrPromise]`; `:165` expects `list[int \| None]` (`__empty__`), ty gives `list[int]`; `:210` expects `bytes`, ty gives `Any` | No comment; pyright ignores the same lines |
| `choices=<Choices class>` rejected | 8 | `db/models/fields/test_choices.py:43` `models.CharField(choices=Kind)`; `forms/test_fields_choices.py:68` | Yes: `test_choices.py:41` "ty drops `type[Choices]` from the union: astral-sh/ty#4551" |
| `apps.get_model("app.Model")` | 8 | `apps/test_registry/models.py:23` expects `type[First]`, ty gives `type[Any]` | No; plugin-only |
| Forward ForeignKey / OneToOne target | 3 | `db/models/fields/test_related_forward/models.py:30` `Book().author` expects `Author`, ty gives `Any`; `contrib/test_models.py:18` `LogEntry().user` expects `User`, ty gives `AbstractBaseUser` (swappable user) | No |
| Implicit `id` | 1 | `db/models/fields/test_fields_base/models.py:33` `NoPrimaryKey().id` expects `int`; ty reports missing-attribute as well | No |
| `null=True` on Field subclasses, or fields with no null overload | 11 | `fields/test_fields_nullable/models.py:113` expects `str \| None`, ty gives `str`; `:60` generic subclass with no TypeVar defaults gives `Unknown`; `fields/test_fields_base/models.py:275` JSONField expects `Any \| None` | Yes: `:112` "only the plugin can widen it"; `:57-59` "pyrefly and ty still solve `null=True` from the inherited self-annotated overload, pyright doesn't" |
| CompositePrimaryKey `pk` | 1 | `fields/test_composite_pk/models.py:15` expects `tuple[Any, ...]`, ty gives `Any` | No |
| Generic ty behaviour: literal promotion, `Unknown` leaking | 12 | `utils/test_datastructures.py:24` expects `str \| int`, ty gives `str \| Literal[1]`; `:25` `getlist` gives `list[str] \| Unknown`; `:40` `d.dict()` gives `Unknown`; `contrib/staticfiles/test_finders.py:23` `find(..., find_all=True)` gives `Unknown`; `utils/test_encoding.py:35` gives `Literal["foo"]` | No |
| Overload or descriptor evaluation | 2 | `test_shortcuts.py:33` `redirect(permanent=<bool var>)` expects the union, ty picks `HttpResponsePermanentRedirect`; `apps/test_config.py:41` gives `str \| _Getter[str]` | No |
| Admin | 7 | `contrib/admin/test_options.py:227` `actions = [func, method]` not assignable to `Sequence[Callable[[Self, ...]] \| str]`; `:137` and `:151` ty flags the whole assignment where others flag the inner item | No |
| Override checks, misc | 3 | `db/migrations/test_classvar.py:9`; `utils/test_functional.py:36`; `db/models/test_constraints.py:11` (`fields=["name"]` expects `None`) | No |

Also: `db/models/test_manager_access/models.py:105` `Node().children` gives a union `_ManagerIsNotAccessibleViaInstances | Manager[Node, ...]` where other checkers report `deprecated`. On `:67-68` (`Category().objects`) ty needs no ignore while pyright and pyrefly both carry a `deprecated` ignore.

**What the list does not cover.** `tests/assert_type` has no assertions on `values()` / `values_list()` rows, `annotate`, `WithAnnotations` or `get_user_model`. Lines mentioning `<fk>_id`, `from_queryset`, `as_manager` and `request.user` exist and carry no ty ignores. The plugin-heavy cases live in `tests/typecheck`, which ty never sees, so the ignore list understates the gap for those features.

### 4. Comparison with pyright and pyrefly
| | ty | pyright | pyrefly |
|---|---|---|---|
| Lines with an ignore | 243 | 254 | 173 |
| Assertion-failure ignores | 98 | 96 | 36 |

- Line overlap: 27 ty lines have no pyright ignore, 82 have no pyrefly ignore, and 23 are ty-only. In reverse, 38 pyright lines and 12 pyrefly lines have no ty ignore.
- pyright's other main rules: reportArgumentType 71, reportAttributeAccessIssue 27, reportCallIssue 20, reportAssignmentType 17, reportUnknownMemberType 15. pyrefly's: bad-argument-type 69, no-matching-overload 20, bad-assignment 15.
- ty-only failures (23): `choices=<Choices class>` (8), literal promotion / `Unknown` in `MultiValueDict`, `QueryDict`, `force_str`, finders (12), admin `fieldsets` / `formfield_overrides` / `actions` (3).
- ty passes where pyright fails: `null=True` through an inherited self-annotated overload (`fields/test_fields_nullable/models.py:61,63,129`), `Choices.__empty__` (`db/models/test_enums.py:172,186,226,248`), `_default_manager` (`db/models/test_model_base.py:24-25`), and pyright's strict-mode-only rules.
- pyrefly passes where ty fails: nearly all of `test_enums.py` (6 pyrefly ignores against 49), forward FK (`test_related_forward:30-31`), and implicit `id` (`test_fields_base:33`).
- Overall, ty is roughly level with pyright and about 70 lines behind pyrefly, almost entirely on enums, forward FK and `id`.

### 5. Running ty locally
- Setup: Python 3.12 venv at `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r5/venv`, with the clone, `ext/`, django, psycopg2-binary and types-psycopg2 installed. This was a non-editable `uv pip install`, not `uv sync`, so dependency versions are not the lockfile's.
- `ty check tests/assert_type --python <venv>` from the clone: "All checks passed!" on both ty 0.0.105 and 0.0.107.
- On 0.0.107 with `--error unused-ignore-comment` it still passes. No ignore has become stale and there are no new errors, so nothing in this list is fixed between 0.0.105 and 0.0.107.
- Stripped copy (ty ignores removed, in `scratchpad/r5/strip`, clone untouched) on 0.0.107: 242 diagnostics. That is 96 type-assertion-failure, 60 invalid-argument-type, 35 invalid-assignment, 20 no-matching-overload, 8 missing-attribute, 4 invalid-explicit-return, 3 deprecated (warnings), and the rest at 3 or fewer each. Output is in `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r5/strip107.txt`.

### Sampled versus fully read
- Read as grep lines: every ty-ignore line in `db/models/fields/**`, `test_manager*`, `test_query*`, `test_ordering`, `test_aggregates`, `apps`, `contrib/auth`, `contrib/postgres`, plus all 106 non-mypy lines.
- Read with ty's actual diagnostic: all 96 assertion failures.
- Read with surrounding code: about 15 sites.
- Not individually read: the roughly 60 mypy-ignored negative-test lines outside those directories (forms, template, middleware, migrations, the rest of admin).
- Not done: the stripped copy was not run on 0.0.105; pyright and pyrefly were not run; astral-sh/ty#4551 was not looked up.