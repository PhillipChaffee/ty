# Known Django behaviours under each stub package

Measured 2026-11-21. Our own working document; keep it out of any upstream pull request.

One probe file with 63 numbered probes was checked five ways. Every probe was first confirmed
against Django 6.1.3 at runtime. All model names are invented.

| Column | ty | Stub package |
|---|---|---|
| today, types | released 0.0.107 | django-types 0.24.0 |
| today, stubs | released 0.0.107 | django-stubs `44457d47` (unreleased) |
| stack, types | ruff fork `phillip/stubs-05-gap-tests` (`5416cf4`) | django-types 0.24.0 |
| stack, 6.1.2 | same | django-stubs 6.1.2 (released) |
| stack, stubs | same | django-stubs `44457d47` (unreleased) |

"stack, types" is identical to "today, types" for every probe, so it is left out of the tables.
`ok` means no diagnostic. One more difference is not a numbered probe: passing a `Choices` class as
`choices=` is accepted on django-types and reported as `invalid-argument-type` on both django-stubs
versions (astral-sh/ty#4551).

## Test file

Ruff fork branch `phillip/stubs-06-known-gaps` (`3f2f609`) holds all of this as tests in
`crates/ty_python_semantic/resources/mdtest/external/django.md`: 140 assertions, 40 `# TODO`
markers, pinned to unreleased django-stubs, all passing. The parent link tests live on
`phillip/django-parent-link` and are recorded here only as TODO lines.

The same file pinned to `django-types==0.24.0` (lock regenerated, not committed): 108 assertions
pass and 32 lines differ. The 32 are assertions whose expected value depends on the stub package:
foreign key IDs and string references (11), managers (4), user model (3), custom `QuerySet`
methods (3), field assignments (3), many-to-many fields (3), choices attributes (3), a `Choices`
class as `choices` (1), date string (1).

## Summary

| Group | Probes |
|---|---:|
| Works on django-types, breaks on the switch, fixed by the foreign-key stack | 10 |
| Works on django-types, breaks on the switch, not fixed | 6 |
| Checked on django-types, accepted after the switch (the stubs widen the accepted types) | 3 |
| Wrong on django-types, right after the switch | 5 |
| Gap before and after the switch | 31 |
| Same or equivalent before and after | 8 |

## Works on django-types, breaks on the switch, fixed by the foreign-key stack

| Probe | Behaviour | today, types | today, stubs | stack, 6.1.2 | stack, stubs |
|---|---|---|---|---|---|
| P08 | FK by class | `Author` | `Any` | `Author` | `Author` |
| P09 | nullable FK | `Author \| None` | `Any` | `Author \| None` | `Author \| None` |
| P10 | None to non-null FK | `error: invalid-assignment` | `ok` | `error: invalid-assignment` | `error: invalid-assignment` |
| P11 | fk id | `int` | `Any` | `Unknown` | `int` |
| P12 | nullable fk id | `int \| None` | `Any \| None` | `Unknown \| None` | `int \| None` |
| P13 | fk id with to_field | `str` | `Unknown + error: missing-attribute` | `Unknown` | `str` |
| P19 | one-to-one | `Author` | `Any` | `Author` | `Author` |
| P20 | one-to-one id | `int` | `Any` | `Unknown` | `int` |
| P21 | pk via one-to-one | `int` | `Any` | `Unknown` | `int` |
| P36 | date navigation on nullable field | `error: missing-attribute` | `ok` | `error: missing-attribute` | `error: missing-attribute` |

## Works on django-types, breaks on the switch, not fixed

| Probe | Behaviour | today, types | today, stubs | stack, 6.1.2 | stack, stubs |
|---|---|---|---|---|---|
| P55 | user manager | `AbstractUser` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P56 | request.user | `AbstractUser \| AnonymousUser` | `AbstractBaseUser \| AnonymousUser` | `AbstractBaseUser \| AnonymousUser` | `AbstractBaseUser \| AnonymousUser` |
| P57 | request.user attribute | `ok` | `error: missing-union-attribute` | `error: missing-union-attribute` | `error: missing-union-attribute` |
| P40 | queryset method via as_manager | `Unknown` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P41 | queryset method via from_queryset | `Unknown` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P53 | missing class attribute | `error: missing-attribute` | `error: invalid-attribute-access` | `error: invalid-attribute-access` | `error: invalid-attribute-access` |

## Checked on django-types, accepted after the switch (the stubs widen the accepted types)

| Probe | Behaviour | today, types | today, stubs | stack, 6.1.2 | stack, stubs |
|---|---|---|---|---|---|
| P03 | wrong type to CharField | `error: invalid-assignment` | `ok` | `ok` | `ok` |
| P04 | wrong type to IntegerField | `error: invalid-assignment` | `ok` | `ok` | `ok` |
| P06 | string to automatic id | `error: invalid-assignment` | `ok` | `ok` | `ok` |

## Wrong on django-types, right after the switch

| Probe | Behaviour | today, types | today, stubs | stack, 6.1.2 | stack, stubs |
|---|---|---|---|---|---|
| P05 | ISO date string | `error: invalid-assignment` | `ok` | `ok` | `ok` |
| P39 | as_manager manager | `BaseManager[Book]` | `Manager[Book, BookQuerySet]` | `Manager[Book]` | `Manager[Book, BookQuerySet]` |
| P42 | queryset method after all() | `Unknown` | `BookQuerySet` | `Unknown + error: missing-attribute` | `BookQuerySet` |
| P43 | default manager all() | `BaseManager[Author]` | `QuerySet[Author, Author]` | `QuerySet[Author, Author]` | `QuerySet[Author, Author]` |
| P54 | manager on instance | `ok` | `error: missing-attribute` | `error: missing-attribute` | `error: missing-attribute` |

## Gap before and after the switch

| Probe | Behaviour | today, types | today, stubs | stack, 6.1.2 | stack, stubs |
|---|---|---|---|---|---|
| P07 | reset pk | `error: invalid-assignment` | `error: invalid-assignment` | `ok` | `error: invalid-assignment` |
| P14 | string reference | `Unknown` | `Any` | `Unknown` | `Any` |
| P15 | nullable string reference | `Unknown \| None` | `Any` | `Any \| None` | `Any \| None` |
| P16 | string reference id | `Unknown` | `Any` | `Unknown` | `Any` |
| P17 | app-label string reference | `Unknown` | `Any` | `Unknown` | `Any` |
| P18 | self reference | `Unknown \| None` | `Any` | `Any \| None` | `Any \| None` |
| P22 | plain ForeignKey subclass | `Unknown` | `Any` | `Unknown` | `Any` |
| P23 | reverse accessor related_name | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P24 | reverse accessor default | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P25 | reverse one-to-one | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P26 | related_name with %(class)s | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P27 | multi-table child accessor | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P28 | parent link | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P29 | parent link id | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P31 | many-to-many through | `Unknown` | `type[Any]` | `type[Any]` | `type[Any]` |
| P32 | renamed field new name | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P33 | renamed field old name | `int` | `int` | `Unknown` | `int` |
| P37 | pk on abstract-typed value | `Any` | `Any` | `Any` | `Any` |
| P38 | id on abstract-typed value | `error: missing-attribute` | `error: missing-attribute` | `error: missing-attribute` | `error: missing-attribute` |
| P45 | values row | `dict[str, Any]` | `dict[str, Any]` | `dict[str, Any]` | `dict[str, Any]` |
| P46 | values_list row | `Any` | `Any` | `Any` | `Any` |
| P47 | values_list flat | `Any` | `Any` | `Any` | `Any` |
| P48 | annotate attribute | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` | `Unknown + error: missing-attribute` |
| P49 | unknown lookup | `ok` | `ok` | `ok` | `ok` |
| P50 | unknown constructor keyword | `ok` | `ok` | `ok` | `ok` |
| P51 | wrong constructor value type | `ok` | `ok` | `ok` | `ok` |
| P52 | per-model exception | `type[ObjectDoesNotExist]` | `type[ObjectDoesNotExist]` | `type[ObjectDoesNotExist]` | `type[ObjectDoesNotExist]` |
| P58 | settings | `Any` | `Any` | `Any` | `Any` |
| P59 | unknown setting | `ok` | `ok` | `ok` | `ok` |
| P62 | get_user_model() as a type | `error: invalid-type-form` | `error: invalid-type-form` | `error: invalid-type-form` | `error: invalid-type-form` |
| P63 | value typed with get_user_model() | `Unknown` | `Unknown` | `Unknown` | `Unknown` |

## Same or equivalent before and after

| Probe | Behaviour | today, types | today, stubs | stack, 6.1.2 | stack, stubs |
|---|---|---|---|---|---|
| P01 | plain field | `str` | `str` | `Unknown` | `str` |
| P02 | nullable field | `date \| None` | `date \| None` | `Unknown` | `date \| None` |
| P30 | many-to-many manager | `ManyToManyRelatedManager[Tag, Unknown]` | `ManyRelatedManager[Tag, Any]` | `ManyRelatedManager[Tag, Any]` | `ManyRelatedManager[Tag, Any]` |
| P34 | display method | `str` | `str` | `str` | `str` |
| P35 | date navigation | `ok` | `ok` | `ok` | `ok` |
| P44 | first() | `Author \| None` | `Author \| None` | `Author \| None` | `Author \| None` |
| P60 | choices | `Sequence[tuple[Status, str]]` | `list[tuple[str, str \| _StrPromise]]` | `list[tuple[str, str \| _StrPromise]]` | `list[tuple[str, str \| _StrPromise]]` |
| P61 | choice label | `str` | `str \| _StrPromise` | `str \| _StrPromise` | `str \| _StrPromise` |

## Notes

- P40 and P41 (custom `QuerySet` methods on a manager) are silent `Unknown` on django-types and a
  false `missing-attribute` on django-stubs. Neither is right; the switch turns a silent gap into
  a false error.
- P53: the diagnostic for a missing class attribute changes from `missing-attribute` to
  `invalid-attribute-access`, because django-stubs declares `objects` through a metaclass
  `__getattr__`.
- P28 and P29 (parent links) are fixed on `phillip/django-parent-link`, which is not part of the
  stack.
- P07 (`pk = None`) is astral-sh/ty#4932, with the maintainer's draft astral-sh/ruff#30068.
- The probe file and the raw outputs were in the session scratchpad and are not kept.
