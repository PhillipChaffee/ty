# Glossary of terms and names already used in ty

Words and identifiers that ty's docs, tests, changelog and source already use, collected so that
our changes reuse them and do not invent new ones. Dated 2026-11-20. Our own working document;
keep it out of any upstream pull request.

How to use it: before naming a function, a test section, a docs heading or a concept, look for
the existing word here. If two words exist for one idea, the "Where" column says which register
each belongs to (user docs, tests, changelog, Rust source).

## Sources

Everything below was read from these places. Nothing is from memory.

| Short name | What |
|---|---|
| docs | `docs/` in astral-sh/ty at `8eef928` (ty 0.0.107) |
| changelog | `CHANGELOG.md` in astral-sh/ty at `8eef928` |
| `django.rs` | `crates/ty_python_semantic/src/types/dedicated/django.rs` in astral-sh/ruff at `9ca2a80e78` (main on 2026-11-20) |
| `django.md` | `crates/ty_python_semantic/resources/mdtest/external/django.md`, same commit |
| source | other files under `crates/ty_python_semantic/src` and `crates/ty_python_core/src`, same commit |
| mdtest README | `crates/ty_test/README.md`, same commit |

Not covered: the language server and IDE crates, the CLI reference, configuration option names,
and the pytest support beyond its top-level names. The `Type` list is complete for the commit
read; the other source lists are the names the Django code touches or sits next to.

## 1. Product, repositories and packages

| Term | Meaning | Note |
|---|---|---|
| ty | The type checker. Always lowercase, also at the start of a sentence | docs |
| Ruff / ruff | The repository that holds ty's Rust source (`crates/ty*`) | "the Ruff submodule" in CONTRIBUTING |
| typeshed | The standard-library stubs ty vendors | |
| `ty_extensions` / `ty-extensions` | Module (underscore) and PyPI package (hyphen) with ty-only type forms | docs |
| `django-types` | The stub package Django support relies on today | docs, `django.md` |
| `django-stubs` | "the alternative `django-stubs` package"; support "is planned" | docs |
| stub package, stubs, stub files | A package of `.pyi` files | docs use all three |
| playground | play.ty.dev | docs link "Full example in the playground" |
| mdtest | A Markdown test file and the framework that runs it | lowercase, one word |
| first-party / third-party modules | Your project's code versus installed dependencies | `docs/modules.md` |
| Python environment | Where ty finds third-party modules | `docs/modules.md` |

Crates under `crates/` in ruff: `ty`, `ty_combine`, `ty_completion_bench`, `ty_completion_eval`,
`ty_ide`, `ty_module_resolver`, `ty_project`, `ty_python_core`, `ty_python_semantic`, `ty_server`,
`ty_site_packages`, `ty_static`, `ty_test`, `ty_vendored`, `ty_wasm`.

## 2. How ty talks about library support

| Term | Meaning | Where |
|---|---|---|
| third-party library support | The docs section title | docs |
| built-in support | "ty has built-in support for type inference of Django models" | docs |
| built-in type checking support | Used for Django and Pydantic | docs index |
| specialized language server behavior | Used for pytest | docs index |
| dedicated support | Issue title and label wording ("dedicated support for Django") | ty#1018 |
| `dedicated` | The Rust module that holds per-library code: `types/dedicated/{django,pydantic,pytest}` | source |
| plugin, plugin system | Only ever used to say ty has none | Typing FAQ |
| Features | First heading on a library page | docs |
| "We support the following features:" | Sentence that opens the feature list | docs |
| Setup | Heading for installation steps | docs (Django) |
| Differences from runtime behavior | Heading for places where static results differ from the library at runtime | docs |
| Known limitations | Heading for the short list of gaps | docs |
| "does not yet", "is not fully reflected", "is incomplete" | How limitations are phrased | docs |

Each library page keeps to its own bullet openers. The Django page uses only "Type inference and
assignment checking for", "Recognition of" and "Inference of ... for". "Support for" and
"Rejection of" appear on the Pydantic page only. A section on the Django page opens with what
Django does, then what ty does: "Django adds methods based on a field's options. ty infers their
return types:".

