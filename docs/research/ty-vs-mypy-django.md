# Gaps between mypy and ty for Django

Research date: 2026-11-20. Local working artifact; not meant to be committed.

## Summary

mypy with the django-stubs plugin boots the real Django project at check time and reads the app
registry, so it knows everything Django generates at runtime. ty has no plugin system. Its Django
support is one 460-line Rust module that synthesizes a few model members on top of the
`django-types` stubs. ty matches mypy on plain model field types, primary keys, forward foreign
keys given as class references, and generated display/date methods. It is behind on everything
that needs project-wide knowledge: reverse relations, string model references, custom managers and
querysets, `values()`/`values_list()`/`annotate()` shapes, ORM keyword validation, settings, and
the custom user model.

Three points matter most for anyone moving a mypy-checked Django codebase to ty today:

1. **Many gaps are silent.** Where mypy reports an error or a precise type, ty often yields
   `Unknown`/`Any` with no diagnostic, so type coverage drops without anything flagging it.
2. **Unannotated custom managers lose their methods silently.** `objects = BookManager()` is
   revealed as `BaseManager[Book]`, and `Book.objects.published()` is `Unknown` with no error.
3. **Hand annotations recover a good share.** `ClassVar` manager annotations, generic
   `ForeignKey[...]` annotations, and hand-declared reverse accessors all work under ty.

## Method

| Thread | How | Evidence |
|---|---|---|
| ty implementation | Read ruff at the pinned submodule commit `0528644c0` (ty 0.0.107) | `crates/ty_python_semantic/src/types/dedicated/django.rs`, `resources/mdtest/external/django.md` |
| mypy side | Read django-stubs `5a00610` (6.1.2) plugin and stubs, and django-types `25e39e1` | `mypy_django_plugin/main.py`, `transformers/*.py`, `django/context.py` |
| Roadmap | Public issues and PRs in astral-sh/ty and astral-sh/ruff | URLs in the roadmap section |
| Head-to-head | Ran both checkers on one sample project, 100 labelled cases | See "Reproducing" |

Head-to-head versions: Django 6.1.3, Python 3.13; mypy 2.4.1 + django-stubs 6.1.2 (plugin on);
ty 0.0.107 + django-types 0.24.0.

## How each side works

| | mypy + django-stubs plugin | ty |
|---|---|---|
| Mechanism | Plugin hooks; runs `django.setup()` and reads `_meta` (`mypy_django_plugin/django/context.py:49-69`) | Built-in special-casing; purely static |
| Needs importable project and settings | Yes; "if your `manage.py runserver` crashes, mypy will crash too" (django-stubs `README.md:191-193`) | No |
| Stubs | `django-stubs` | `django-types` only; `django-stubs` "planned" (`docs/features/third-party/django.md:79`) |
| Model detection | App registry | `Model` in the MRO, matched by class name and module (`django.rs:20-26`) |
| Field metadata | Runtime field objects | Literal keyword arguments only: `name`, `primary_key`, `choices`, `null`, `to_field` (`django.rs:71-102`) |
| Scope of Django-specific code | 16 transformer modules | `id`, `pk`, `<fk>_id`, `get_<f>_display`, `get_next/previous_by_<f>`, `Meta` override suppression |

Everything else ty knows about Django (field value types, `null=True`, forward FK types, managers,
querysets) comes from django-types through ordinary descriptor and overload resolution.

## Head-to-head results

Idiomatic, unannotated Django code. "Parity" means the same useful type or the same error.

### At parity

| Case | Both report |
|---|---|
| Plain, nullable, Decimal, datetime, inherited-from-abstract fields | `str`, `date \| None`, `Decimal`, `datetime` |
| Automatic `id`, `pk`, custom primary key, multi-table child `pk` | `int` / `str` |
| Forward FK by class reference, and its `_id` (follows related pk) | `Book`, `str`, `int` |
| `get_<field>_display()` | `str` |
| Unknown attribute on a model instance | error |
| Default manager basics: `get`, `first`, iteration, `count`, `get_or_create`, `in_bulk` | `Review`, `Review \| None`, `tuple[Book, bool]`, ... |
| Async ORM: `aget`, `async for` | `Review` |
| `aggregate()` | `dict[str, Any]` (mypy has no hook either) |
| `ModelForm.instance`, `ModelForm.save()` | `Any` on both |
| `TextChoices` `.label`, `.value`, `.labels` | `str`, `list[str]` |

