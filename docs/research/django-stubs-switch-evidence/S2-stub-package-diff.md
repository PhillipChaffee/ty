## collectB - django-types vs django-stubs: packaging and stub-level differences

Scratch root (all paths below are under it): `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/collectB/`
Dirs: `types-whl/` (django-types 0.24.0), `stubs-whl/` (django-stubs 6.1.2), `stubs-main/` (django-stubs master), `types-main/` (django-types main), `ext-whl/` (django-stubs-ext 6.1.2). File paths below are relative to each dir's `django-stubs/`.

### Answer
Released django-stubs 6.1.2 is worse than django-types for a plugin-less checker: field type vars have no defaults and `null=True` is plugin-only. PR #3763 (merged 2026-11-19, unreleased) fixes that for scalar fields via PEP 696 defaults plus `__init__` overloads with a `self:` annotation. Foreign keys are still `Any` without the plugin on django-stubs master; django-types infers them from `to`. `Model.objects` also moves from a `ClassVar` to a metaclass `__getattr__`.

### Packaging
| | django-types | django-stubs |
|---|---|---|
| Latest release | 0.24.0, 2026-04-22 | 6.1.2, 2026-10-05 |
| Releases in last 12 months | 2 (0.23.0, 0.24.0) | 15 (5.2.8 to 6.1.2) |
| Main HEAD | `25e39e1`, 2026-10-29 | `44457d4`, 2026-11-21 |
| Commits since 2025-11-21 | 51 | more than 400 (my fetch depth capped at 400, oldest 2026-05-12) |
| requires-python | >=3.10 | >=3.11 |
| Dependencies | `types-psycopg2>=2.9.21.13` | `django`, `django-stubs-ext>=6.0.2`, `types-pyyaml`, `typing-extensions>=4.11.0`; extra `compatible-mypy` = `mypy>=1.13,<2.5` |
| Installs | `django-stubs/` only | `django-stubs/` and `mypy_django_plugin/` |
| Django support | no classifiers or table | 6.1 full; 6.0 and 5.2 partial (README table, 6.1.2 row) |

- Both install the same top-level `django-stubs/` directory, so they cannot coexist in one environment.
- django-stubs pulls in Django itself at runtime; django-types does not.
- `RelatedManager` import path differs: django-stubs users import from `django_stubs_ext.db.models.manager` (re-exports from `django.db.models.fields.related_descriptors`); django-types users import from `django.db.models.manager`.

### a) `db/models/fields/__init__.pyi`
| | django-types 0.24.0 | django-stubs 6.1.2 | django-stubs master |
|---|---|---|---|
| `Field` | `Generic[_ST, _GT]` (L34) | `Generic[_ST, _GT]`, no defaults (L53-57) | `Generic[_ST_contra, _GT_co]`, both `default=Any` (L52-53, L79) |
| `__set__` | `value: _ST` (L65) | `value: _ST` (L184) | `value: _ST_contra \| Combinable` (L189) |
| `__get__` on class | `-> Self` (L68) | `-> _FieldDescriptor[Self]` (L187) | same (L193) |
| `__get__` on instance | `-> _GT` | `-> _GT` | `-> _GT_co` |
| `IntegerField` | `Generic[_I], Field[_I \| Combinable, _I]`, `_I` bound `int \| None` (L115-117) | `Field[_ST, _GT]` plus `_pyi_private_set_type`/`_pyi_private_get_type` (L277-280) | `Field[_ST_Int_contra, _GT_Int_co]`, defaults `float \| int \| str` and `int` (L285-288) |
| `null=True` | `__new__` overloads: `null: Literal[False]` returns `IntegerField[int]`, `Literal[True]` returns `IntegerField[int \| None]` (L119 onward) | plugin only | 4 `__init__` overloads (L290-342); the nullable one is `self: IntegerField[float \| int \| str \| None, int \| None]` with `null: Literal[True]`; a `null: bool` overload is `@deprecated` |
| `CharField` | one param `_C` bound `str \| None` (L698-700) | two params, no defaults (L339) | defaults `str \| int` and `str` (L757-760) |
| `DateField` | one param `_DD` (L1189-1193) | two params (L525) | defaults `str \| date` and `date` (L1317-1320) |
| `DateTimeField` | `DateField[_DT]` (L1335) | `DateField[_ST, _GT]` (L591) | defaults `str \| real_datetime \| date` and `real_datetime` (L1452-1455) |
| `AutoField` | `IntegerField[int]`, not generic (L602) | `IntegerField[_ST, _GT]` (L685) | defaults `int \| str` and `int` (L1731-1734); keeps `_pyi_private_*` "for pyrefly" (L1736-1738) |
| `related_model` on `Field` | `Any \| None` (L45) | `type[Model] \| None` (L126) | same (L145) |