Verbs the feature lists use: "Type inference and assignment checking for", "Recognition of",
"Inference of types for", "Inference of return types for", "Support for", "Rejection of".
Changelog verbs: "Infer", "Recognize", "Support", "Avoid synthesizing", "suppress", "Respect",
"Report", "Preserve", "Accept", "Detect".

## 3. Django vocabulary

### Concepts

| Term | Meaning | Where |
|---|---|---|
| model | A subclass of Django's `Model` | everywhere |
| Django model | Used when the library is not clear from context | docs, changelog |
| basic model | The plain starting case in a test | `django.md` section title |
| model field, field | A class attribute whose type inherits from Django's `Field` | docs, `django.rs` |
| field definition | The assignment that declares a field | `django.md` |
| field construction | The call that creates the field, e.g. `CharField(max_length=13)` | `django.rs` doc comments |
| metadata | Facts read from a field's or model's definition (`FieldMetadata`, `ModelMetadata`) | `django.rs` |
| value type | The type you read from a field attribute | `django.md`, `django.rs` |
| input type | The type a field accepts on assignment ("checked against the field's *input* type") | `django.md` |
| nullable field | A field declared with `null=True` | docs, `django.md` |
| non-nullable | The opposite; used for date fields | docs, changelog |
| primary key | The model's key field | everywhere |
| automatic primary key | The key Django adds when none is declared | docs, `django.md`, `django.rs` |
| automatic `id` field, automatic `id` | The attribute that carries the automatic primary key | docs, changelog |
| custom primary key | A key declared with `primary_key=True` | `django.md` |
| explicit primary key, explicit `id` field | A key or `id` the user declared | `django.md`, `django.rs` |
| `pk` alias | "`pk` is an alias for the primary key" | docs, `django.md` |
| foreign key | Prose form | docs, changelog |
| `ForeignKey`, `OneToOneField` | Code form, used when naming the class | `django.md`, changelog |
| forward foreign-key relationship | Access from the declaring model to the target | docs |
| relationship | Docs word for a relation between models | docs |
| relation field | Source word for a `ForeignKey`-like field | `django.rs` |
| foreign key ID | The `<field>_id` attribute; section title "Foreign key IDs" | `django.md` |
| stored ID type | The type of the value a relation field stores | `django.rs` |
| related model | The model a foreign key points to | docs, `django.md`, `django.rs` |
| target model | Same thing, used in the limitations list and in draft ruff#29731 | docs |
| referenced field, referenced instance | What `to_field` or the foreign key points at | `django.md`, changelog |
| explicit target field | Section title for `to_field` | `django.md` |
| source model | The model that declares the foreign key | `django.md` |
| reverse accessor | The attribute Django adds to the related model | `django.md` |
| reverse relationship attributes | Docs phrase for the same thing | docs |
| string reference | A model named by a string, e.g. `ForeignKey("Book")` | docs |
| stringified lazy relationships | The maintainer's phrase for the same thing | ty#1018 |
| choices | The `choices` parameter; section title "Choices" | docs, `django.md` |
| generated methods | Methods Django adds from field options | docs heading |
| date navigation | `get_next_by_<field>()` and `get_previous_by_<field>()` | `django.md`, `django.rs` |
| date field | Any field that inherits from `DateField`, including `DateTimeField` | `django.md`, `django.rs` |
| abstract model | A model whose own `Meta` sets `abstract = True` | `django.md`, changelog |
| concrete subclass, concrete | A non-abstract model | `django.md`, `django.rs` |
| `Meta` configuration | The inner `Meta` class | changelog, `django.rs` |
| inherited `Meta` configuration | A `Meta` that subclasses a parent's `Meta` | `django.md` section title |
| field name, field renaming | The `name` parameter; "Field names" section | docs, `django.md` |
| model constructor | `Model(...)`; "precise model constructor signatures" | docs, ty#1018 |
| follows | The verb for "takes its type from": "whose type follows the model's primary key", "The ID type follows the related primary key" | docs, `django.md` |
| parent, parent model | The model a subclass inherits from ("inherits the primary key behavior of its parent") | `django.md` |
| abstract base | An abstract model used as a base class | `django.md` |
| override, inherit | What a child's `Meta` does to a parent's `Meta` | changelog, `django.md` |
| own | Prefix meaning "declared in this class body, not inherited": `own_model_fields`, `own_primary_key`, `own_meta` | `django.rs` |
| synthesized | Added by ty, not present in the stubs: "synthesized attributes and methods" | `django.rs`, changelog |

