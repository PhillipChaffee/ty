# Django gaps we could address

A working backlog of ty's Django gaps relative to mypy with the django-stubs plugin, ordered by
how ready each one is for us to pick up. Dated 2026-11-20.

- Evidence for each gap: `ty-vs-mypy-django.md`.
- What maintainers accept: `ty-django-pr-expectations.md`.
- Rules we follow: `django-contribution-guidelines.md`.

Observed results are from ty 0.0.107 with django-types 0.24.0, and mypy 2.4.1 with django-stubs
6.1.2 and its plugin, on Django 6.1.3. Code locations are in astral-sh/ruff at `0528644c0`:
`django.rs` is `crates/ty_python_semantic/src/types/dedicated/django.rs`, and `django.md` is
`crates/ty_python_semantic/resources/mdtest/external/django.md`.

The reproductions below are facts to work from. Issue text and pull request descriptions must be
written by a person (see the guidelines, section 2).

## Overview

| # | Gap | Tier | Effort | Blocked by |
|---|---|---|---|---|
| 1 | Multi-table `<parent>_ptr` and `<parent>_ptr_id` | A: ready after a go-ahead | Small | Maintainer go-ahead |
| 2 | M2M `through` when a class is passed | A | Small | django-stubs switch |
| 3 | `name=` field renames | A | Small to medium | Maintainer go-ahead |
| 4 | Per-model `DoesNotExist` | A | Small | Low value; ask if wanted |
| 5 | Docs page is behind the implementation | A (this repository) | Small | Nothing |
| 6 | Stub-level fixes in django-stubs | A (upstream) | Small each | Nothing |
| 7 | Unannotated custom managers lose their methods | B: report first | Unknown | Diagnosis |
| 8 | String references in the same module, and `"self"` | B: coordinate | Medium | Draft #29731 |
| 9 | `Model(...)` and `create()` keyword checks | B: coordinate | Medium to large | Maintainer plan |
| 10 | Reverse relations in the same file | C: design first | Medium | Design agreement |
| 11 | Reverse relations across files | C | Large | Project-wide index design |
| 12 | `"app.Model"` references | C | Large | App registry design |
| 13 | `values()` / `values_list()` shapes | C | Medium to large | No stated position |
| 14 | `annotate()` attributes | C | Large | No stated position |
| 15 | `filter()` / `order_by()` / `select_related()` name checks | C | Large | No stated position |
| 16 | `_meta.get_field` | C | Small | Low value |
| 17 | Settings types, `AUTH_USER_MODEL`, `get_user_model()`, `DEFAULT_AUTO_FIELD` | D: do not build | Large | Needs settings knowledge |
| - | `instance.pk = None` | Not ours | - | Maintainer draft #30068 |
| - | `request.user` narrowing | Not ours | - | General narrowing issue (ty#1479) |

Tier A fits the existing code pattern. Tier B overlaps the maintainer's plans or needs diagnosis.
Tier C needs new architecture and a design discussion. Tier D has no route without a decision
that maintainers have so far leaned against.

## Tier A: ready once a maintainer agrees

### 1. Multi-table `<parent>_ptr` and `<parent>_ptr_id`

```python
class Book(models.Model):
    isbn = models.CharField(max_length=13, primary_key=True)

class Ebook(Book):
    size_kb = models.IntegerField()

def f(ebook: Ebook) -> None:
    reveal_type(ebook.book_ptr)     # Django: Book
    reveal_type(ebook.book_ptr_id)  # Django: str
```

- **ty today:** `missing-attribute` on `book_ptr`.
- **mypy + plugin:** also a false `attr-defined` error on `book_ptr`. Fixing this would put ty
  ahead of mypy here.
- **Approach:** add a `_ptr` / `_ptr_id` suffix to the name pre-filter (`django.rs:227-234`),
  then walk the MRO as `primary_key_member` does (`django.rs:282-296`) to find a concrete,
  non-abstract parent model whose lowercased name matches. Type is the parent instance;
  `_ptr_id` is the parent's primary-key type.
- **Tests to write:** concrete parent, abstract parent (no `_ptr`), two levels of inheritance,
  parent with a custom primary key, a user-declared `parent_link` field, and a negative case.
- **Risks:** proxy models are not modelled at all today; an explicit
  `OneToOneField(parent_link=True)` changes the attribute name.
- **Why first:** in-pattern, unclaimed, removes a false positive, small.

### 2. M2M `through` when a class is passed

```python
class Book(models.Model):
    tags = models.ManyToManyField(Tag, through=BookTag)

reveal_type(Book.tags.through)  # Django: type[BookTag]
```

- **ty today:** `Unknown` (silent). The manager's second parameter is also `Unknown`:
  `ManyToManyRelatedManager[Tag, Unknown]`.
- **mypy + plugin:** the through model, including the auto-generated one (`Book_tags`).
- **Approach:** read the `through` keyword in field metadata (`django.rs:95-102`) when it is a
  class object. The auto-generated through model would need a synthesized class and is out of
  scope for a first change.
- **Blocked by:** the django-stubs switch (draft #29731) rewrites the foreign-key plumbing this
  sits on. Wait, then check what the new stubs already give.

### 3. `name=` field renames

```python
class Counter(models.Model):
    views = models.IntegerField(name="view_count")

c.view_count  # Django: int
c.views       # Django: AttributeError
```

- **ty today:** the renamed attribute is `missing-attribute`, and the original name is still
  accepted. TODOs already record this at `django.md:122-135`.
- **Approach:** the renamed name is already tracked (`django.rs:71-77`). Serving `view_count`
  needs the lookup restructured, because the pre-filter cannot match arbitrary names. Hiding
  `views` is harder: the hook only runs for names missing from the class body.
- **Suggestion:** propose doing only the first half (resolve the renamed attribute) and leave the
  second as a TODO.
- **Risk:** the feature is rare in real code, so motivation may be questioned.

### 4. Per-model `DoesNotExist`

```python
reveal_type(Book.DoesNotExist)  # mypy: Book.DoesNotExist; ty: type[ObjectDoesNotExist]
```

- **ty today:** the generic `ObjectDoesNotExist`. `except Book.DoesNotExist` works; only the
  distinction between models is lost.
- **Approach:** would need a synthesized class per model (`class/dynamic_literal.rs:55`).
- **Value:** low. Ask whether it is wanted before spending time.

### 5. Docs page is behind the implementation (this repository)

`docs/features/third-party/django.md` does not mention three things that have shipped:

- Abstract models get no automatic `id` (ruff #29744).
- `Meta` overrides no longer report `invalid-override` (ruff #29769).
- A foreign key or one-to-one field used as the primary key gives `pk` the related key's type
  (ruff #29785).

It could also document the workarounds we verified for today's limitations:

- `objects: ClassVar[BookManager] = BookManager()` types a custom manager and its methods.
  Without `ClassVar`, ty reports `incompatible-attribute-override`.
- An annotation-only `books: RelatedManager[Book]` types a reverse accessor.

The maintainer has said he wants this page to lead with features and keep limitations short, so
keep any addition brief. This is a docs pull request to `astral-sh/ty` and can go ahead without
waiting on the stubs switch, though the workaround text will need revisiting after it.

### 6. Stub-level fixes in django-stubs (upstream)

Both projects prefer fixes in the stubs. Candidates:

- Follow-ups listed in typeddjango/django-stubs#3763: foreign-key overloads, `FilePathField`,
  fields still typed `Any`.
- Field input types, such as ISO date strings assigned to date fields (the TODO at
  `django.md:54-55`).
- Check whether anything in gap 7 can be expressed in stubs.

## Tier B: report or coordinate first

### 7. Unannotated custom managers lose their methods

```python
class BookManager(models.Manager["Book"]):
    def published(self) -> models.QuerySet["Book"]: ...

class Book(models.Model):
    objects = BookManager()

reveal_type(Book.objects)              # mypy: BookManager; ty: BaseManager[Book]
reveal_type(Book.objects.published())  # mypy: QuerySet[Book, Book]; ty: Unknown, no error
```

- **Why it matters most:** this is the most common pattern in real Django code, and it fails
  silently. `QuerySet.as_manager()` and chained custom queryset methods behave the same way.
- **What we know:** with django-stubs 6.1.2 in place of django-types, ty reveals `BookManager`
  correctly. So the cause is how django-types 0.24.0 declares
  `objects: ClassVar[BaseManager[Self]]` on `Model`, combined with ty preferring the inherited
  declaration over the subclass's unannotated assignment.
- **What we do not know:** why `.published` is `Unknown` with no `missing-attribute` error, and
  whether the django-types repository head already declares `objects` differently.
- **Action:** diagnose, then file an issue. This may resolve itself with the django-stubs switch,
  in which case the useful contribution is a test that locks it in. `as_manager()` and
  `from_queryset()` exposing queryset methods on the manager is a separate, larger item.

### 8. String references in the same module, and `"self"`

```python
class Book(models.Model):
    editor = models.ForeignKey("Author", null=True, on_delete=models.SET_NULL)
    sequel = models.ForeignKey("self", null=True, on_delete=models.SET_NULL)

reveal_type(book.editor)     # Django: Author | None; ty: Unknown | None
reveal_type(book.editor_id)  # Django: int | None;    ty: Unknown | None
reveal_type(book.sequel)     # Django: Book | None;   ty: Unknown | None
```

- **Status:** on the maintainer's stated list. Draft #29731 adds `foreign_key_model_type`, which
  handles a class object and yields nothing for a string; this gap would extend that function.
- **Approach sketch:** `"self"` resolves to the enclosing class. A bare `"Author"` resolves in
  the defining module's scope. Anything with a dot is gap 12.
- **Action:** do not start alone. Offer it on ty#1018 once the draft lands.

### 9. `Model(...)` and `create()` keyword checks

```python
Review(bok=book, rating=5)     # mypy: Unexpected attribute "bok"; ty: silent
Review.objects.create(nope=1)  # mypy: error; ty: silent
```

- **Status:** "precise model constructor signatures" is on the maintainer's list. TODOs exist at
  `django.md:75`, `:86`, `:134`.
- **Precedent in ty:** pydantic's field-to-parameter synthesis
  (`types/class/static_literal.rs:1942-2155`).
- **Risks:** false positives from `name=` renames, `<fk>_id` keywords, positional arguments,
  custom `__init__`, and `**kwargs` unpacking.
- **Note:** mypy's value-type checking here is weak (it accepted `rating="five"`), so name
  checking is where the value is.
- **Action:** coordinate. Do not start alone.

## Tier C: needs a design discussion

### 10 and 11. Reverse relations

```python
author.books        # related_name="books"
book.review_set     # default accessor
user.author_profile # reverse one-to-one
tag.books           # reverse many-to-many
book.ebook          # multi-table child
```

- **ty today:** `missing-attribute` on all five. These are false positives on correct code, which
  makes this the most visible gap.
- **Why it is hard:** the accessor lives on the target model but is declared on the referring
  model, possibly in another file. That needs an index of all models in the project. The only
  cross-file precedent in ty is pytest's bounded fixture search
  (`types/dedicated/pytest/fixtures.rs:130-207`). The default `<model>_set` name cannot be
  pre-filtered cheaply.
- **Possible first step (gap 10):** same-file reverse relations only. pyrefly shipped exactly
  that in its 1.3.0 release, which is useful precedent to cite.
- **Status:** on the maintainer's list, no design stated. TODO tests exist at
  `django.md:296-318`.
- **Workaround today:** annotate by hand, `books: RelatedManager[Book]`.
- **Action:** file a precise issue if none exists, and raise the same-file option on ty#1018.
  Build nothing until a design is agreed.

### 12. `"app.Model"` references

- `ForeignKey("shop.Author")` needs a map from app label to module. That means knowing
  `INSTALLED_APPS` or inferring apps from the directory layout.
- Design discussion only. Shares its hard part with gap 11.

### 13. `values()` and `values_list()` shapes

```python
Book.objects.values("title", "price")           # mypy: TypedDict; ty: dict[str, Any]
Book.objects.values_list("title", flat=True)    # mypy: str;       ty: Any
```

- ty has the result shapes available (synthesized TypedDict, `types/typed_dict.rs:218-247`;
  dynamic named tuple, `types/class.rs:633`). What is missing is special-casing these calls for
  literal string arguments.
- No maintainer position. Silent today, so it costs precision, not correctness.
- A version limited to own-model field names, with no `__` traversal, is the realistic scope to
  propose.

### 14. `annotate()` attributes

- `Book.objects.annotate(n=Count("review")).get().n` is a false `missing-attribute` in ty.
- Needs a per-call augmented model type. Large. Raise as an issue only.

### 15. Field-name checks in query methods

- `filter(titel="x")`, `order_by("nope")`, `select_related("nope")`, `values_list("nope")` are
  all silent in ty and all errors in mypy.
- The lookup syntax is a string language that crosses relations (`author__name__icontains`).
  Note that mypy's own checking is shallower than expected: it missed `title__bogus` and
  `author__nmae`.
- No maintainer position. Issue only.

### 16. `_meta.get_field`

- ty returns `Field[Any, Any]` and does not flag unknown names. Low value; literal arguments
  only. Not worth raising on its own.

## Tier D: do not build

### 17. Settings-driven behaviour

- `settings.DEBUG` and project settings are `Any` in ty; unknown settings are not flagged.
- `get_user_model()` and `request.user` give `AbstractUser` instead of the project's user model.
- A foreign key to `settings.AUTH_USER_MODEL` is `Any`.
- The automatic `id` is always `int`, ignoring `DEFAULT_AUTO_FIELD`.

All of these need ty to know the settings module. That means a configuration option or reading
project settings, and maintainers declined a library-specific option for pydantic. There is no
stated position for Django. The useful action is one well-argued issue asking how ty intends to
handle it, not code.

Workarounds today: cast `get_user_model()` results, or use a typed request subclass.

## Suggested sequence

1. Docs follow-up (gap 5). No dependencies, small, and it introduces us to the maintainers.
2. File precise issues for gaps 1, 7 and 10, each with a minimal reproduction.
3. On ty#1018, offer to take gap 1 and ask whether to wait for the django-stubs switch.
4. Diagnose gap 7 while waiting.
5. Stub fixes in django-stubs (gap 6) in parallel.
6. After the switch lands, re-run the head-to-head, update this file, then consider gaps 2, 3
   and 8.

## Before acting on this file

- Re-run the comparison after the django-stubs switch; several results will change.
- Check ty#1018 and the two drafts (#29731, #30068) for movement.
- The "approach" notes come from reading the code. Nothing here has been prototyped.
- No maintainer has said whether outside Django pull requests are welcome.