- Constructor kwargs on master go through `**kwargs: Unpack[FieldInitKwargs]`, a `closed=True` TypedDict (PEP 728) at L60. Its comment says this makes ty reject unknown keys.
- Field arity changes from 1 to 2 params. User annotations like `CharField[str]` mean something different, and set-types widen: `IntegerField` accepts `float | int | str` on assignment, where django-types accepted `int | Combinable`.

### b) `db/models/fields/related.pyi`
| | django-types 0.24.0 | django-stubs master (6.1.2 is the same shape) |
|---|---|---|
| `ForeignKey` | `Generic[_M], ForeignObject[_M]`, `_M` bound `Model \| None` (L72, L165) | `ForeignObject[_ST_contra, _GT_co]`, `_ST` `default=Any`, `_GT` `default=_ST` (L43-44, L159) |
| `to` parameter | `type[_M] \| str` (L174) | `type[Model] \| str`, not linked to any type var (L166) |
| Nullable FK | `__new__` overloads return `ForeignKey[_M]` (L206) or `ForeignKey[_M \| None]` (L242) | single `__init__` with `null: bool = False` (L164-183); no overloads |
| Instance `__get__` | `-> _M` (L248) | `-> _GT_co` (L120), which is `Any` unless explicitly subscripted |
| Class `__get__` | `ForwardManyToOneDescriptor`, non-generic (L245) | `ForwardManyToOneDescriptor[Self]` (L115) |
| `related_model` | attribute `type[_M]` (L170) | `@property -> type[Model]` on `RelatedField` (L71) |
| `OneToOneField` | `Generic[_M], ForeignKey[_M]` (L253) | `ForeignKey[_ST_contra, _GT_co]` (L215) |
| `ManyToManyField` | `Generic[_MM, _MN], RelatedField[Sequence[_MN], ManyToManyRelatedManager[_MM, _MN]]` (L344); `through: type[_MN]` (L364) | `RelatedField, Generic[_To, _Through]`, `_Through` `default=Any` (L256-259); `through: type[_Through] \| str \| None` (L278); `__get__` on instance returns `ManyRelatedManager[_To, _Through]` (L313) |

- Manager class name differs: `ManyToManyRelatedManager` in `db/models/manager.pyi` (django-types L67) versus `ManyRelatedManager` in `db/models/fields/related_descriptors.pyi` (django-stubs master L168).
- `RelatedManager` lives at `manager.pyi` L43 in django-types and at `related_descriptors.pyi` L107 in django-stubs master, where it is `Generic[_To, _To_QS_co]`.

### c) `db/models/base.pyi`
| | django-types 0.24.0 | django-stubs 6.1.2 and master |
|---|---|---|
| `objects` | `objects: ClassVar[BaseManager[Self]]` on `Model` (L28) | not declared on `Model`; `ModelBase.__getattr__(cls: type[_Self], name: Literal["objects"]) -> Manager[_Self]` (L54) |
| `_default_manager` | `ClassVar[BaseManager[Self]]` (L27) | `@property` on the metaclass returning `Manager[_Self]` (L49-50); `_base_manager` likewise |
| `DoesNotExist` | `ClassVar[type[ObjectDoesNotExist]]` (L24) | `Final[type[ObjectDoesNotExist]]` (L64); adds `NotUpdated` |
| `pk` | `Any` | `Any` |
| `id` | absent | absent |
| `__init__` | `(*args: Any, **kwargs: Any)` | same |
| `_meta` | `ClassVar[Options[Self]]` | same |
| Bases | `metaclass=ModelBase` | `AltersData, metaclass=ModelBase` |

django-types main (unreleased) has also moved `objects` to the metaclass, as a `_DefaultManager` descriptor (`types-main/django-stubs/db/models/base.pyi` L25-36).

