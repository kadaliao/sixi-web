import os
import sqlite3

import pytest

from sixi_web import Column, Database, ForeignKey, Table


@pytest.fixture
def db():
    DB_PATH = "./test.db"
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = Database(DB_PATH)
    return db


@pytest.fixture
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)

    return Author


@pytest.fixture
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = ForeignKey(Author)

    return Book


def test_create_db(db):
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []


def test_define_tables(Author, Book):
    assert Author.name.type == str
    assert Book.author.table == Author
    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"


def test_create_tables(db, Author, Book):

    db.create(Author)
    db.create(Book)

    assert Author._get_create_sql() == "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT);"
    assert Book._get_create_sql() == "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"

    for table in ("author", "book"):
        assert table in db.tables


def test_create_author_instance(db, Author):
    db.create(Author)
    zhangsan = Author(name="Zhang San", age=35)
    assert zhangsan.name == "Zhang San"
    assert zhangsan.age == 35
    assert zhangsan.id is None


def test_save_author_instance(db, Author):
    db.create(Author)

    zhangsan = Author(name="Zhang San", age=23)
    db.save(zhangsan)
    assert zhangsan._get_insert_sql() == ("""INSERT INTO author (age, name) VALUES (?, ?);""", [23, "Zhang San"])
    assert zhangsan.id == 1

    lisi = Author(name="Li Si", age=18)
    db.save(lisi)
    assert lisi.id == 2

    wangwu = Author(name="Wang Wu", age=39)
    db.save(wangwu)
    assert wangwu.id == 3


def test_query_all_authors(db, Author):
    db.create(Author)

    lisi = Author(name="lisi", age=23)
    wangwu = Author(name="wangwu", age=25)
    db.save(lisi)
    db.save(wangwu)

    authors = db.all(Author)

    assert Author._get_select_all_sql() == ("SELECT id, age, name FROM author;", ["id", "age", "name"])

    assert len(authors) == 2
    assert type(authors[0]) == Author
    assert {a.age for a in authors} == {23, 25}
    assert {a.name for a in authors} == {"wangwu", "lisi"}


def test_get_author(db, Author):
    db.create(Author)
    lisi = Author(name="lisi", age=43)
    db.save(lisi)

    john_from_db = db.get(Author, id=1)

    assert Author._get_select_where_sql(id=1) == ("SELECT id, age, name FROM author WHERE id = ?;", ["id", "age", "name"], [1])
    assert type(john_from_db) == Author
    assert john_from_db.age == 43
    assert john_from_db.name == "lisi"
    assert john_from_db.id == 1


def test_get_book(db, Author, Book):
    db.create(Author)
    db.create(Book)
    lisi = Author(name="lisi", age=43)
    wangwu = Author(name="wangwu", age=50)
    book1 = Book(title="book1", published=False, author=lisi)
    book2 = Book(title="book2", published=True, author=wangwu)
    db.save(lisi)
    db.save(wangwu)
    db.save(book1)
    db.save(book2)

    book_from_db = db.get(Book, 2)

    assert book_from_db.title == "book2"
    assert book_from_db.author.name == "wangwu"
    assert book_from_db.author.id == 2


def test_query_all_books(db, Author, Book):
    db.create(Author)
    db.create(Book)
    lisi = Author(name="lisi", age=43)
    wangwu = Author(name="wangwu", age=50)
    book1 = Book(title="book1", published=False, author=lisi)
    book2 = Book(title="book2", published=True, author=wangwu)
    db.save(lisi)
    db.save(wangwu)
    db.save(book1)
    db.save(book2)

    books = db.all(Book)

    assert len(books) == 2
    assert books[1].author.name == "wangwu"
