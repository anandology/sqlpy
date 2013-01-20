"""Database and session abstractions.

(part of sqlpy)
"""

from __future__ import absolute_import
from .engines import sqlite

__all__ = [
	"Database", "Session",
    "database"
]

class Database:
    def __init__(self, engine):
        self.engine = engine

    def query(self, sql_query, vars=None):
        with self.session() as s:   
            return s.query(sql_query,vars)

    def session(self):
    	return Session(self.engine)

class Session:
    def __init__(self, engine):
        self.engine = engine
        self.conn = engine.connect()

    def query(self, sql_query,vars):
        return self.engine.query(self.conn, sql_query,vars)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # commit when there is no error 
        # and rollback when there is an error.
        if value is None:
            self.commit()
        else:
            self.rollback()

    def commit(self):
        print "commit"
        self.conn.commit()

    def rollback(self):
        print "rollback"
        self.conn.rollback()


engines = {
	"sqlite": sqlite.SqliteEngine
}

def database(engine, **params):
	e = engines[engine](**params)
	return Database(e)
