import sqlite3

import pandas as pd

from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, event
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    PickleType,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    Index,
    ForeignKeyConstraint,
    CheckConstraint,
    Enum,
    Numeric,
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, relationship

# import os
# import sys
# sys.path.append( os.path.dirname(os.path.abspath(__file__)) )
from .secrets import db_url

Base = declarative_base()


class Color(Base):
    """stores pairs like ('Black', '#000000').  The `code` field is
    unconstrained, so for instance HTML color names like 'LightCoral'
    could be stored there if they will be usable in that form.
    """

    __tablename__ = 'colors'
    name = Column(String, primary_key=True)
    code = Column(String, unique=True)


class Grade(Base):
    """abstract base for different types of grades (e.g. boulders or
    routes).  `order` is a numeric value for sorting the grades."""

    __abstract__ = True
    grade = Column(String, primary_key=True)
    order = Column(Float, unique=True, nullable=False)


class BoulderGrade(Grade):
    __tablename__ = 'valid_boulder_grades'


class RopeGrade(Grade):
    __tablename__ = 'valid_rope_grades'


# TODO: handle comps/leagues etc. where grade will be in points


class User(Base):
    """Only setters will need logins."""

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    # TODO: email, password, etc.


class Climb(Base):
    """abstract base for different types of climbs (e.g. boulders or
    routes).  `name` will typically just be a letter, like 'A'."""

    __abstract__ = True
    name = Column(String, primary_key=True)

    @declared_attr
    def color(cls):
        return Column(String, ForeignKey('colors.name'))

    @declared_attr
    def setter(cls):
        return Column(Integer, ForeignKey('users.id'), nullable=True)

    date_set = Column(Date, nullable=True)


class Problem(Climb):
    __tablename__ = 'boulder_problems'
    suggested_grade = Column(
        String, ForeignKey('valid_boulder_grades.grade'), nullable=True
    )


class Route(Climb):
    __tablename__ = 'rope_routes'
    suggested_grade = Column(
        String, ForeignKey('valid_rope_grades.grade'), nullable=True
    )


class Vote(Base):
    """`voter` will be some 'unique' string for each visitor/voter, probably a
    cookie or hash from browser+ip, etc."""

    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime)
    voter = Column(String)
    # TODO: PK / UC etc.  each user gets 1 vote per climb


class BoulderVote(Vote):
    __tablename__ = 'boulder_votes'
    climb = Column(String, ForeignKey('boulder_problems.name'), nullable=False)
    grade = Column(String, ForeignKey('valid_boulder_grades.grade'), nullable=False)


class RopeVote(Vote):
    __tablename__ = 'rope_votes'
    climb = Column(String, ForeignKey('rope_routes.name'), nullable=False)
    grade = Column(String, ForeignKey('valid_rope_grades.grade'), nullable=False)


# TODO?: relationships
# TODO?: ondelete="CASCADE" for some ForeignKeys


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection) is sqlite3.Connection:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=on")
        # TODO?: synchronous=0
        cursor.close()


def get_engine():
    engine = create_engine(db_url)
    return engine


def get_session(engine=None):
    if not engine:
        engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


# TODO: contextmanager?


def create_tables(drop_first=False):
    # This will probably be handled by alembic.
    if drop_first:
        raise NotImplementedError
    engine = get_engine()
    Base.metadata.create_all(engine)


def populate_tables(drop_first=False):
    populate_table_from_csv('colors.csv', 'colors')
    populate_table_from_csv('boulder_grades.csv', 'valid_boulder_grades')
    populate_table_from_csv('rope_grades.csv', 'valid_rope_grades')


def populate_table_from_csv(csvfile, tablename, engine=None):
    """reads csv file into existing db table."""
    if engine is None:
        engine = get_engine()
    df = pd.read_csv(csvfile)
    num_rows = df.to_sql(
        name=tablename,
        con=engine,
        if_exists='append',  # 'replace' will drop schema!
        index=False,
    )
