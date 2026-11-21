from __future__ import annotations

import datetime
from typing import reveal_type

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    )
    django.setup()

from django.contrib.auth import get_user_model
from django.db import models
from django.http import HttpRequest


class Genre(models.TextChoices):
    FICTION = "F", "Fiction"
    SCIENCE = "S", "Science"


class Timestamped(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        app_label = "x"
        ordering = ["created"]


class Author(Timestamped):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=50, unique=True)

    class Meta(Timestamped.Meta):
        ordering = ["name"]


class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)

    class Meta:
        app_label = "x"


class Tag(models.Model):
    label = models.CharField(max_length=20)

    class Meta:
        app_label = "x"


class BookQuerySet(models.QuerySet["Book"]):
    def cheap(self):
        return self.filter(price__lt=10)


class BookManager(models.Manager["Book"]):
    def bestsellers(self):
        return self.filter(pages__gt=100)

    def n_bestsellers(self) -> int:
        return self.bestsellers().count()


class Book(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, null=True)
    pages = models.IntegerField()
    pages_n = models.IntegerField(null=True)
    published = models.DateField()
    published_n = models.DateField(null=True)
    updated = models.DateTimeField(auto_now=True)
    updated_n = models.DateTimeField(null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    price_n = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    in_print = models.BooleanField(default=True)
    in_print_n = models.BooleanField(null=True)
    genre = models.CharField(max_length=1, choices=Genre.choices)
    annotated: models.CharField[str] = models.CharField(max_length=10)

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    editor = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name="edited")
    author_by_slug = models.ForeignKey(Author, on_delete=models.CASCADE, to_field="slug", related_name="+")
    author_str = models.ForeignKey("Author", on_delete=models.CASCADE, related_name="+")
    sequel_of = models.ForeignKey("self", on_delete=models.SET_NULL, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    objects = BookManager()
    cheap_ones = BookQuerySet.as_manager()

    class Meta:
        app_label = "x"


class Profile(models.Model):
    author = models.OneToOneField(Author, on_delete=models.CASCADE)
    backup = models.OneToOneField(Author, on_delete=models.SET_NULL, null=True, related_name="+")

    class Meta:
        app_label = "x"


class Passport(models.Model):
    author = models.OneToOneField(Author, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        app_label = "x"


class EBook(Book):
    url = models.CharField(max_length=200)

    class Meta:
        app_label = "x"


def probes(book: Book, author: Author, country: Country, profile: Profile, passport: Passport, ebook: EBook, ts: Timestamped) -> None:
    # scalar fields
    reveal_type(book.title)  # P01 CharField
    reveal_type(book.subtitle)  # P02 CharField null=True
    reveal_type(book.pages)  # P03 IntegerField
    reveal_type(book.pages_n)  # P04 IntegerField null=True
    reveal_type(book.published)  # P05 DateField
    reveal_type(book.published_n)  # P06 DateField null=True
    reveal_type(book.updated)  # P07 DateTimeField
    reveal_type(book.updated_n)  # P08 DateTimeField null=True
    reveal_type(book.price)  # P09 DecimalField
    reveal_type(book.price_n)  # P10 DecimalField null=True
    reveal_type(book.in_print)  # P11 BooleanField
    reveal_type(book.in_print_n)  # P12 BooleanField null=True
    book.title = 3  # P13 wrong-type assignment
    book.published = "2020-01-01"  # P14 ISO string to DateField
    book.published = datetime.date(2020, 1, 1)  # P15 date to DateField
    book.subtitle = None  # P16 None to nullable CharField
    book.title = None  # P17 None to non-null CharField
    # primary keys
    reveal_type(book.id)  # P18 automatic id
    reveal_type(book.pk)  # P19 pk
    reveal_type(country.code)  # P20 custom pk field
    reveal_type(country.pk)  # P21 pk with custom CharField pk
    country.id  # P22 id on model with custom pk
    # foreign keys
    reveal_type(book.author)  # P23 FK by class
    reveal_type(book.author_id)  # P24 FK _id
    reveal_type(book.editor)  # P25 FK null=True
    reveal_type(book.editor_id)  # P26 FK null=True _id
    reveal_type(book.author_by_slug)  # P27 FK to_field
    reveal_type(book.author_by_slug_id)  # P28 FK to_field _id
    reveal_type(book.author_str)  # P29 FK by string
    reveal_type(book.author_str_id)  # P30 FK by string _id
    reveal_type(book.sequel_of)  # P31 FK "self" null=True
    reveal_type(book.sequel_of_id)  # P32 FK "self" _id
    reveal_type(book.country)  # P33 FK to custom-pk model
    reveal_type(book.country_id)  # P34 FK to custom-pk model _id
    reveal_type(book.author.name)  # P35 attribute through FK
    # one-to-one
    reveal_type(profile.author)  # P36 O2O
    reveal_type(profile.author_id)  # P37 O2O _id
    reveal_type(profile.backup)  # P38 O2O null=True
    reveal_type(passport.author)  # P39 O2O primary key
    reveal_type(passport.pk)  # P40 pk with O2O primary key
    reveal_type(passport.author_id)  # P41 O2O pk _id
    passport.id  # P42 id on model with O2O pk
    # many-to-many
    reveal_type(book.tags)  # P43 M2M
    reveal_type(book.tags.all())  # P44 M2M .all()
    reveal_type(book.tags.through)  # P45 M2M .through
    reveal_type(Book.tags.through)  # P46 M2M class-level .through
    # synthesized methods
    reveal_type(book.get_genre_display())  # P47 get_FOO_display
    reveal_type(book.get_next_by_published())  # P48 get_next_by_FOO
    reveal_type(book.get_previous_by_updated())  # P49 get_previous_by_FOO
    book.get_title_display()  # P50 get_FOO_display without choices
    # abstract / inheritance
    reveal_type(ts.id)  # P51 id on abstract
    reveal_type(author.id)  # P52 id on concrete child of abstract
    reveal_type(author.created)  # P53 inherited field
    reveal_type(Author.Meta.ordering)  # P54 Meta overriding parent Meta
    reveal_type(ebook.book_ptr)  # P55 MTI parent link
    reveal_type(ebook.book_ptr_id)  # P56 MTI parent link _id
    reveal_type(ebook.pk)  # P57 MTI pk
    reveal_type(ebook.id)  # P58 MTI id
    reveal_type(ebook.title)  # P59 MTI inherited field
    reveal_type(book.ebook)  # P60 MTI reverse
    # managers / querysets
    reveal_type(Author.objects)  # P61 default manager
    reveal_type(Author.objects.all())  # P62
    reveal_type(Author.objects.filter(name="x"))  # P63
    reveal_type(Author.objects.first())  # P64
    reveal_type(Author.objects.get(pk=1))  # P65
    reveal_type(Author.objects.values("name"))  # P66
    reveal_type(Author.objects.values_list("name", flat=True))  # P67
    reveal_type(Author.objects.values_list("name", "slug"))  # P68
    reveal_type(Author.objects.count())  # P69
    reveal_type(Author.objects.create(name="x"))  # P70
    reveal_type(Author.objects.filter(nme="x"))  # P71 misspelled lookup
    reveal_type(author.objects)  # P72 objects on instance
    reveal_type(Book.objects)  # P73 custom manager
    reveal_type(Book.objects.bestsellers())  # P74 unannotated custom method
    reveal_type(Book.objects.n_bestsellers())  # P75 annotated custom method
    reveal_type(Book.objects.all())  # P76
    reveal_type(Book.objects.first())  # P77
    reveal_type(Book.cheap_ones)  # P78 as_manager
    reveal_type(Book.cheap_ones.cheap())  # P79 as_manager custom method
    reveal_type(Book.cheap_ones.all())  # P80
    reveal_type(Book._default_manager)  # P81
    reveal_type(EBook.objects)  # P82 inherited custom manager
    reveal_type(EBook.objects.first())  # P83
    for a in Author.objects.all():
        reveal_type(a)  # P84 iteration
    # model class attributes
    reveal_type(Book.DoesNotExist)  # P85
    reveal_type(Book.MultipleObjectsReturned)  # P86
    reveal_type(Book._meta)  # P87
    reveal_type(Book._meta.get_field("title"))  # P88
    reveal_type(Book.title)  # P89 class-level field access
    reveal_type(Book.author)  # P90 class-level FK access
    # choices
    reveal_type(Genre.choices)  # P91
    reveal_type(Genre.FICTION.label)  # P92
    reveal_type(Genre.values)  # P93
    reveal_type(Genre.labels)  # P94
    reveal_type(Genre.FICTION.value)  # P95
    reveal_type(Genre.FICTION)  # P96
    # user model, request, settings
    User = get_user_model()
    reveal_type(User)  # P97
    user = User()
    reveal_type(user)  # P98
    reveal_type(user.username)  # P99
    reveal_type(User.objects)  # P100
    reveal_type(HttpRequest().user)  # P101
    reveal_type(settings.DEBUG)  # P102
    reveal_type(settings.NOT_A_SETTING)  # P103
    # constructors
    reveal_type(Book(title="x"))  # P104 constructor
    Book(titel="x")  # P105 misspelled keyword
    Book(title=3)  # P106 wrong-typed keyword
    reveal_type(book.annotated)  # P107 user-annotated field
    # reverse accessors
    reveal_type(author.book_set)  # P108 implicit reverse FK
    reveal_type(author.edited)  # P109 related_name reverse FK
    reveal_type(author.profile)  # P110 reverse O2O
    reveal_type(book.save())  # P111
    reveal_type(book.refresh_from_db())  # P112
    reveal_type(Author.objects.filter(name="x").order_by("name").exists())  # P113
    reveal_type(Author.objects.aggregate(n=models.Count("id")))  # P114
    reveal_type(Author.objects.annotate(n=models.Count("book")))  # P115
    reveal_type(Author.objects.get_or_create(name="x"))  # P116
    reveal_type(Author.objects.select_related("x").prefetch_related("y").last())  # P117
    reveal_type(Author.objects.in_bulk([1]))  # P118
    reveal_type(Author.objects.none())  # P119
    reveal_type(Author.objects.values_list("name"))  # P120