### Gaps where ty is behind

| Area | Example | mypy + plugin | ty 0.0.107 | Silent in ty? |
|---|---|---|---|---|
| String model reference | `ForeignKey("shop.Author", null=True)` | `Author \| None` | `Unknown \| None` | Yes |
| `"self"` reference | `ForeignKey("self", null=True)` | `Book \| None` | `Unknown \| None` | Yes |
| `_id` of a string-referenced FK | `book.editor_id` | `int \| None` | `Unknown \| None` | Yes |
| `settings.AUTH_USER_MODEL` target | `author.user` | `User \| None` | `Any \| None` | Yes |
| Reverse FK, `related_name` | `author.books` | `Book_RelatedManager` | `missing-attribute` | No (false positive) |
| Default reverse accessor | `book.review_set` | `RelatedManager[Review]` | `missing-attribute` | No (false positive) |
| Reverse M2M, reverse O2O, multi-table child accessor | `tag.books`, `user.author_profile`, `book.ebook` | typed | `missing-attribute` | No (false positive) |
| M2M `through` | `Book.tags.through` | `type[Book_tags]` | `Unknown` | Yes |
| M2M manager | `book.tags` | through model known | `ManyToManyRelatedManager[Tag, Unknown]` | Yes |
| Custom manager | `objects = BookManager()` | `BookManager` | `BaseManager[Book]` | Yes |
| Custom manager method | `Book.objects.published()` | `QuerySet[Book, Book]` | `Unknown` | Yes |
| `QuerySet.as_manager()` | `Author.objects.active()` | `AuthorQuerySet[...]` | `Unknown` | Yes |
| Custom queryset chaining | `.filter(...).active()` | `AuthorQuerySet[...]` | `Unknown` | Yes |
| Inherited custom manager | `Ebook.objects` | `BookManager` | `BaseManager[Ebook]` | Yes |
| `values()` | `values("title", "price")` | `TypedDict({'title': str, 'price': Decimal})` | `dict[str, Any]` | Yes |
| `values_list()` incl. `flat`, `named`, `author__name` | | `tuple[str, Decimal]`, `str`, named tuple | `Any` | Yes |
| `annotate()` | `.annotate(n=Count("review")).get().n` | `int` | `missing-attribute` | No (false positive) |
| Unknown field in `filter`, `values_list`, `order_by` | `filter(titel="x")` | error with field choices | no error | Yes |
| Unknown relation in `select_related` | | error | no error | Yes |
| Unknown constructor / `create` keyword | `Review(bok=book)` | error | no error | Yes |
| `_meta.get_field` | `get_field("title")` / `get_field("nope")` | `CharField[...]` / error | `Field[Any, Any]` / no error | Yes |
| Settings | `settings.DEBUG`, project settings | `bool`, `int`, `dict[str, bool]` | `Any` | Yes |
| Unknown setting | `settings.NOT_A_SETTING` | error | no error | Yes |
| Custom user model | `get_user_model()`, `request.user` | `User`, `User \| AnonymousUser` | `AbstractUser`, `AbstractUser \| AnonymousUser` | Yes (custom fields then error) |
| Per-model exceptions | `Book.DoesNotExist` | `Book.DoesNotExist` | `ObjectDoesNotExist` | Yes (minor) |
| Lazy strings | `reverse_lazy("home")` | `_StrPromise` | `Any` | Yes |

ty also reveals `BaseManager[Review]` where mypy reveals `QuerySet[Review, Review]` for
`.all()`/`.filter()`. That is a django-types modelling choice (`BaseManager` subclasses
`QuerySet`, methods return `Self`), and is harmless in practice.