### d) `manager.pyi` and `query.pyi`
| | django-types 0.24.0 | django-stubs 6.1.2 | django-stubs master |
|---|---|---|---|
| `QuerySet` | `QuerySet[_T]` over `_BaseQuerySet[_T]` (query L180) | `Generic[_Model, _Row]`, `_Row default=_Model` (L80) | same (L82) |
| `BaseManager` | subclasses `QuerySet[_T]` (manager L11) | `Generic[_T]`, not a `QuerySet` (L14) | `Generic[_T_co, _QS_co]`, `_QS_co default=QuerySet[_T_co]` (L14, L26) |
| `Manager.filter` / `all` | inherited, `-> Self` | `-> QuerySet[_T]` (L132) | `-> _QS_co` (L151) |
| `values()` | `ValuesQuerySet[_T, dict[str, Any]]` (query L120-122) | `QuerySet[_Model, dict[str, Any]]` (L189) | same (L200) |
| `values_list()` | `ValuesQuerySet[_T, Any]` | `QuerySet[_Model, Any]` | same (L202-204) |
| `as_manager()` | `Manager[_T]` | `Manager[_Model]` | `Manager[_Model_co, Self]` (L95) |

- `ValuesQuerySet` does not exist in django-stubs.
- django-stubs master adds a manager `__get__` whose instance-access overload is `@deprecated` and returns `_ManagerIsNotAccessibleViaInstances` (manager L52-59).
- Master splits slice `__getitem__` into `Self` versus `list[_Row_co]` (query L109-113).

### e) auth, settings, request
- `get_user_model()` returns `type[AbstractUser]` in django-types (`contrib/auth/__init__.pyi` L38) and `type[AbstractBaseUser]` in django-stubs (`_UserModel`, `contrib/auth/models.pyi` L19-21). So `.username` and `.email` are lost without the plugin.
- `HttpRequest.user` is `_AnyUser` in both. That alias is `AbstractUser | AnonymousUser` in django-types (`contrib/auth/models.pyi` L14) and `AbstractBaseUser | AnonymousUser` in django-stubs (L23).
- `AbstractUser` fields are assignments in django-types (`username = models.CharField(max_length=150)`, L113) and annotations in django-stubs master (`username: models.CharField[str | int, str]`, L113).
- `settings` is `LazySettings` with `__getattr__ -> Any` in both.

### f) `db/models/enums.pyi`
| | django-types 0.24.0 | django-stubs (6.1.2 and master identical) |
|---|---|---|
| `TextChoices` bases | `(str, Choices)` | `(Choices, StrEnum, metaclass=_TextChoicesType)` |
| `.choices` | `Sequence[tuple[_EnumMemberT, str]]`, tuples of the enum member | `list[tuple[str, _StrOrPromise]]` |
| `.values` | `Sequence[_EnumMemberT]` | `list[str]` |
| `.label` | `@property -> str` | `enum.property -> _StrOrPromise` |
| `.labels` | `list[str]` | `list[_StrOrPromise]` |

### PR #3763
- Merged 2026-11-19 as `2c8f775` by Thibaut Decombe (UnknownPlatypus): 42 files, +3048 / -514. It is not in 6.1.2.
- Stub changes, from the commit message and stat:
  - each field gets its own defaulted type params;
  - `null` is resolved by `__init__` overloads;
  - `_pyi_private_set_type` and `_pyi_private_get_type` are dropped, except on `AutoField`;
  - `Combinable` moves into `Field.__set__`;
  - redundant `__set__` overrides on related fields are removed;
  - `ArrayField` reads element types from `base_field`;
  - gis and citext fields get the same treatment;
  - the plugin now reads the PEP 696 defaults.
- Follow-ups, breaking changes and review discussion below come from a WebFetch model summary of the PR page, not the raw text:
  - Follow-ups: foreign key overloads; `FilePathField` defaults; `RasterField`, `HStoreField` and `GeometryField` still `Any`; pyrefly and zuban issues to stop using `_pyi_private_*`; migration PRs for `django-mysql` and similar; plugin code deletion.
  - Breaking: `x: models.IntegerField = models.IntegerField(null=True)` is now rejected; bad kwargs report `call-overload` instead of `arg-type`.
  - It fixes #766, #1264 and #2724, and supersedes #3317 and #1900.
  - sharkdp linked astral-sh/ruff#29675 and #29731; astral-sh/ty#4977 was closed as intended.
- README (master L736-737): pyright, and mypy without the plugin, do not solve a subclass's type params from inherited `self`-annotated overloads (pyright#11989, mypy#22395). Custom field subclasses must redeclare the overloads there.