Placeholders are written `<field>`, as in `<field>_id`, `get_<field>_display()`,
`get_next_by_<field>()`. Docs and tests never write `FOO` or `{field}`.

### Example names the tests and docs already use

`Book`, `Author`, `Review`, `Ebook`, `Article`, with fields `isbn`, `title`, `rating`,
`published`, `status`, `author`, `book`.

### Rust names in `django.rs`

| Name | Kind | Purpose |
|---|---|---|
| `is_model` | function | Whether a class has Django's `Model` in its MRO |
| `Field` | struct | A model field: `name`, `ty`, `metadata` |
| `Field::from_definition` | function | Reads metadata from the field's definition |
| `FieldMetadata` | struct | `primary_key`, `has_choices`, `null`, `to_field` |
| `own_model_fields` | Salsa query | Fields declared in this class body |
| `ModelMetadata` | struct | `is_abstract` |
| `model_metadata` | Salsa query | Reads this model's own `Meta` |
| `own_meta` | function | The `Meta` class declared in this class body |
| `synthesized_member` | function | Entry point; "a quick filter on the name" comes first |
| `primary_key_member` | function | `id` and `pk` |
| `own_primary_key` | function | The field with `primary_key=True` in this class body |
| `foreign_key_id_member` | function | `<field>_id` |
| `foreign_key_id_type` | function | Shared by `<field>_id` and `pk` |
| `display_method` | function | `get_<field>_display()` |
| `date_navigation_method` | function | `get_next_by_<field>()`, `get_previous_by_<field>()` |

Naming pattern: `<thing>_member` returns an attribute type, `<thing>_method` returns a callable,
`<thing>_type` is a shared helper, `own_<thing>` looks only at the class body.

Known classes: `KnownClass::DjangoModel`, `DjangoField`, `DjangoDateField`, `DjangoForeignKey`.
Known modules: `KnownModule::DjangoDbModelsBase`, `DjangoDbModelsFields`,
`DjangoDbModelsFieldsRelated`.

Call sites outside the module: `django::synthesized_member` in `types/class/static_literal.rs`
and `django::is_model` in `types/overrides/attributes.rs` (the `Meta` override exemption).

### Section titles in `django.md`

Basic model; Nullable fields; Field names; Primary keys (Automatic primary key, Custom primary
key, Explicit `id` field, ForeignKey and OneToOneField as primary keys); Foreign key IDs
(Automatic primary key, Custom primary key, Explicit target field); Choices; Date navigation;
Abstract models (Basic, Annotated abstract setting, Inherited Meta configuration, Multiple
inheritance).

## 4. How types are displayed

Use these spellings in `# revealed:` comments and in prose.

| Display | Meaning | Where |
|---|---|---|
| `Unknown` | A type that could not be fully inferred; behaves like `Any` but appears implicitly | Typing FAQ |
| `Any` | The explicit dynamic type | |
| `@Todo` | A type ty cannot infer yet because of a missing feature in ty | Typing FAQ |
| `Divergent` | Type-level recursion that does not converge | Typing FAQ |
| `Never` | The empty set of values | source |
| `Literal[1]`, `Literal["a"]` | Literal value types | mdtest README |
| `A \| B` | Union | |
| `A & B`, `~A` | Intersection and negation | `docs/features/type-system.md` |
| `Top[...]`, `Bottom[...]` | Top and bottom materializations | docs, `ty_extensions` |
| `float*`, `complex*` | Explained in the Typing FAQ | Typing FAQ |
| `<class 'Meta'>` | A class object (class literal) | observed in ty 0.0.92 output |
| `AlwaysTruthy`, `AlwaysFalsy` | Objects whose truthiness is fixed | source, `ty_extensions` |
| `Self` | Shown for methods synthesized with a `Self` type variable | `django.md` |

