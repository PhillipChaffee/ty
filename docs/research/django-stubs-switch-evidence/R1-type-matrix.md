## R1 - What ty actually infers for the same Django code under django-types, django-stubs 6.1.2, and django-stubs master

### Answer
All 6 planned runs completed; nothing was skipped.

- **django-stubs master (C)** matches django-types (A) for scalar fields, including `null=True`, and is better for managers and querysets. It loses every relation type: ForeignKey / OneToOneField attributes and `<fk>_id` become silent `Any`.
- **Released django-stubs 6.1.2 (B)** is far worse: every field attribute, plus `id` and `pk`, is `Unknown`.
- **ty's hard-coded behaviours** (`id`, `pk`, `<field>_id`, `get_*_display`, `get_next_by_*`) still fire under B and C, but their types come from the stubs. One breaks outright: `<fk>_id` for a ForeignKey with `to_field` is `missing-attribute` under B and C.

### 1. Versions
| Env | Packages (Python 3.13.18, Django 6.1.3 in all) |
|---|---|
| A | django-types 0.24.0 (pulls types-psycopg2) |
| B | django-stubs 6.1.2, django-stubs-ext 6.1.2, no mypy plugin |
| C | django-stubs master 44457d47 (2026-11-21, "Add `Model._is_pk_set()` (#3840)") plus its `ext/`; still self-reports as 6.1.2 |

ty main build: `/home/user/ruff/target/debug/ty` ("ty unknown (c068ccdd0 2026-11-21)"). Released: ty 0.0.107. uv 0.13.9.

