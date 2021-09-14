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