Words for kinds of types: dynamic type, gradual type, fully static type, materialization,
subtype, assignable, redeclaration, narrowing, reachability.

`ty_extensions` names seen: `Intersection`, `Not`, `Top`, `Bottom`, `AlwaysTruthy`,
`AlwaysFalsy`, `static_assert`.

## 5. Diagnostics and rules

| Term | Meaning |
|---|---|
| rule | A named check, e.g. `missing-attribute`. Written in backticks, kebab-case |
| diagnostic | One reported finding |
| violation | What a rule reports (`docs/rules.md`) |
| level | `error`, `warn` or `ignore` |
| suppression comment | `# ty: ignore[rule-name]` |
| baseline | A recorded set of existing diagnostics |
| false positive | An error on correct code; the stated reason for library support |
| sub-diagnostic | Extra detail attached to a diagnostic (contributor docs) |

Rules that come up in Django work, with their current names in 0.0.107:

| Rule | When |
|---|---|
| `missing-attribute` | Attribute does not exist |
| `possibly-missing-attribute` | Attribute may not exist |
| `invalid-assignment` | Value not assignable to the declared type |
| `invalid-argument-type` | Argument type does not match the parameter |
| `unknown-argument` | Unknown keyword argument |
| `missing-argument` | Required argument not provided |
| `incompatible-attribute-override` | Subclass attribute not compatible with the base (the `Meta` case) |
| `incompatible-method-override` | Same for methods |
| `no-matching-overload` | No overload accepts the call |
| `unresolved-reference` | Name not defined |
| `pydantic-discarded-extra-argument` | The only library-specific rule so far |

Rule names have changed. Use the current name and check `docs/reference/rules.md` first:

- ty 0.0.92 printed `unresolved-attribute`; 0.0.107 prints `missing-attribute`.
- ty 0.0.92 printed `invalid-attribute-override`; the 0.0.107 rule list has
  `incompatible-attribute-override`.
- The changelog entry for ruff#29769 says "invalid-override errors".

Rule name patterns in the current list: `invalid-*`, `missing-*`, `possibly-missing-*`,
`incompatible-*-override`, `unresolved-*`, `unsupported-*`, `unknown-*`, `redundant-*`,
`unused-*`, `inconsistent-*`, `unsound-*`.

Message shape seen: "Object of type `X` has no attribute `y`"; "Invalid assignment to data
descriptor attribute `title` on type `Book`: Expected `...`, found `...`".

## 6. Type-system names in the Rust source

### Variants of `Type`

`Dynamic`, `Divergent`, `Recursive`, `RecursiveVar`, `Never`, `FunctionLiteral`, `BoundMethod`,
`KnownBoundMethod`, `WrapperDescriptor`, `DataclassDecorator`, `DataclassTransformer`,
`Callable`, `ModuleLiteral`, `ClassLiteral`, `GenericAlias`, `SubclassOf`, `NominalInstance`,
`ProtocolInstance`, `SpecialForm`, `KnownInstance`, `PropertyInstance`, `SlotDescriptor`,
`Union`, `Intersection`, `EnumComplement`, `AlwaysTruthy`, `AlwaysFalsy`, `LiteralValue`,
`TypeVar`, `BoundSuper`, `TypeIs`, `TypeGuard`, `TypeForm`, `TypedDict`, `TypeAlias`,
`NewTypeInstance`.

### Classes