### 2. Matrix (main build)
Full 120-probe matrix plus 38 follow-up probes: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/out/matrix.md`. Selected rows:

| Probe | A | B | C |
|---|---|---|---|
| `book.title` / `pages` / `published` / `updated` / `price` / `in_print` | `str` / `int` / `date` / `datetime` / `Decimal` / `bool` | `Unknown` (all) | same as A |
| the same with `null=True` | `X \| None` | `Unknown` | `X \| None` |
| `book.title = 3` | invalid-assignment | no diagnostic | no diagnostic |
| `book.published = "2020-01-01"` | invalid-assignment | no diagnostic | no diagnostic |
| `book.title = None` (non-null) | invalid-assignment | no diagnostic | invalid-assignment |
| `book.title = b"x"`, `book.published = 3` | invalid-assignment | no diagnostic | invalid-assignment |
| `book.pages = "abc"` / `= 1.5` | invalid-assignment | no diagnostic | no diagnostic |
| `book.id`, `book.pk` | `int` | `Unknown` | `int` |
| `country.pk` (CharField pk) | `str` | `Unknown` | `str` |
| `country.id` (custom pk) | missing-attribute | missing-attribute | missing-attribute |
| `book.author` (FK by class) | `Author` | `Unknown` | `Any` |
| `book.author_id` | `int` | `Any` | `Any` |
| `book.editor` / `editor_id` (null FK) | `Author \| None` / `int \| None` | `Unknown` / `Any \| None` | `Any` / `Any \| None` |
| `book.author_by_slug` (`to_field`) | `Author` | `Unknown` | `Any` |
| `book.author_by_slug_id` | `str` | missing-attribute | missing-attribute |
| FK `"Author"` / `"y.Author"` | `Unknown` | `Unknown` | `Any` |
| FK `"self"`, null | `Unknown \| None` | `Unknown` | `Any` |
| `book.country_id` (FK to str pk) | `str` | `Any` | `Any` |
| `profile.author` (O2O) / null O2O | `Author` / `Author \| None` | `Unknown` | `Any` |
| `passport.pk` (O2O as pk) | `int` | `Any` | `Any` |
| `book.tags` | `ManyToManyRelatedManager[Tag, Unknown]` | `ManyRelatedManager[Tag, Any]` | same as B |
| `book.tags.all()` | `ManyToManyRelatedManager[Tag, Unknown]` | `QuerySet[Tag, Tag]` | same as B |
| `book.tags.through` | `Unknown` | `Any` | `Any` |
| `get_genre_display()` / `get_next_by_published()` | `str` / `Book` | same | same |
| `ts.id` on abstract model | missing-attribute | same | same |
| `author.id` (child of abstract) | `int` | `Unknown` | `int` |
| `Author.Meta.ordering` (Meta subclassing parent Meta) | `list[str]`, no error | same | same |
| `ebook.book_ptr` / `book_ptr_id` / `pk` | `Book` / `int` / `int` | `Book` / `Unknown` / `Unknown` | `Book` / `int` / `int` |
| `Author.objects` | `BaseManager[Author]` | `Manager[Author]` | `Manager[Author, QuerySet[Author, Author]]` |
| `.all()` / `.filter()` / `.annotate()` / `.none()` | `BaseManager[Author]` | `QuerySet[Author, Author]` | same as B |
| `.first()` / `.get()` / `.count()` | `Author \| None` / `Author` / `int` | same | same |
| `.values("name")` | `ValuesQuerySet[Author, dict[str, Any]]` | `QuerySet[Author, dict[str, Any]]` | same as B |
| `.values_list("name", flat=True)` | `ValuesQuerySet[Author, Any]` | `QuerySet[Author, Any]` | same as B |
| `.filter(nme="x")` (misspelt lookup) | no diagnostic | same | same |
| `author.objects` (instance) | `BaseManager[Author]`, no error | missing-attribute | missing-attribute |
| `Book.objects` (`objects = BookManager()`) | `BaseManager[Book]` | `BookManager` | `BookManager` |
| `Book.objects.bestsellers()` (unannotated) | `Unknown` | `Unknown` | `Unknown` |
| `Book.objects.n_bestsellers()` (`-> int`) | `Unknown` | `int` | `int` |
| `Book.cheap_ones` (`as_manager()`) | `Manager[Book]` | `Manager[Book]` | `Manager[Book, BookQuerySet]` |
| `Book.cheap_ones.cheap()` | `Unknown`, no error | missing-attribute | missing-attribute |
| `Book.cheap_ones.all()` | `Manager[Book]` | `QuerySet[Book, Book]` | `BookQuerySet` |
| `Book.DoesNotExist` / `Book._meta` | `type[ObjectDoesNotExist]` / `Options[Book]` | same | same |
| `Book.title` (class level) | `CharField[str]` | `_FieldDescriptor[CharField[Unknown, Unknown]]` | `_FieldDescriptor[CharField[str \| int, str]]` |
| `Genre.choices` | `Sequence[tuple[Genre, str]]` | `list[tuple[str, str \| _StrPromise]]` | same as B |
| `Genre.FICTION.label` | `str` | `str \| _StrPromise` | same as B |
| `Genre.values` | `Sequence[Genre]` | `list[str]` | `list[str]` |
| `get_user_model()` | `type[AbstractUser]` | `type[AbstractBaseUser]` | same as B |
| `user.username` | `str` | missing-attribute | missing-attribute |
| `HttpRequest().user` | `AbstractUser \| AnonymousUser` | `AbstractBaseUser \| AnonymousUser` | same as B |
| `settings.DEBUG` (and `settings.NOT_A_SETTING`) | `Any` | `Any` | `Any` |
| `Book(titel="x")`, `Book(title=3)` | no diagnostic | same | same |
| `title: models.CharField[str] = ...` | fine, `str` | invalid-type-arguments, `Unknown` | fine, `str` |
| `author.book_set`, `author.edited`, reverse O2O, `book.ebook` | missing-attribute | same | same |
| hand-declared `novels: RelatedManager[Novel]` | `RelatedManager[Novel]`; `.all()` gives `RelatedManager[Novel]` | `RelatedManager[Novel]`; `.all()` gives `QuerySet[Novel, Novel]` | `RelatedManager[Novel, QuerySet[Novel, Novel]]` |

**RelatedManager import paths.** A: `django.db.models.manager.RelatedManager` (stub-only, so it needs `TYPE_CHECKING`). B and C: `django.db.models.fields.related_descriptors.RelatedManager` (stub-only) or `django_stubs_ext.db.models.manager.RelatedManager` (importable at runtime). Neither side's path resolves under the other, so user code has to change.

**Released 0.0.107 versus main.** The only difference in any file or environment is `ebook.book_ptr` and `ebook.book_ptr_id`: 0.0.107 reports `missing-attribute` and `Unknown` in A, B and C. Everything else is identical.

### 3. Meaningful differences A to C
**Better under C**
- Queryset methods return `QuerySet[...]` instead of `BaseManager[...]`.
- An unannotated `objects = BookManager()` keeps its type, so annotated custom methods resolve. Under A the inherited `objects: ClassVar[BaseManager[Self]]` wins and custom methods are `Unknown`.
- `as_manager()` carries the queryset type, so `.all()` gives `BookQuerySet`.
- `author.objects` on an instance is correctly an error.
- ISO strings are accepted for DateField (set type is `str | date | Combinable`).
- M2M `.all()` gives `QuerySet[Tag, Tag]`.

**Worse under C, silently `Any`**
- Every ForeignKey / OneToOneField attribute, however the target is written (A handles the class form).
- Nullability on relations: `book.editor` is `Any`, not `Author | None`.
- All `<fk>_id` types, and `pk` when the pk is a OneToOneField.
- Anything reached through a relation, such as `book.author.name`.
- `Book.objects` is `BookManager` on `EBook` too, so `EBook.objects.first()` is `Book | None` (A: `EBook | None`). This follows from my `Manager["Book"]` declaration.

**New errors under C**
- `<fk>_id` with `to_field`: missing-attribute (false positive).
- `user.username` on `get_user_model()()`: missing-attribute, because the stubs fall back to `AbstractBaseUser` without the plugin.
- `Book.cheap_ones.cheap()`: missing-attribute (silent `Unknown` under A).
- `models.ForeignKey[Author]` annotations still work, but django-types' other one-parameter generics would need checking.

**Looser under C**
- `book.title = 3` and `book.pages = "abc"` are accepted, because the set types are `str | int` and `float | int | str`.

**Workaround in B and C.** Annotating `fk: models.ForeignKey[Author, Author] = ...` or `ForeignKey[Author | None, Author | None]` gives `Author` / `Author | None` and checks assignments, but `<fk>_id` stays `Any`. The same two-parameter annotation is `invalid-type-arguments` under A. The one-parameter `ForeignKey[Author]` works in all three.

**Released 6.1.2 (B), what users have today**
- All scalar field attributes, `id`, `pk` and `book_ptr_id` are `Unknown`; no assignment is checked at all.
- `models.CharField[str]` is an error ("No type argument provided for required type variable `_GT`").
- Managers, querysets, choices and the user model behave as in C.
- FK attributes are `Unknown` rather than `Any`.

### 4. Surprises
- **Metaclass `__getattr__` for `objects`.** `Model.objects` does resolve through `ModelBase.__getattr__(cls, name: Literal["objects"])` in B and C. But `Author.nonexistent` then reports `invalid-attribute-access` ("Expected `Literal["objects"]`, found `Literal["nonexistent"]`") and still reveals `Manager[Author]`. That is a confusing message and a wrong recovered type.
- **`null=True` overloads.** ty does pick the `self`-annotated `__init__` overload under C: `CharField(max_length=3, null=True)` is `CharField[str | int | None, str | None]`. Explicit `null=False` and `null=True, blank=True` are also right. JSONField is `Any` in B and C.
- **Hard-coded `<field>_id`.** It works in B and C but appears to derive its type from the related pk's stub type, giving `Any` or `Any | None` (nullability is preserved).
- **String-named FK targets** are `Unknown` even under A, including `"self"` and `"app.Model"`. So ty today only resolves class-object targets.
- **No constructor checking** in any environment, and no reverse accessors in any environment.
- **`settings.DEBUG` is `Any`** in all three.
- **Runtime curiosity.** `Author.Meta.ordering` at runtime is the parent's `['created']`, because Django pops `Meta` off the class; ty reports `list[str]` with no error either way.

### 5. Files
All under `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/`:
- Main test module: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/probe.py`. It imports under real Django; I also created tables in in-memory SQLite and exercised the instances.
- Follow-up probes: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/extra.py`. This one was not run at runtime.
- RelatedManager variants: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/rm_a.py`, `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/rm_b.py`, `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/rm_c.py`.
- Raw outputs: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/out/`, named `{probe,extra,rm_a,rm_b,rm_c}_{A,B,C}_{main,rel}.txt`.
- Matrices: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/out/matrix.md`, and `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/out/matrix_full.md` with full error messages. Generator: `/tmp/claude-0/-home-user/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/r1/matrix.py`.
- Venvs: `venvA`, `venvB`, `venvC`, and `venvty` (ty 0.0.107) in the same directory.

Rerun with `<ty> check --python <dir>/venvX --output-format concise <file>` from that directory.

### Confidence and gaps
- **Confidence:** high for the revealed types; they are direct tool output from default ty settings with no configuration file.
- **Not done:** I did not read ty's source to confirm why `<fk>_id` is `Any` or why the `to_field` case is missing; those are inferences from the output. No mypy or pyright comparison was run. C was installed from the local clone, not from GitHub.