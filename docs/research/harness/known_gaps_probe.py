from typing import reveal_type

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Length
from django.http import HttpRequest


class Author(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "x"


class Tag(models.Model):
    class Meta:
        app_label = "x"


class Status(models.TextChoices):
    DRAFT = "D", "Draft"
    PUBLISHED = "P", "Published"


class BookQuerySet(models.QuerySet["Book"]):
    def published(self) -> "BookQuerySet":
        return self.filter(pages=1)


class Book(models.Model):
    title = models.CharField(max_length=200)
    pages = models.IntegerField()
    released = models.DateField()
    reviewed = models.DateField(null=True)
    status = models.CharField(max_length=1, choices=Status, default=Status.DRAFT)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    editor = models.ForeignKey(Author, null=True, on_delete=models.SET_NULL, related_name="+")
    by_name = models.ForeignKey(Author, to_field="name", on_delete=models.CASCADE, related_name="+")
    str_author = models.ForeignKey("Author", on_delete=models.CASCADE, related_name="+")
    str_editor = models.ForeignKey("Author", null=True, on_delete=models.SET_NULL, related_name="+")
    app_author = models.ForeignKey("x.Author", on_delete=models.CASCADE, related_name="+")
    sequel = models.ForeignKey("self", null=True, on_delete=models.SET_NULL, related_name="+")
    tags = models.ManyToManyField(Tag)
    views = models.IntegerField(name="view_count")

    objects = BookQuerySet.as_manager()
    reviewed_books = models.Manager.from_queryset(BookQuerySet)()

    class Meta:
        app_label = "x"


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        app_label = "x"


class Profile(models.Model):
    author = models.OneToOneField(Author, on_delete=models.CASCADE)

    class Meta:
        app_label = "x"


class Passport(models.Model):
    author = models.OneToOneField(Author, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        app_label = "x"


class Publication(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="%(class)ss")

    class Meta:
        abstract = True
        app_label = "x"


class Magazine(Publication):
    class Meta:
        app_label = "x"


class Ebook(Book):
    class Meta:
        app_label = "x"


class TrackedForeignKey(models.ForeignKey):
    pass


class Chapter(models.Model):
    book = TrackedForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        app_label = "x"


User = get_user_model()


def probes(
    book: Book, author: Author, review: Review, profile: Profile, passport: Passport,
    publication: Publication, ebook: Ebook, chapter: Chapter, request: HttpRequest,
) -> None:
    reveal_type(book.title)  # P01 plain field
    reveal_type(book.reviewed)  # P02 nullable field
    book.title = 3  # P03 wrong type to CharField
    book.pages = "abc"  # P04 wrong type to IntegerField
    book.released = "1980-10-12"  # P05 ISO date string
    book.id = "1"  # P06 string to automatic id
    book.pk = None  # P07 reset pk
    reveal_type(book.author)  # P08 FK by class
    reveal_type(book.editor)  # P09 nullable FK
    book.author = None  # P10 None to non-null FK
    reveal_type(book.author_id)  # P11 fk id
    reveal_type(book.editor_id)  # P12 nullable fk id
    reveal_type(book.by_name_id)  # P13 fk id with to_field
    reveal_type(book.str_author)  # P14 string reference
    reveal_type(book.str_editor)  # P15 nullable string reference
    reveal_type(book.str_author_id)  # P16 string reference id
    reveal_type(book.app_author)  # P17 app-label string reference
    reveal_type(book.sequel)  # P18 self reference
    reveal_type(profile.author)  # P19 one-to-one
    reveal_type(profile.author_id)  # P20 one-to-one id
    reveal_type(passport.pk)  # P21 pk via one-to-one
    reveal_type(chapter.book)  # P22 plain ForeignKey subclass
    reveal_type(author.books)  # P23 reverse accessor related_name
    reveal_type(book.review_set)  # P24 reverse accessor default
    reveal_type(author.profile)  # P25 reverse one-to-one
    reveal_type(author.magazines)  # P26 related_name with %(class)s
    reveal_type(book.ebook)  # P27 multi-table child accessor
    reveal_type(ebook.book_ptr)  # P28 parent link
    reveal_type(ebook.book_ptr_id)  # P29 parent link id
    reveal_type(book.tags)  # P30 many-to-many manager
    reveal_type(Book.tags.through)  # P31 many-to-many through
    reveal_type(book.view_count)  # P32 renamed field new name
    reveal_type(book.views)  # P33 renamed field old name
    reveal_type(book.get_status_display())  # P34 display method
    book.get_next_by_released()  # P35 date navigation
    book.get_next_by_reviewed()  # P36 date navigation on nullable field
    reveal_type(publication.pk)  # P37 pk on abstract-typed value
    publication.id  # P38 id on abstract-typed value
    reveal_type(Book.objects)  # P39 as_manager manager
    reveal_type(Book.objects.published())  # P40 queryset method via as_manager
    reveal_type(Book.reviewed_books.published())  # P41 queryset method via from_queryset
    reveal_type(Book.objects.all().published())  # P42 queryset method after all()
    reveal_type(Author.objects.all())  # P43 default manager all()
    reveal_type(Author.objects.first())  # P44 first()
    reveal_type(Book.objects.values("title").get())  # P45 values row
    reveal_type(Book.objects.values_list("title", "pages").get())  # P46 values_list row
    reveal_type(Book.objects.values_list("title", flat=True).get())  # P47 values_list flat
    reveal_type(Book.objects.annotate(n=Length("title")).get().n)  # P48 annotate attribute
    Book.objects.filter(titel="x")  # P49 unknown lookup
    Book(titel="x")  # P50 unknown constructor keyword
    Book(title=3)  # P51 wrong constructor value type
    reveal_type(Book.DoesNotExist)  # P52 per-model exception
    Author.nonexistent  # P53 missing class attribute
    author.objects  # P54 manager on instance
    reveal_type(User.objects.create_user("alice"))  # P55 user manager
    reveal_type(request.user)  # P56 request.user
    request.user.is_superuser  # P57 request.user attribute
    reveal_type(settings.DEBUG)  # P58 settings
    settings.NOT_A_SETTING  # P59 unknown setting
    reveal_type(Status.choices)  # P60 choices
    reveal_type(Status.DRAFT.label)  # P61 choice label


def user_annotation(user: User) -> None:  # P62 get_user_model() as a type
    reveal_type(user)  # P63 value typed with get_user_model()