| Name | Meaning |
|---|---|
| class literal | A specific class object |
| `ClassLiteral` | `Static`, `Dynamic`, `DynamicNamedTuple`, `DynamicTypedDict`, `DynamicEnum` |
| `StaticClassLiteral` | A class defined with a `class` statement. The Django code works on this |
| `DynamicClassLiteral` | A class created with `type(name, bases, dict)` |
| `ClassType` | `NonGeneric(ClassLiteral)` or `Generic(GenericAlias)` |
| `GenericAlias` | A specialization of a generic class |
| `ClassBase` | An entry in an MRO: `Any`, `Dynamic`, `Divergent`, `Class`, `Protocol`, ... |
| MRO | Method resolution order; walked with `iter_mro` |
| `KnownClass`, `KnownModule`, `KnownFunction` | Classes, modules and functions ty recognizes by name |
| `is_known` | Test against a `KnownClass` |
| body scope | The scope of a class body (`body_scope`) |
| nominal instance / `nominal_class` | An instance of a class, and the class behind it |
| `SubclassOf` | The type spelled `type[C]` |
| `CodeGeneratorKind` | `DataclassLike`, `Pydantic`, `NamedTuple`, `TypedDict`: classes whose members are generated |
| specialization, `Specialization` | Type arguments applied to a generic class |
| generic context, `GenericContext` | The type variables a class or function binds |
| `to_instance_approximation` | Turn a class-like type into the instance type; used to avoid hardcoding `int` |

### Callables

`Signature`, `Parameters`, `Parameter` (`positional_only`, `positional_or_keyword`,
`keyword_variadic`), `with_annotated_type`, `Type::function_like_callable`,
`BoundTypeVarInstance::synthetic_self`, `BindingContext::Synthetic`. "Synthetic" is the word for
type variables and protocols ty creates; "synthesized" is the word for members and signatures.

### Places, scopes and definitions

| Name | Meaning |
|---|---|
| place | Something that can hold a value: a symbol or a member |
| `Place` | `Defined(...)` or `Undefined` |
| `Definedness` | `AlwaysDefined` or `PossiblyUndefined` |
| `TypeOrigin` | `Declared` or `Inferred` |
| declared type / inferred type | From an annotation / from the assigned value |
| public type | The type of a symbol as seen from outside its scope |
| symbol | A name in a scope |
| member | An attribute looked up on a type or in a class body (`class_member`, `.member(...)`) |
| binding | An assignment to a place |
| declaration | An annotation for a place |
| definition, `Definition`, `DefinitionKind` | One binding or declaration site, e.g. `Assignment`, `AnnotatedAssignment` |
| scope | A module, class or function body |
| semantic index, `semantic_index` | Per-file tables of scopes, places and definitions |
| place table, `place_table` | The places of one scope |
| use-def map, `use_def_map` | Which bindings reach which use; `end_of_scope_symbol_bindings` |
| `ProgramEnvironment`, `env` | Passed next to `db` in current main |
| `ignore_possibly_undefined` | Take the type if the place is defined at all |

### Salsa and performance

`db` (always the first parameter), `#[salsa::tracked]`, query, tracked, interned, incrementality,
cycle, `heap_size`, `get_size2::GetSize`, boxed slice (`Box<[T]>`).

## 7. Test vocabulary

| Term | Meaning |
|---|---|
| mdtest | A Markdown test; each header section is one test |
| assertion | `# revealed: <type>` or `# error: [rule-code]`, optionally with a `"message substring"` |
| `# TODO:` | Marks an assertion that records today's wrong result |
| `# ok` | Marks a line that must produce no diagnostic |
| literate style | Prose and code blocks interleaved |
| snapshot, diagnostic snapshotting | Recorded full diagnostic output |
| external dependencies, external mdtests | Tests under `mdtest/external/` that install real packages |
| lockfile | The `.lock` file next to an external test |
| `MDTEST_EXTERNAL=1` | Enables the external tests |
| "Regression test for <issue URL>" | How a test cites the bug it guards |
| ecosystem report, conformance report, memory report | The bot reports on a ruff pull request |
| property tests | Randomized tests of type relations |

