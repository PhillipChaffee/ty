## Scoping - public statements and ecosystem context for ty's django-types -> django-stubs switch

### Answer
ty's Django support (first merged Oct 22, 2026) was deliberately built on `django-types` as a stopgap, because `django-stubs` field constructors gave `CharField[Unknown, Unknown]` without special-casing private `_pyi_private_{set,get}_type` hints. django-stubs maintainers then removed that obstacle upstream (PR #3763, merged Nov 19, 2026, **not yet in a PyPI release**). sharkdp's draft ruff#29731 pins a fork commit of that PR. django-stubs has roughly 9x the downloads of django-types, is what pyrefly recommends, and is what the Django projects in mypy_primer's upstream list install.

Access caveat: github.com HTML was readable only through a summarising fetcher (curl got 403, the GitHub MCP is scoped to forks). Quotes below are short verbatim fragments returned by that fetcher; longer passages are paraphrase. Nothing was read as raw HTML.

### (a) Verified from pages

**1. astral-sh/ty#1018** (https://github.com/astral-sh/ty/issues/1018) - "dedicated support for Django", opened Aug 16, 2025 by aaschenbrener; labels `django`, `library`; removed from milestone "ty-1.1" on Nov 18, 2026.
- carljm, Aug 16, 2025: "We would like to add some kind of Django support in future".
- carljm, Apr 2, 2026: "My inclination is that this feature should be always-on and not require any additional configuration."
- sobolevn (django-stubs maintainer), Apr 3, 2026: django-stubs added ty support, but for model checking "Only mypy plugin can do that."
- sharkdp, Nov 2, 2026: "Django support in ty currently relies on the `django-types` stub package"; "we plan to support `django-stubs` as the default stub package soon" (links ruff#29642#issuecomment-6368241066); "We try to rely on externally provided stubs (`django-stubs`, `django-types`) as much as possible". His upcoming list: django-stubs support; reverse FK/one-to-one accessors; stringified lazy relations; precise model constructor signatures.
- sharkdp, Nov 2, 2026: "ty does not have a plugin system (yet?)."
- User reports:
  - McDinii, Mar 6, 2026: "django-types works after" 0.0.21.
  - ronaldorcampos, Apr 1, 2026: "you just need to have django-stubs installed."
  - WhyNotHugo, Apr 1, 2026: "django-types seems to necessitate manual type declaration of all the fields"; reverse FK fails with both.
  - kalekseev, May 1, 2026: "django-types on main branch works good enought with ty", with an ArrayField bug.
  - johnthagen, Nov 2, 2026: asks for a feature-gap list against the django-stubs mypy plugin and suggests running its tests against ty.
  - regularkevvv, Jul 14, 2026: a ty fork with WASM plugins.

**2. ruff#29642** (https://github.com/astral-sh/ruff/pull/29642) - "[ty] Very basic Django support", sharkdp, merged Oct 22, 2026. The description calls django-types "a fork of django-stubs which requires less special-casing in type checkers". Ecosystem bot: 2,533 `unresolved-attribute` removed, 0 added.
- ngnpope (django-stubs maintainer), Oct 23, issuecomment-6362273924:
  - "there is an ongoing effort to improve `django-stubs` to work better with other type checkers"
  - django-types "partially syncs from `django-stubs`", and "it's typically behind the latest Django release"
  - "Our intent is that `django-stubs` will support all type checkers stubs-only as best as possible", with "the mypy plugin being entirely optional".
- **issuecomment-6368241066 is by sharkdp himself** (Oct 23), replying to ngnpope:
  - "I didn't want to add special handling for those magic `_pyi_private_{set,get}_type` fields"
  - "Really the only thing that was problematic with django-stubs are the constructors on field classes like `CharField`"
  - "I am mainly wondering if it's worth switching to `django-stubs` _right now_"
  - He says he wants to build on django-stubs, had emailed UnknownPlatypus, and may later contribute tests to django-stubs' `tests/assert_type`.
- ngnpope, Oct 23: "Probably worth waiting until the field changes land".

**3. ruff#29731** (https://github.com/astral-sh/ruff/pull/29731) - draft, sharkdp, opened Oct 26, 2026, label `ty`, 2 commits, last push Oct 26. No human reviewers. Test Plan is empty.
- Diff (https://patch-diff.githubusercontent.com/raw/astral-sh/ruff/pull/29731.diff):
  - `django.md` and `django.lock` move from `django-types==0.24.0` to `django-stubs @ git+https://github.com/UnknownPlatypus/django-stubs.git@5f2e45b...`. This adds real `django` 6.1.2, `django-stubs-ext`, asgiref, sqlparse and others to the lock.
  - New ForeignKey special-casing in `constructor.rs` and `dedicated/django.rs`. sharkdp's inline note says it "could be removed" with upstream FK work.
  - `foreign_key_id_member` now goes through `__get__`.
  - Test changes: `book.published = "1980-10-12"` no longer errors; `get_next_by_<nullable field>` loses its expected `unresolved-attribute` (a regression, marked TODO).
- Bots (Oct 26): conformance unchanged; memory unchanged; ecosystem 9 added `unresolved-attribute`, 5 removed, 4 changed, all in zulip, flaky changes excluded.
- Predecessor ruff#29675 (https://github.com/astral-sh/ruff/pull/29675), "[ty] Support Django fields with django-stubs", read the `_pyi_private_*` hints. Closed unmerged Oct 26. Its ecosystem run: 46 added, 155 removed, 14 changed. UnknownPlatypus there said he backported django-types improvements and hopes the two projects can merge back together.

**4. django-stubs#3763** (https://github.com/typeddjango/django-stubs/pull/3763) - "Resolve field nullability at the call site with `__init__` overloads", by UnknownPlatypus, opened Oct 25, merged Nov 19, 2026. Approved by sobolevn, ngnpope, FallenDeity; sharkdp reviewed `related.pyi`.
- Removes the `_pyi_private_*` hints; uses PEP 696 defaults plus two `__init__` overloads per field.
- Breaking effects: `x: models.IntegerField = models.IntegerField(null=True)` is rejected; bad kwargs report `call-overload` instead of `arg-type`; custom Field subclasses must declare defaults or redefine overloads.
- Smoke table covers pyrefly 1.4.0, pyright 1.1.414, ty 0.0.90, mypy 2.4.0, zuban 0.10.1. ty accepts a nullable field assigned to a non-null annotation by design (astral-sh/ty#4977, closed not planned, https://github.com/astral-sh/ty/issues/4977).
- Follow-ups listed: FK overloads; FilePathField, RasterField, HStoreField, GeometryField; a pyrefly issue; zuban dropping `_pyi_private_*`; migration PRs for django-mysql and similar; deleting plugin code. A possible `_ST`/`_GT` order swap was deferred to a separate issue.
- ngnpope, Nov 13: it resolves many ty errors, but a larger repo still showed about 200-500.
- Release status: latest PyPI is 6.1.2, Oct 5, 2026 (https://pypi.org/pypi/django-stubs/json), which predates the merge. The README's top compatibility row is "unreleased".
- README (https://github.com/typeddjango/django-stubs): "ty: basic support, checked in CI", same wording for pyright and pyrefly. Without the plugin, reverse accessors must be declared by hand.
- Related: pyrefly#5532 (https://github.com/pyrefly-org/pyrefly/issues/5532) - pyrefly currently reads `_pyi_private_*`.

**5. Other ty issues**
- #4932 (https://github.com/astral-sh/ty/issues/4932), open, `instance.pk = None` rejected. sharkdp, Nov 9: "I think this will be easier to fix once we rely on `django-stubs` (instead of `django-types`) for Pydantic support." ("Pydantic" looks like a slip for Django.)
- #4822 and #4847: both closed. They mention only django-types, in repro commands and kalekseev's "I've been using django-types with ty for a few months now."

**6. ty docs**
- `docs/features/third-party/django.md` (https://raw.githubusercontent.com/astral-sh/ty/main/docs/features/third-party/django.md): support works "when the `django-types` stub package is installed"; setup is `uv add --dev django-types`. Its note: "Support for the alternative `django-stubs` package is planned, but for now you must use `django-types` exclusively to avoid conflicting stub files."
- `docs/coming-from-mypy-or-pyright.md`: no Django text (grep found nothing).

**7. Other checkers**
- pyrefly (https://pyrefly.org/en/docs/django/): "Install django-stubs"; built-in support for id/pk/`<fk>_id`, forward FK, M2M, Choices, generic views. No reverse relations.
- django-types README (https://github.com/sbdchd/django-types): "forked from ... django-stubs with the goal of removing the mypy plugin dependency". It requires hand-declared `id`, `<fk>_id` and reverse managers, and names mypy and pyright.
- pyright docs (https://github.com/microsoft/pyright/blob/main/docs/type-stubs.md): Django appears only as a `--createstub` example; no stub package is recommended.

**8. Adoption** (pypistats, PyPI, repo pages; fetched 2026-11-21)

| | django-stubs | django-types |
|---|---|---|
| Downloads, last month | 14,872,850 | 1,633,070 |
| Latest release | 6.1.2, 2026-10-05 | 0.24.0, 2026-04-22 |
| Release cadence | 6 releases Jul-Oct 2026 | 0.23.0 in Feb 2026, 0.22.0 in Jul 2025 |
| Stars | 2.0k | 347 |
| Open issues / PRs | 69 / 31 | 53 / 10 |

**9. Ecosystem projects**
- Local `/home/user/ruff/crates/ty_python_semantic/resources/primer/` holds only `flaky.txt`; the project list is not in the repo.
- Upstream mypy_primer (https://raw.githubusercontent.com/hauntsaninja/mypy_primer/master/mypy_primer/projects.py): zulip, django-test-migrations and django-modern-rest install `django-stubs`; the django-stubs repo itself is a project; strawberry installs `django`. None install django-types.
- The local checkout still pins `django-types==0.24.0` in `/home/user/ruff/crates/ty_python_semantic/resources/mdtest/external/django.md` and `django.lock`. `/home/user/ruff/crates/ty_python_semantic/src/types/dedicated/django.rs:396` has a django-types-specific comment.

### (b) Not loaded or uncertain
- #1018's first fetch showed "Load more: 19 remaining items"; `?timeline_page=1` returned the middle comments. Full comment bodies were not seen verbatim.
- sharkdp's resolved review comments on django-stubs#3763 `related.pyi` are hidden.
- Not checked: stack PR ruff#29732, the full ecosystem diff for #29731, and whether ecosystem-analyzer uses upstream mypy_primer or a fork's list.
- Pylance/basedpyright bundling of django-stubs: not confirmed. The one basedpyright page fetched says nothing about it.
- django-types last-commit date not shown.

### Confidence
Medium-high on facts and dates; medium on exact quote wording, since it came through a summariser.

### Open questions
1. When will django-stubs release #3763 (6.2 or 7.0?), and will the `_ST`/`_GT` swap land in the same breaking release? Can ty docs recommend django-stubs before that release?
2. What happens for users with released django-stubs 6.1.2 (still has `_pyi_private_*`) or with django-types? Will ty support both, detect which is installed, or drop django-types? What about the "conflicting stub files" case when both are installed?
3. django-stubs requires real `django` and `django-stubs-ext`. What are the effects on the mdtest lockfile and user setup?
4. Is the upstream FK-overload follow-up done, so ty's new ForeignKey special-casing can be removed?
5. What are the 9 new zulip `unresolved-attribute` errors (`named_user_group`), and why the `get_next_by_` regression for nullable fields?
6. What do the Any-vs-Unknown changes mean for `unsound-*` diagnostics?
7. Does #4932 (`pk = None`) actually get fixed by django-stubs' `pk` typing?
8. What is the plan for third-party stubs built on django-stubs (djangorestframework-stubs, django-mysql, custom Field subclasses)?
9. What do #29732 and later ruff PRs/commits since Oct 26 contain? The draft has had no pushes since then.
10. What is django-types' maintainer stance on merging back?