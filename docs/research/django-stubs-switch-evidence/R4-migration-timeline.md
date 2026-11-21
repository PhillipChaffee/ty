## R4 - What a ty switch from django-types to django-stubs involves (release timing, user migration, ecosystem, other checkers, ty docs)

Paths: `STUBS` = `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/collectB/stubs-main` (HEAD 44457d4, 2026-11-21), `TYPES` = `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/collectB/types-main` (HEAD 25e39e1, 2026-10-29), wheels in `.../collectB/stubs-whl` (6.1.2) and `.../collectB/types-whl` (0.24.0).

### Answer
django-stubs has not released #3763 and nobody has named a version or date. The ForeignKey follow-up is not opened. A ty user who migrates today faces real source changes (FK annotations, manager imports, custom fields, new install requirements), and ty itself must special-case FKs until upstream adds FK overloads.

### 1. Release timing (verified)
- **No release, milestone or version statement.** Latest release is still 6.1.2 (2026-10-05), with no draft or pre-release (https://github.com/typeddjango/django-stubs/releases). #3763 has no milestone or labels.
- **The README only says "unreleased".** The compatibility table row reads `unreleased | 1.16 - 2.4 | 6.1 | 6.0, 5.2 | 3.11 - 3.15` (`STUBS/README.md:66`); `pyproject.toml:3` still says 6.1.2.
- **Maintainer remarks on #3763** (https://github.com/typeddjango/django-stubs/pull/3763):
  - ngnpope, 2026-11-13: "Maybe we should have a single breaking release that gets everything sorted?"
  - ngnpope, 2026-11-14: "Arguably we're already making a breaking change as custom fields will need to be updated".
  - UnknownPlatypus, 2026-11-19: "Here we go!", and anyone could start the follow-ups, "especially the fk update."
- **`_ST`/`_GT` swap is unresolved.** ngnpope, 2026-11-14: "It's a shame that the first type var is for the setter and the second for the getter." UnknownPlatypus, same day: "I suppose this is too big of a breaking change to consider ?"
- **ForeignKey follow-up: not opened.** A PR search for "ForeignKey overloads" returns only #3763, the closed #3317 and #1900, and older PRs. The only activity after 11-19 is #3840 (`Model._is_pk_set()`, merged 11-21), #3842 (ty 0.0.105 bump, 11-20), #3841 (open) and issue #3843 "Update AI stance".
- **Master still has a plain FK.** `ForeignKey(ForeignObject[_ST_contra, _GT_co])` has a single non-overloaded `__init__`, with `_ST_contra` defaulting to `Any` (`STUBS/django-stubs/db/models/fields/related.pyi:43-44,159-164`).
- **Inference:** the "single breaking release" remark suggests the release may wait for more breaking work; the next version is probably a major, but that is unconfirmed.

### 2. Migration checklist for a ty user

| Area | django-types | django-stubs | Change needed |
|---|---|---|---|
| Install | Only `types-psycopg2`, Python >=3.10 (0.24.0 METADATA) | Requires `django`, `django-stubs-ext>=6.0.2`, `types-pyyaml`, `typing-extensions`; Python >=3.11 (`STUBS/pyproject.toml:8,31-36`) | Uninstall django-types first (same `django-stubs/` dir). README install for "ty, pyrefly, pyright" is plain `pip install django-stubs` (`STUBS/README.md:18-22`); skip `[compatible-mypy]`. |
| Scalar field annotations | `CharField(Field[_C \| Combinable, _C], Generic[_C])`, one param, `__new__` overloads (`TYPES/.../fields/__init__.pyi:708`) | `CharField(Field[_ST_Char_contra, _GT_Char_co])`, defaults `str \| int` / `str` (`STUBS/.../fields/__init__.pyi:757-760`) | `CharField[str]` becomes bare `CharField` or two params. |
| Nullable field annotations | n/a | Bare annotation means non-null defaults | `x: models.IntegerField = models.IntegerField(null=True)` is rejected (#3763 description). |
| ForeignKey | `ForeignKey(ForeignObject[_M], Generic[_M])`, `__new__` overloads (`TYPES/.../related.pyi:158`) | Two params, second defaults to the first | `ForeignKey[Book]` still parses; nullable is `ForeignKey[Book \| None]`. Unannotated FKs are `Any` from stubs alone. |
| Reverse managers | `django.db.models.manager.RelatedManager` and `ManyToManyRelatedManager[_T, _V, _QS]` (`TYPES/.../manager.pyi:170,194`); README suggests `RelatedManager["User"]()` or `Manager[User]` | `django_stubs_ext.db.models.manager.RelatedManager[Model, QS]` and `ManyRelatedManager[Model, Through]`, declared by hand (`STUBS/README.md:653-680`) | Change imports and names. `ManyRelatedManager` takes no queryset arg. 6.1.1 notes say `Manager[...]` reverse annotations must be narrowed. |
| `Model.objects` | 0.24.0: `objects: ClassVar[BaseManager[Self]]` (`types-whl/.../base.pyi:28`) | Metaclass `__getattr__(cls, name: Literal["objects"]) -> Manager[Self]` (`STUBS/.../base.pyi:51-55`) | Class-level only; instance access is not modelled. |
| Managers | `Manager[_T, _QS]` | `Manager[Model, QuerySet]`; shared managers need a per-model subclass (`STUBS/README.md:330-345`) | Check custom manager declarations. |
| `get_user_model()` | `type[AbstractUser]` (`TYPES/.../auth/__init__.pyi:34`) | `type[AbstractBaseUser]` (`STUBS/.../auth/__init__.pyi:26`, `models.pyi:19-23`) | Code using `.username`/`.email` needs narrowing. `request.user` is `_AnyUser` in both; django-types main already set `_User = AbstractBaseUser` (`TYPES/.../auth/models.pyi:17`). |
| `TextChoices.choices` | `Sequence[tuple[_EnumMemberT, _StrOrPromise]]` (`TYPES/.../enums.pyi:16`) | `list[tuple[str, _StrOrPromise]]`, `values -> list[str]` (`STUBS/.../enums.pyi:67-70`) | Revealed types change. |
| Custom Field subclasses | Inherit `__new__` overloads | Must declare own TypeVar defaults; overloads must be redefined when the subclass changes types (`STUBS/README.md:695-740`) | The pyright/mypy-without-plugin caveat at `README.md:736` does not name ty. |
| Hand-declared `id: int`, `<fk>_id: int` | README tells users to write them (`TYPES/README.md` "id Field", "ForeignKey ids") | Plugin-only upstream | ty synthesizes these, so they become redundant but harmless (inference). |
| Helpers | README already points to `django_stubs_ext.monkeypatch()` | `django_stubs_ext` now always installed; `TypedModelMeta` usable (`STUBS/README.md:105-119`) | `WithAnnotations` and `Manager.from_queryset` are plugin-only: "pyright, pyrefly and ty see `Product.objects` as an unparametrized `Manager` here" (`README.md:454-455`). Queryset-preserving `.values()` chains are also plugin-only (`README.md:401`). |

`ValuesQuerySet` exists only as a `django_stubs_ext` alias (`STUBS/ext/django_stubs_ext/aliases.py:16,28`); I found no such name in django-types.

### 3. Third-party ecosystem (PyPI metadata, 2026-11-21)
- **djangorestframework-stubs 3.18.2** (2026-11-02) requires `django-stubs>=6.1.2`. Installing it beside django-types pulls in django-stubs and collides on `django-stubs/`.
- **djangorestframework-types 0.9.0** (sbdchd) was last released 2024-10-10 and declares no dependencies. It is the django-types-side DRF option today, and it is stale.
- **django-filter-stubs 0.1.3** (2023-03-28) requires `django-stubs>=1.3.0`. Wagtail 8.1 pins `django-stubs==6.1.0` in its `testing` extra.
- django-mysql, django-phonenumber-field, django-ninja, django-model-utils, django-simple-history, strawberry-graphql-django and others declare no stub dependency.
- **After the switch:** DRF and filter stubs become co-installable. Packages subclassing fields or using `_pyi_private_*` need the migration PRs #3763 lists (django-mysql named there); pyrefly#5532 names django-phonenumber-field as affected by field-typing changes.

### 4. django-types' future
- **No statement found** on merging back, deprecation, or ty's switch. The README still frames it as a fork "with the goal of removing the mypy plugin dependency" (`TYPES/README.md:5-12`).
- **Activity is healthy but unreleased.** 41 commits since 0.24.0 (2026-04-22), including "declare Model.objects on ModelBase" (#415, 2026-09-29), "Fix queryset variance and enum choices compatibility with ty" (#412), "Stop modelling managers as QuerySet subclasses" (#425). Main therefore differs noticeably from the 0.24.0 that ty's mdtest pins.
- **It is converging on django-stubs:** #409, #411, #417 are "sync with django-stubs" PRs. #424 ("_User = AbstractBaseUser to match django-stubs") was closed unmerged by its author with no comment, yet main has that alias.
- Issue #361 "ty compatibility" (kalekseev, opened 2025-12-02, open) has no maintainer statement about django-stubs.
- `CHANGELOG.md` is abandoned (last entry 0.5.2, 2021).

### 5. Other plugin-less checkers
- **pyrefly** tells users `pip install django-stubs`; "Does not require a plugin or manual config" (https://pyrefly.org/en/docs/django/). It special-cases auto `id`/`pk`, FK forward type and `X_id`, M2M as `ManyRelatedManager[Author, models.Model]`, choices, `get_X_display`, generic views, factory_boy. Reverse relations are "not yet supported".
- **pyrefly reads `_pyi_private_get_type`/`_pyi_private_set_type`** on the field class (pyrefly#5532, sk-, 2026-11-04, open). UnknownPlatypus, 2026-11-09: "we are moving away from the `_pyi_private_*` in django-stubs, see typeddjango/django-stubs#3763." Master keeps a shim on `AutoField`: "pyrefly types the implicit `id` from these ... TODO: drop once it does" (`STUBS/.../fields/__init__.pyi:1736-1738`).
- **Pylance bundles django-types, not django-stubs.** Rich Chiodo (Microsoft), 2024-06-18: "We actually pull django stubs from here" (sbdchd/django-types), saying typeddjango stubs "are mypy only and don't work with other type checkers." Bundled stubs can be overridden via `python.analysis.stubPath` (https://github.com/microsoft/pylance-release/issues/6029, closed 2026-06-23; updates tracked in #8083).
- **pyright** is "basic support, checked in CI" upstream, with the custom-field caveat (pyright#11989).
- **zuban:** #3763 says "pyrefly and zuban build django support on it [`_pyi_private_*`]" and lists a zuban issue as a follow-up. I found no zuban docs page.
- **ty in django-stubs CI:** `ty check tests/assert_type`, pinned `ty==0.0.105`, with 243 `# ty: ignore` comments (96 `type-assertion-failure`, 60 `invalid-argument-type`, 35 `invalid-assignment`), against 254 pyright and 173 pyrefly ignores.

### 6. ty docs and tests
Page: https://raw.githubusercontent.com/astral-sh/ty/main/docs/features/third-party/django.md
- Line 3 and Setup (lines 70-75): package name and `uv add --dev django-types`.
- Note at line 79: remove or invert (do not install both; uninstall django-types).
- Line 47 `book.title = 3  # error: [invalid-assignment]` and the "Assignments" section (92-96) become false: the CharField set-type default is `str | int`.
- Limitation at lines 102-110: example `"models.ForeignKey[Book]"` still parses; a nullable example would need `Book | None`.
- Line 112 (reverse relations): add the `django_stubs_ext` manual declaration.
- Likely new limitations to list: `WithAnnotations`, `from_queryset`, custom Field subclasses.
- Tests: `/home/user/ruff/crates/ty_python_semantic/resources/mdtest/external/django.md:11` pins `django-types==0.24.0`. `/home/user/ruff/crates/ty_python_semantic/src/types/dedicated/django.rs:396-400` relies on django-types' `ForeignKey[Author | None]` shape via `related_model`.
- Draft astral-sh/ruff#29731 (sharkdp, 2026-10-26, draft) pins mdtests to the #3763 commit and adds a `KnownClass::DjangoForeignKey` constructor special case; sharkdp notes it "could be removed with" upstream FK overloads.
- sharkdp, astral-sh/ty#1018, 2026-11-02: "we plan to support `django-stubs` as the default stub package soon". Nothing about supporting both.
- **Supporting both (inference):** ty would need shape detection, since both ship `django-stubs/`. Candidate signals: field class arity and `__new__` versus `self`-annotated `__init__`; existence of `django.db.models.fields.related_descriptors.ManyRelatedManager`; `ModelBase.__getattr__` versus `objects` attribute. It would also need two mdtest environments and to track django-types main, which is drifting from 0.24.0.

### Confidence & gaps
- **Confidence:** high for stub and README facts; medium for GitHub threads, which were read through a summarising fetch (the GitHub MCP is not authorised for these repos), so quotes may be truncated.
- **Could not load:** full #3763 review threads (including the FK review comment sharkdp links), the #29731 diff, ruff#29642, typeddjango Discussions, any zuban Django docs, pylance-release#8083.
- **Open questions:**
  1. Next django-stubs version and date, and whether it waits for FK overloads or the `_ST`/`_GT` swap.
  2. Whether ty will support django-types during a transition.
  3. Whether ty resolves subclass type params from inherited `__init__` overloads (the README caveat names only pyright and mypy).
  4. Whether ty handles the metaclass `__getattr__(name: Literal["objects"])` pattern without special-casing.
  5. Whether django-types maintainers intend to continue once ty and pyrefly both default to django-stubs, and whether Pylance will re-evaluate its bundle.
  6. What `request.user` resolves to in django-types 0.24.0 (only main's alias was checked).

### Sources
- https://github.com/typeddjango/django-stubs/pull/3763, /releases, /pulls, /issues
- https://github.com/astral-sh/ruff/pull/29731, https://github.com/astral-sh/ty/issues/1018
- https://github.com/pyrefly-org/pyrefly/issues/5532, https://pyrefly.org/en/docs/django/
- https://github.com/microsoft/pylance-release/issues/6029
- https://github.com/sbdchd/django-types/issues/361, /pull/424
- https://pypi.org/pypi/<package>/json for the packages in section 3
- Local clones, wheels and `/home/user/ruff` (HEAD 25bb62e) as cited