Test prose is present tense and states the Django runtime fact first, e.g. "Django adds an
integer `id` field when no primary key is declared." TODO wording seen: "Should not be an error,
and the type should be ...", "Reject the unknown keyword ...", "Should be an missing-attribute
error."

## 8. Pull request and changelog vocabulary

| Term | Meaning |
|---|---|
| `[ty]` | Required title prefix for ruff pull requests; stripped in the changelog |
| `[ty] Django: ...` | Title form of the recent Django pull requests. Changelog shows "Django: support ..." and also unprefixed "Infer the types of Django model ..." |
| `Pydantic: ...` | Same pattern for Pydantic, with a capitalised verb after the colon |
| Summary, Test Plan | Sections of a ruff pull request |
| Summary, Notes to reviewers | Sections of a ty pull request |
| "Towards astral-sh/ty#1018", "Fixes astral-sh/ty#NNNN" | Issue references |
| "New Markdown tests" | Usual test-plan wording |
| labels | `ty`, `bug`, `server`, `cli`, `diagnostics`, `configuration`, `memory`, `breaking`, `preview`; ignored in the changelog: `internal`, `testing`, `ci`, `playground`, `documentation`, `release` |
| issue labels | `django`, `library`, `help wanted`, `needs-decision`, `needs-design`, `wish` |
| changelog sections | Breaking changes, Preview features, Bug fixes, LSP server, CLI, Diagnostic improvements, Configuration changes, Memory usage improvements |

## 9. Words to avoid, and what to say

| Do not write | Write | Why |
|---|---|---|
| plugin, hook, extension point | built-in support, dedicated support | ty has no plugin system and says so |
| auto id, implicit id, default pk | automatic `id`, automatic primary key | Existing term |
| generated attribute (in Rust) | synthesized member | Source and changelog say "synthesize" |
| synthesized (in user docs) | "attributes and methods that Django generates", "Recognition of" | The docs page never says "synthesized" |
| backward relation, back-reference | reverse accessor (tests), reverse relationship attributes (docs) | Existing terms |
| lazy reference, forward reference | string reference | Docs term; "forward" already means forward foreign key |
| FK, O2O, M2M, PK | foreign key, one-to-one field, many-to-many field, primary key | Docs and tests spell them out; `pk` only as the attribute name |
| `get_FOO_display` | `get_<field>_display()` | Placeholder convention |
| output type, read type | value type | Existing term in tests and source |
| set type, write type | input type | Existing term in tests |
| optional field | nullable field | "Optional" means something else in Pydantic docs |
| inherited fields helper named `all_*` | `own_*` plus an MRO walk | Existing structure in `django.rs` |
| `unresolved-attribute`, `invalid-override` | `missing-attribute`, `incompatible-attribute-override` | Current rule names |
| Ty, TY | ty | Always lowercase |
| "`pk` has the type of", "takes its type from" | "the type of `pk` follows ..." | The docs verb is "follows" |
| relationship field | foreign key or one-to-one field (docs), relation field (Rust) | "relationship field" is used nowhere |
| base model | parent model, abstract base | Tests say "parent"; `BaseModel` is a Pydantic class |
| concrete models that inherit from it | concrete subclasses | Existing term in tests |
| redefine `Meta`, subclass `Meta` | override or inherit from a parent's `Meta`; `Meta` configuration | Changelog and test wording |
| "Support for ..." on the Django page | "Recognition of ...", "Inference of ..." | The Django page's own openers |

The last six rows come from our first docs change (backlog item 5), where the first draft used the
left-hand wording and had to be corrected.

## 10. Gaps in this glossary

- Terms for many-to-many fields, managers and querysets do not appear in ty's docs or source
  yet, apart from `QuerySet[Book]` in two test TODOs. Take them from Django's own documentation
  when needed.
- "related model" and "target model" are both in use for the same thing. Tests and source prefer
  "related model".
- Draft ruff#29731 introduces `foreign_key_model_type`; it is not on main, so it is not listed.
- The docs page and tests currently name `django-types`. This will change with the django-stubs
  switch.