### Statements about other checkers
- django-stubs README L10-14: "mypy: full and complete support ... pyright: basic support, checked in CI; pyrefly: basic support, checked in CI; ty: basic support, checked in CI".
- CI runs `ty check tests/assert_type` (`.github/workflows/test.yml` L253) with ty pinned at 0.0.105. `tests/assert_type` contains 243 `# ty: ignore` comments, 96 of them `type-assertion-failure`.
- django-stubs README L660: "pyright, pyrefly and ty do not run the plugin, so under those you declare them yourself" (reverse relations).
- django-types README: "forked from django-stubs with the goal of removing the mypy plugin dependency ... and that non-mypy type checkers like pyright will work better with Django". It never mentions ty or pyrefly.
- The django-stubs README does not mention django-types.

### (1) Inference changes for unannotated model code (django-types 0.24.0 to django-stubs master)
- `ForeignKey(Other, ...)` and `OneToOneField(...)` instance access goes from `Other` (or `Other | None`) to `Any`, unless ty special-cases it.
- Scalar field get-types are unchanged (`int`, `str | None`, and so on); set-types widen.
- `null=some_bool` hits a deprecated overload.
- `Model.objects` and `_default_manager` become `Manager[Self]` via the metaclass, where they were `BaseManager[Self]`.
- `Manager` is no longer a `QuerySet` subtype.
- `.values()` returns `QuerySet[M, dict[str, Any]]`.
- `get_user_model()` and `request.user` narrow to `AbstractBaseUser`.
- `TextChoices.choices` element type changes.
- M2M accessor is `ManyRelatedManager[To, Through]`.
- Class-level field access returns `_FieldDescriptor[Self]`, not the field.

### (2) Names ty's Rust code might key on
- Module paths are unchanged for `Model` (`django.db.models.base`), `AutoField`, `DateField`, `Field` (`django.db.models.fields`) and `ForeignKey` (`django.db.models.fields.related`).
- Changed:
  - type-param count and meaning on every field and on FK;
  - `related_model` goes from a generic attribute `type[_M]` to a property returning `type[Model]`;
  - `ManyToManyRelatedManager` becomes `ManyRelatedManager`, in a different module;
  - `RelatedManager` moves module;
  - `ValuesQuerySet` is removed;
  - `objects` is no longer a class attribute on `Model`;
  - `DoesNotExist` is `Final`, not `ClassVar`;
  - `_BaseQuerySet` is gone;
  - nullability moves from `__new__` return types to `__init__` `self` annotations;
  - `AutoField` becomes generic.

### (3) Still `Any` or plugin-only in django-stubs master
- FK and O2O target types, and FK nullability.
- `<fk>_id`, `id`, and `pk` (`Any`).
- Reverse accessors.
- `get_<field>_display`.
- Typed `Model.__init__`, `create` and `filter` kwargs.
- `values`/`values_list` row types.
- `from_queryset`, `WithAnnotations`.
- Swappable user model.
- `settings.X`.
- Per-model `DoesNotExist` hierarchy.
- `RasterField`, `HStoreField`, `GeometryField`.

### Confidence and gaps
- **Confidence:** high for stub contents and PyPI facts, which I read directly; medium for the PR body, follow-ups and review discussion.
- **Not obtained:** the raw PR description and `.diff`. `curl` returned 403 through the proxy, and `gh` and the GitHub MCP are not enabled for typeddjango/django-stubs. I used the squash commit in the clone plus the WebFetch summary instead.
- **Not verified:** I ran no type checker, so the "inference changes" are read off the stubs, not from ty output. In particular I did not test whether ty honours a metaclass `__getattr__` with `name: Literal["objects"]`, or `self`-annotated `__init__` overloads.
- django-types main differs a lot from 0.24.0 (two-param `QuerySet` and `Manager`, metaclass `objects`, type-var defaults); I only skimmed it.

### Sources
- https://pypi.org/pypi/django-types/json, https://pypi.org/pypi/django-stubs/json, https://pypi.org/pypi/django-stubs-ext/json
- https://github.com/typeddjango/django-stubs (clone at `44457d4`; commit `2c8f775`)
- https://github.com/sbdchd/django-types (clone at `25e39e1`)
- https://github.com/typeddjango/django-stubs/pull/3763 (WebFetch summary)