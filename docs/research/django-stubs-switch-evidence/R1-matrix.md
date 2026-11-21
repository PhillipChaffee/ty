## probe.py
| line | probe | A | B | C | rel differs |
|---|---|---|---|---|---|
| 84 | `annotated: models.CharField[str] = models.CharField(max_length=10)` | (no diag) | error[invalid-type-arguments] | (no diag) |  |
| 125 | `book.title  # P01 CharField` | `str` | `Unknown` | `str` |  |
| 126 | `book.subtitle  # P02 CharField null=True` | `str \| None` | `Unknown` | `str \| None` |  |
| 127 | `book.pages  # P03 IntegerField` | `int` | `Unknown` | `int` |  |
| 128 | `book.pages_n  # P04 IntegerField null=True` | `int \| None` | `Unknown` | `int \| None` |  |
| 129 | `book.published  # P05 DateField` | `date` | `Unknown` | `date` |  |
| 130 | `book.published_n  # P06 DateField null=True` | `date \| None` | `Unknown` | `date \| None` |  |
| 131 | `book.updated  # P07 DateTimeField` | `datetime` | `Unknown` | `datetime` |  |
| 132 | `book.updated_n  # P08 DateTimeField null=True` | `datetime \| None` | `Unknown` | `datetime \| None` |  |
| 133 | `book.price  # P09 DecimalField` | `Decimal` | `Unknown` | `Decimal` |  |
| 134 | `book.price_n  # P10 DecimalField null=True` | `Decimal \| None` | `Unknown` | `Decimal \| None` |  |
| 135 | `book.in_print  # P11 BooleanField` | `bool` | `Unknown` | `bool` |  |
| 136 | `book.in_print_n  # P12 BooleanField null=True` | `bool \| None` | `Unknown` | `bool \| None` |  |
| 137 | `book.title = 3  # P13 wrong-type assignment` | error[invalid-assignment] | (no diag) | (no diag) |  |
| 138 | `book.published = "2020-01-01"  # P14 ISO string to DateField` | error[invalid-assignment] | (no diag) | (no diag) |  |
| 139 | `book.published = datetime.date(2020, 1, 1)  # P15 date to DateField` | (no diag) | (no diag) | (no diag) |  |
| 140 | `book.subtitle = None  # P16 None to nullable CharField` | (no diag) | (no diag) | (no diag) |  |
| 141 | `book.title = None  # P17 None to non-null CharField` | error[invalid-assignment] | (no diag) | error[invalid-assignment] |  |
| 143 | `book.id  # P18 automatic id` | `int` | `Unknown` | `int` |  |
| 144 | `book.pk  # P19 pk` | `int` | `Unknown` | `int` |  |
| 145 | `country.code  # P20 custom pk field` | `str` | `Unknown` | `str` |  |
| 146 | `country.pk  # P21 pk with custom CharField pk` | `str` | `Unknown` | `str` |  |
| 147 | `country.id  # P22 id on model with custom pk` | error[missing-attribute] | error[missing-attribute] | error[missing-attribute] |  |
| 149 | `book.author  # P23 FK by class` | `Author` | `Unknown` | `Any` |  |
| 150 | `book.author_id  # P24 FK _id` | `int` | `Any` | `Any` |  |
| 151 | `book.editor  # P25 FK null=True` | `Author \| None` | `Unknown` | `Any` |  |
| 152 | `book.editor_id  # P26 FK null=True _id` | `int \| None` | `Any \| None` | `Any \| None` |  |
| 153 | `book.author_by_slug  # P27 FK to_field` | `Author` | `Unknown` | `Any` |  |
| 154 | `book.author_by_slug_id  # P28 FK to_field _id` | `str` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 155 | `book.author_str  # P29 FK by string` | `Unknown` | `Unknown` | `Any` |  |
| 156 | `book.author_str_id  # P30 FK by string _id` | `Unknown` | `Any` | `Any` |  |
| 157 | `book.sequel_of  # P31 FK "self" null=True` | `Unknown \| None` | `Unknown` | `Any` |  |
| 158 | `book.sequel_of_id  # P32 FK "self" _id` | `Unknown \| None` | `Any \| None` | `Any \| None` |  |
| 159 | `book.country  # P33 FK to custom-pk model` | `Country` | `Unknown` | `Any` |  |
| 160 | `book.country_id  # P34 FK to custom-pk model _id` | `str` | `Any` | `Any` |  |
| 161 | `book.author.name  # P35 attribute through FK` | `str` | `Unknown` | `Any` |  |
| 163 | `profile.author  # P36 O2O` | `Author` | `Unknown` | `Any` |  |
| 164 | `profile.author_id  # P37 O2O _id` | `int` | `Any` | `Any` |  |
| 165 | `profile.backup  # P38 O2O null=True` | `Author \| None` | `Unknown` | `Any` |  |
| 166 | `passport.author  # P39 O2O primary key` | `Author` | `Unknown` | `Any` |  |
| 167 | `passport.pk  # P40 pk with O2O primary key` | `int` | `Any` | `Any` |  |
| 168 | `passport.author_id  # P41 O2O pk _id` | `int` | `Any` | `Any` |  |
| 169 | `passport.id  # P42 id on model with O2O pk` | error[missing-attribute] | error[missing-attribute] | error[missing-attribute] |  |
| 171 | `book.tags  # P43 M2M` | `ManyToManyRelatedManager[Tag, Unknown]` | `ManyRelatedManager[Tag, Any]` | `ManyRelatedManager[Tag, Any]` |  |
| 172 | `book.tags.all())  # P44 M2M .all(` | `ManyToManyRelatedManager[Tag, Unknown]` | `QuerySet[Tag, Tag]` | `QuerySet[Tag, Tag]` |  |
| 173 | `book.tags.through  # P45 M2M .through` | `Unknown` | `Any` | `Any` |  |
| 174 | `Book.tags.through  # P46 M2M class-level .through` | `Unknown` | `type[Any]` | `type[Any]` |  |
| 176 | `book.get_genre_display()  # P47 get_FOO_display` | `str` | `str` | `str` |  |
| 177 | `book.get_next_by_published()  # P48 get_next_by_FOO` | `Book` | `Book` | `Book` |  |
| 178 | `book.get_previous_by_updated()  # P49 get_previous_by_FOO` | `Book` | `Book` | `Book` |  |
| 179 | `book.get_title_display()  # P50 get_FOO_display without choices` | error[missing-attribute] | error[missing-attribute] | error[missing-attribute] |  |
| 181 | `ts.id  # P51 id on abstract` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 182 | `author.id  # P52 id on concrete child of abstract` | `int` | `Unknown` | `int` |  |
| 183 | `author.created  # P53 inherited field` | `datetime` | `Unknown` | `datetime` |  |
| 184 | `Author.Meta.ordering  # P54 Meta overriding parent Meta` | `list[str]` | `list[str]` | `list[str]` |  |
| 185 | `ebook.book_ptr  # P55 MTI parent link` | `Book` | `Book` | `Book` | A: error[missing-attribute] + `Unknown`; B: error[missing-attribute] + `Unknown`; C: error[missing-attribute] + `Unknown` |
| 186 | `ebook.book_ptr_id  # P56 MTI parent link _id` | `int` | `Unknown` | `int` | A: error[missing-attribute] + `Unknown`; B: error[missing-attribute] + `Unknown`; C: error[missing-attribute] + `Unknown` |
| 187 | `ebook.pk  # P57 MTI pk` | `int` | `Unknown` | `int` |  |
| 188 | `ebook.id  # P58 MTI id` | `int` | `Unknown` | `int` |  |
| 189 | `ebook.title  # P59 MTI inherited field` | `str` | `Unknown` | `str` |  |
| 190 | `book.ebook  # P60 MTI reverse` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 192 | `Author.objects  # P61 default manager` | `BaseManager[Author]` | `Manager[Author]` | `Manager[Author, QuerySet[Author, Author]]` |  |
| 193 | `Author.objects.all()  # P62` | `BaseManager[Author]` | `QuerySet[Author, Author]` | `QuerySet[Author, Author]` |  |
| 194 | `Author.objects.filter(name="x")  # P63` | `BaseManager[Author]` | `QuerySet[Author, Author]` | `QuerySet[Author, Author]` |  |
| 195 | `Author.objects.first()  # P64` | `Author \| None` | `Author \| None` | `Author \| None` |  |
| 196 | `Author.objects.get(pk=1)  # P65` | `Author` | `Author` | `Author` |  |
| 197 | `Author.objects.values("name")  # P66` | `ValuesQuerySet[Author, dict[str, Any]]` | `QuerySet[Author, dict[str, Any]]` | `QuerySet[Author, dict[str, Any]]` |  |
| 198 | `Author.objects.values_list("name", flat=True)  # P67` | `ValuesQuerySet[Author, Any]` | `QuerySet[Author, Any]` | `QuerySet[Author, Any]` |  |
| 199 | `Author.objects.values_list("name", "slug")  # P68` | `ValuesQuerySet[Author, Any]` | `QuerySet[Author, Any]` | `QuerySet[Author, Any]` |  |
| 200 | `Author.objects.count()  # P69` | `int` | `int` | `int` |  |
| 201 | `Author.objects.create(name="x")  # P70` | `Author` | `Author` | `Author` |  |
| 202 | `Author.objects.filter(nme="x")  # P71 misspelled lookup` | `BaseManager[Author]` | `QuerySet[Author, Author]` | `QuerySet[Author, Author]` |  |
| 203 | `author.objects  # P72 objects on instance` | `BaseManager[Author]` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 204 | `Book.objects  # P73 custom manager` | `BaseManager[Book]` | `BookManager` | `BookManager` |  |
| 205 | `Book.objects.bestsellers()  # P74 unannotated custom method` | `Unknown` | `Unknown` | `Unknown` |  |
| 206 | `Book.objects.n_bestsellers()  # P75 annotated custom method` | `Unknown` | `int` | `int` |  |
| 207 | `Book.objects.all()  # P76` | `BaseManager[Book]` | `QuerySet[Book, Book]` | `QuerySet[Book, Book]` |  |
| 208 | `Book.objects.first()  # P77` | `Book \| None` | `Book \| None` | `Book \| None` |  |
| 209 | `Book.cheap_ones  # P78 as_manager` | `Manager[Book]` | `Manager[Book]` | `Manager[Book, BookQuerySet]` |  |
| 210 | `Book.cheap_ones.cheap()  # P79 as_manager custom method` | `Unknown` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 211 | `Book.cheap_ones.all()  # P80` | `Manager[Book]` | `QuerySet[Book, Book]` | `BookQuerySet` |  |
| 212 | `Book._default_manager  # P81` | `BaseManager[Book]` | `Manager[Book]` | `Manager[Book, QuerySet[Book, Book]]` |  |
| 213 | `EBook.objects  # P82 inherited custom manager` | `BaseManager[EBook]` | `BookManager` | `BookManager` |  |
| 214 | `EBook.objects.first()  # P83` | `EBook \| None` | `Book \| None` | `Book \| None` |  |
| 216 | `a  # P84 iteration` | `Author` | `Author` | `Author` |  |
| 218 | `Book.DoesNotExist  # P85` | `type[ObjectDoesNotExist]` | `type[ObjectDoesNotExist]` | `type[ObjectDoesNotExist]` |  |
| 219 | `Book.MultipleObjectsReturned  # P86` | `type[MultipleObjectsReturned]` | `type[MultipleObjectsReturned]` | `type[MultipleObjectsReturned]` |  |
| 220 | `Book._meta  # P87` | `Options[Book]` | `Options[Book]` | `Options[Book]` |  |
| 221 | `Book._meta.get_field("title")  # P88` | `Field[Any, Any]` | `Field[Any, Any] \| ForeignObjectRel` | `Field[Any, Any] \| ForeignObjectRel` |  |
| 222 | `Book.title  # P89 class-level field access` | `CharField[str]` | `_FieldDescriptor[CharField[Unknown, Unknown]]` | `_FieldDescriptor[CharField[str \| int, str]]` |  |
| 223 | `Book.author  # P90 class-level FK access` | `ForwardManyToOneDescriptor` | `ForwardManyToOneDescriptor[ForeignKey[Unknown, Unknown]]` | `ForwardManyToOneDescriptor[ForeignKey[Any, Any]]` |  |
| 225 | `Genre.choices  # P91` | `Sequence[tuple[Genre, str]]` | `list[tuple[str, str \| _StrPromise]]` | `list[tuple[str, str \| _StrPromise]]` |  |
| 226 | `Genre.FICTION.label  # P92` | `str` | `str \| _StrPromise` | `str \| _StrPromise` |  |
| 227 | `Genre.values  # P93` | `Sequence[Genre]` | `list[str]` | `list[str]` |  |
| 228 | `Genre.labels  # P94` | `list[str]` | `list[str \| _StrPromise]` | `list[str \| _StrPromise]` |  |
| 229 | `Genre.FICTION.value  # P95` | `str` | `str` | `str` |  |
| 230 | `Genre.FICTION  # P96` | `Literal[Genre.FICTION]` | `Literal[Genre.FICTION]` | `Literal[Genre.FICTION]` |  |
| 233 | `User  # P97` | `type[AbstractUser]` | `type[AbstractBaseUser]` | `type[AbstractBaseUser]` |  |
| 235 | `user  # P98` | `AbstractUser` | `AbstractBaseUser` | `AbstractBaseUser` |  |
| 236 | `user.username  # P99` | `str` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 237 | `User.objects  # P100` | `UserManager[AbstractUser]` | `Manager[AbstractBaseUser]` | `Manager[AbstractBaseUser, QuerySet[AbstractBaseUser, AbstractBaseUser]]` |  |
| 238 | `HttpRequest().user  # P101` | `AbstractUser \| AnonymousUser` | `AbstractBaseUser \| AnonymousUser` | `AbstractBaseUser \| AnonymousUser` |  |
| 239 | `settings.DEBUG  # P102` | `Any` | `Any` | `Any` |  |
| 240 | `settings.NOT_A_SETTING  # P103` | `Any` | `Any` | `Any` |  |
| 242 | `Book(title="x")  # P104 constructor` | `Book` | `Book` | `Book` |  |
| 243 | `Book(titel="x")  # P105 misspelled keyword` | (no diag) | (no diag) | (no diag) |  |
| 244 | `Book(title=3)  # P106 wrong-typed keyword` | (no diag) | (no diag) | (no diag) |  |
| 245 | `book.annotated  # P107 user-annotated field` | `str` | `Unknown` | `str` |  |
| 247 | `author.book_set  # P108 implicit reverse FK` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 248 | `author.edited  # P109 related_name reverse FK` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 249 | `author.profile  # P110 reverse O2O` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 250 | `book.save()  # P111` | `None` | `None` | `None` |  |
| 251 | `book.refresh_from_db()  # P112` | `None` | `None` | `None` |  |
| 252 | `Author.objects.filter(name="x").order_by("name").exists()  # P113` | `bool` | `bool` | `bool` |  |
| 253 | `Author.objects.aggregate(n=models.Count("id"))  # P114` | `dict[str, Any]` | `dict[str, Any]` | `dict[str, Any]` |  |
| 254 | `Author.objects.annotate(n=models.Count("book"))  # P115` | `BaseManager[Author]` | `QuerySet[Author, Author]` | `QuerySet[Author, Author]` |  |
| 255 | `Author.objects.get_or_create(name="x")  # P116` | `tuple[Author, bool]` | `tuple[Author, bool]` | `tuple[Author, bool]` |  |
| 256 | `Author.objects.select_related("x").prefetch_related("y").last()  # P117` | `Author \| None` | `Author \| None` | `Author \| None` |  |
| 257 | `Author.objects.in_bulk([1])  # P118` | `dict[Any, Author]` | `dict[Any, Author]` | `dict[Any, Author]` |  |
| 258 | `Author.objects.none()  # P119` | `BaseManager[Author]` | `QuerySet[Author, Author]` | `QuerySet[Author, Author]` |  |
| 259 | `Author.objects.values_list("name")  # P120` | `ValuesQuerySet[Author, Any]` | `QuerySet[Author, Any]` | `QuerySet[Author, Any]` |  |
## rm_a.py
| line | probe | A | B | C | rel differs |
|---|---|---|---|---|---|
| 8 | `from django.db.models.manager import RelatedManager` | (no diag) | error[missing-module-member] | error[missing-module-member] |  |
| 27 | `w.novels  # R1` | `RelatedManager[Novel]` | `Unknown` | `Unknown` |  |
| 28 | `w.novels.all()  # R2` | `RelatedManager[Novel]` | `Unknown` | `Unknown` |  |
| 29 | `w.novels.first()  # R3` | `Novel \| None` | `Unknown` | `Unknown` |  |
| 30 | `w.novels.create()  # R4` | `Novel` | `Unknown` | `Unknown` |  |
## rm_b.py
| line | probe | A | B | C | rel differs |
|---|---|---|---|---|---|
| 8 | `from django.db.models.fields.related_descriptors import RelatedManager` | error[missing-module-member] | (no diag) | (no diag) |  |
| 27 | `w.novels  # R1` | `Unknown` | `RelatedManager[Novel]` | `RelatedManager[Novel, QuerySet[Novel, Novel]]` |  |
| 28 | `w.novels.all()  # R2` | `Unknown` | `QuerySet[Novel, Novel]` | `QuerySet[Novel, Novel]` |  |
| 29 | `w.novels.first()  # R3` | `Unknown` | `Novel \| None` | `Novel \| None` |  |
| 30 | `w.novels.create()  # R4` | `Unknown` | `Novel` | `Novel` |  |
## rm_c.py
| line | probe | A | B | C | rel differs |
|---|---|---|---|---|---|
| 8 | `from django_stubs_ext.db.models.manager import RelatedManager` | error[import-not-found] | (no diag) | (no diag) |  |
| 27 | `w.novels  # R1` | `Unknown` | `RelatedManager[Novel]` | `RelatedManager[Novel, QuerySet[Novel, Novel]]` |  |
| 28 | `w.novels.all()  # R2` | `Unknown` | `QuerySet[Novel, Novel]` | `QuerySet[Novel, Novel]` |  |
| 29 | `w.novels.first()  # R3` | `Unknown` | `Novel \| None` | `Novel \| None` |  |
| 30 | `w.novels.create()  # R4` | `Unknown` | `Novel` | `Novel` |  |
## extra.py
| line | probe | A | B | C | rel differs |
|---|---|---|---|---|---|
| 29 | `fk2: models.ForeignKey[Author, Author] = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="+")  # E00a` | error[invalid-type-arguments] | (no diag) | (no diag) |  |
| 30 | `fk2n: models.ForeignKey[Author | None, Author | None] = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, related_name="+")  # E00b` | error[invalid-type-arguments] | (no diag) | (no diag) |  |
| 31 | `fk1: models.ForeignKey[Author] = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="+")  # E00c` | (no diag) | (no diag) | (no diag) |  |
| 33 | `fk_slug2: models.ForeignKey[Author, Author] = models.ForeignKey(Author, on_delete=models.CASCADE, to_field="slug", related_name="+")` | error[invalid-type-arguments] | (no diag) | (no diag) |  |
| 49 | `book.fk2  # E01 FK annotated two-param` | `Unknown` | `Author` | `Author` |  |
| 50 | `book.fk2_id  # E02` | `Unknown` | `Any` | `Any` |  |
| 51 | `book.fk2n  # E03 FK annotated two-param nullable` | `Unknown` | `Author \| None` | `Author \| None` |  |
| 52 | `book.fk2n_id  # E04` | `Unknown \| None` | `Any \| None` | `Any \| None` |  |
| 53 | `book.fk1  # E05 FK annotated one-param` | `Author` | `Author` | `Author` |  |
| 54 | `book.fk1_id  # E06` | `int` | `Any` | `Any` |  |
| 55 | `book.fk_app  # E07 FK "app.Model"` | `Unknown` | `Unknown` | `Any` |  |
| 56 | `book.fk_slug2  # E08` | `Unknown` | `Author` | `Author` |  |
| 57 | `book.fk_slug2_id  # E09 annotated FK with to_field` | `Unknown` | error[missing-attribute] + `Unknown` | error[missing-attribute] + `Unknown` |  |
| 58 | `book.m2m_t  # E10 M2M with through` | `ManyToManyRelatedManager[Author, Unknown]` | `ManyRelatedManager[Author, Any]` | `ManyRelatedManager[Author, Any]` |  |
| 59 | `book.m2m_t.through  # E11` | `Unknown` | `Any` | `Any` |  |
| 60 | `author.age  # E12 null=False explicit` | `int` | `Unknown` | `int` |  |
| 61 | `author.nick  # E13 null=True, blank=True` | `str \| None` | `Unknown` | `str \| None` |  |
| 62 | `author.bio  # E14 TextField` | `str` | `Unknown` | `str` |  |
| 63 | `author.flag  # E15 CharField null=False explicit` | `str` | `Unknown` | `str` |  |
| 64 | `author.uid  # E16 UUIDField null=True` | `UUID \| None` | `Unknown` | `UUID \| None` |  |
| 65 | `author.data  # E17 JSONField null=True` | `Unknown \| None` | `Any` | `Any` |  |
| 66 | `author.email  # E18 EmailField` | `str` | `Unknown` | `str` |  |
| 67 | `author.score  # E19 FloatField null=True` | `float \| None` | `Unknown` | `float \| None` |  |
| 68 | `book.title = b"bytes"  # E20` | error[invalid-assignment] | (no diag) | error[invalid-assignment] |  |
| 69 | `book.pages = "abc"  # E21` | error[invalid-assignment] | (no diag) | (no diag) |  |
| 70 | `book.pages = 1.5  # E22` | error[invalid-assignment] | (no diag) | (no diag) |  |
| 71 | `book.published = 3  # E23` | error[invalid-assignment] | (no diag) | error[invalid-assignment] |  |
| 72 | `book.title = object()  # E24` | error[invalid-assignment] | (no diag) | error[invalid-assignment] |  |
| 73 | `book.fk2 = book  # E25 wrong model to annotated FK` | (no diag) | error[invalid-assignment] | error[invalid-assignment] |  |
| 74 | `book.fk_app = 3  # E26 int to unannotated FK` | (no diag) | (no diag) | (no diag) |  |
| 75 | `Author.nonexistent)  # E27 unknown class attribute (metaclass __getattr__` | error[missing-attribute] + `Unknown` | error[invalid-attribute-access] + `Manager[Author]` | error[invalid-attribute-access] + `Manager[Author, QuerySet[Author, Author]]` |  |
| 76 | `Author.objects.get(name="x").name  # E28` | `str` | `Unknown` | `str` |  |
| 77 | `Author.pk  # E29` | `AutoField` | `_FieldDescriptor[AutoField[Unknown, Unknown]]` | `_FieldDescriptor[AutoField[int \| str, int]]` |  |
| 78 | `Author.id  # E30` | `AutoField` | `_FieldDescriptor[AutoField[Unknown, Unknown]]` | `_FieldDescriptor[AutoField[int \| str, int]]` |  |
| 79 | `settings  # E31` | `LazySettings` | `LazySettings` | `LazySettings` |  |
| 80 | `Author.objects.values_list("name", flat=True).first()  # E32` | `Any \| None` | `Any \| None` | `Any \| None` |  |
| 81 | `models.CharField(max_length=3)  # E33 field constructor` | `CharField[str]` | `CharField[Unknown, Unknown]` | `CharField[str \| int, str]` |  |
| 82 | `models.CharField(max_length=3, null=True)  # E34 field constructor null=True` | `CharField[str \| None]` | `CharField[Unknown, Unknown]` | `CharField[str \| int \| None, str \| None]` |  |
| 83 | `models.ForeignKey(Author, on_delete=models.CASCADE)  # E35` | `ForeignKey[Author]` | `ForeignKey[Unknown, Unknown]` | `ForeignKey[Any, Any]` |  |
| 84 | `models.ForeignKey(Author, on_delete=models.CASCADE, null=True)  # E36` | `ForeignKey[Author \| None]` | `ForeignKey[Unknown, Unknown]` | `ForeignKey[Any, Any]` |  |
| 85 | `models.ManyToManyField(Author)  # E37` | `ManyToManyField[Author, Unknown]` | `ManyToManyField[Author, Any]` | `ManyToManyField[Author, Any]` |  |
| 86 | `models.OneToOneField(Author, on_delete=models.CASCADE)  # E38` | `OneToOneField[Author]` | `OneToOneField[Unknown, Unknown]` | `OneToOneField[Any, Any]` |  |