Capabilities the plugin has that the sample did not exercise, and that ty has no code for:
`Prefetch(to_attr=...)` typing, `defer`/`only`/`distinct`/`update`/`bulk_update` field-name
checks, `save(update_fields=[...])`, `apps.get_model("app.Model")`, `GenericRelation` targets,
`TypedModelMeta` checking of `Meta` attributes, `WithAnnotations[...]`, and `DEFAULT_AUTO_FIELD`
(ty always types the automatic `id` as `int` via `AutoField`, `django.rs:303`).

### Where ty is stricter or mypy is weaker

| Case | mypy + plugin | ty |
|---|---|---|
| `book.title = 3` | accepted (django-stubs set type includes `int`) | `invalid-assignment` |
| `instance.pk = None` (Django's copy idiom) | accepted | rejected; open bug [astral-sh/ty#4932](https://github.com/astral-sh/ty/issues/4932) |
| `ebook.book_ptr` (multi-table parent link) | false `attr-defined` error | `missing-attribute` (both wrong) |
| `Status.choices` | `list[tuple[str, str]]` | `Sequence[tuple[Status, str]]` (differs, both usable) |
| No Django boot, no settings module, no import of project dependencies | required | not needed |

mypy's plugin did not catch several things one might expect: `filter(title__bogus=...)`,
`filter(author__nmae=...)`, `filter(rating="abc")`, `Review(rating="five")`, and
`create(rating="x")` were all accepted in this run. Its keyword validation is real but shallower
than its reputation.

### Baselines

| Configuration | Result |
|---|---|
| mypy + django-stubs, plugin off | Fields `Any`, `Need type annotation` on every field, no `id`/`_id`/reverse accessors. The stubs are not usable alone with mypy. |
| ty + django-stubs 6.1.2 (unsupported) | Model fields and forward FKs are `Unknown`; `_id` is `Any`. Custom managers do resolve (`BookManager`), unlike with django-types. |

The second row confirms the docs: use django-types only. It also shows the custom-manager
problem is specific to how django-types declares `objects`.

### Workarounds that work in ty today

Verified with ty 0.0.107 + django-types 0.24.0:

```python
class Author(models.Model):
    objects: ClassVar[AuthorManager] = AuthorManager()   # -> AuthorManager, methods typed
    books: RelatedManager[Book]                           # reverse accessor, declared by hand

class Book(models.Model):
    editor: models.ForeignKey[Author | None] = models.ForeignKey(
        "shop.Author", on_delete=models.SET_NULL, null=True
    )                                                     # -> Author | None, editor_id -> int | None
```

| Workaround | Outcome |
|---|---|
| `objects: ClassVar[Mgr] = Mgr()` | Manager and its custom methods are typed. Without `ClassVar`, ty reports `incompatible-attribute-override`. |
| Manager whose `get_queryset()` returns a custom queryset, with explicit forwarding methods | Custom queryset methods chain correctly. |
| `ForeignKey[Model \| None]` annotation on string and `"self"` references | Attribute and `_id` both typed. |
| Annotation-only `RelatedManager[Model]` for reverse accessors | Typed; `.first()` gives `Model \| None`. |

No workaround exists for `values()`/`values_list()` shapes, ORM keyword validation, typed
settings, or the custom user model (other than casts or a typed request subclass).

## Roadmap and maintainer position

| Topic | Status | Source |
|---|---|---|
| Plugin system | Not planned. carljm: "We currently have no plans to build a plugin system for `ty`." | [astral-sh/ty#291](https://github.com/astral-sh/ty/issues/291) (closed not planned) |
| Tracking issue | Open, no milestone (removed from "ty-1.1" on 2026-11-18) | [astral-sh/ty#1018](https://github.com/astral-sh/ty/issues/1018) |
| Stated next steps | Switch to django-stubs, reverse FK/O2O accessors, string lazy relations, precise model constructor signatures | sharkdp, 2026-11-02, in #1018 |
| django-stubs switch | Draft, unreviewed; includes FK inference from the target model | [astral-sh/ruff#29731](https://github.com/astral-sh/ruff/pull/29731) |
| Upstream unblocker | Merged 2026-11-19; moves nullability into `__init__` overloads | [typeddjango/django-stubs#3763](https://github.com/typeddjango/django-stubs/pull/3763) |
| `pk = None` fix | Draft | [astral-sh/ruff#30068](https://github.com/astral-sh/ruff/pull/30068) |
| Managers, querysets, lookups, settings, user model, DRF | No issue, PR, or maintainer statement found | search of astral-sh/ty |
| Feature parity list vs the mypy plugin | Requested by a user in #1018; does not exist | #1018 |

All Django work landed between 2026-10-22 and 2026-11-03 (ty 0.0.92 to 0.0.97). Nothing
Django-related has landed on ruff main since the pin.

For context, pyrefly ships built-in Django support on django-stubs and also lacks reverse
relations ([pyrefly docs](https://pyrefly.org/en/docs/django/)). mypy with the plugin is still
the only checker that introspects Django at runtime.

## Gap classification

| Class | Gaps | Outlook |
|---|---|---|
| On the stated roadmap | django-stubs support, reverse accessors, string/`"self"` references, constructor signatures | Planned, no dates |
| Fixable statically, not on the roadmap | Custom managers and `as_manager()`/`from_queryset()`, `values`/`values_list`/`annotate` shapes, lookup-keyword validation, per-model `DoesNotExist`, M2M `through`, `_meta.get_field` | Needs new special-casing; nobody has asked for it in the tracker yet |
| Needs project-wide configuration | `settings.X` types, `AUTH_USER_MODEL`, `get_user_model()`, `request.user`, `"app.Model"` resolution across apps, `DEFAULT_AUTO_FIELD` | Hard without a settings-module option or a plugin; no stated plan |
| Out of scope on both sides | `ModelForm` field inference, `aggregate()` result shapes | mypy does not do these either |

## Open questions and unverified items

- sharkdp's roadmap comment in #1018 was read through a summarizing fetch; the items are
  paraphrased. Check the wording at the source before quoting it.
- The django-types HEAD (`25e39e1`) was reported to declare `objects` through a metaclass
  descriptor and `BaseManager[_T, _QS]`. The installed 0.24.0 wheel declares
  `objects: ClassVar[BaseManager[Self]]`. The custom-manager result above is for the released
  wheel; HEAD may behave differently. Re-run against a build from HEAD to settle it.
- Why `Book.objects.published` is `Unknown` with no `missing-attribute` error under django-types
  was not traced.
- Django REST framework and other Django-adjacent plugins (`djangorestframework-stubs`) were not
  examined.
- The sample is 100 cases on one small project. Running ty over the django-stubs
  `tests/typecheck` suite would give a much fuller parity list (the request in #1018).
- No 2026 write-up of a real mypy-to-ty Django migration was found.

## Reproducing

The sample project, outputs, and the join script are in the session scratchpad (ephemeral):
`/tmp/claude-0/-home-user-ty/e18cb915-8a5d-5dfd-b03f-996830a4902a/scratchpad/h2h`.

```bash
cd proj && ../venv-mypy/bin/mypy --config-file mypy.ini shop/cases.py shop/models.py
```

```bash
cd proj && ../venv-ty/bin/ty check --python ../venv-ty --output-format concise shop
```

## Sources

- ty docs: `docs/features/third-party/django.md`; `CHANGELOG.md:368,504,534,572-575`
- ruff `0528644c0`: `crates/ty_python_semantic/src/types/dedicated/django.rs`,
  `crates/ty_python_semantic/resources/mdtest/external/django.md`,
  `crates/ty_python_semantic/src/types/overrides/attributes.rs:466-474`
- django-stubs `5a00610`: `mypy_django_plugin/main.py`, `transformers/{models,fields,managers,querysets,orm_lookups,init_create,settings,auth,meta,choices,manytomany}.py`, `django/context.py`, `README.md`
- django-types `25e39e1`: `README.md`, `django-stubs/db/models/{base,manager,query}.pyi`
- Issues and PRs linked inline
