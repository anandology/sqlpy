"""Base database engine.

(part of sqlpy)
"""
from __future__ import absolute_import
from ..utils import ResultSet
from ..sql import reparam

class BaseEngine:
    driver = None
    paramstyle = 'pyformat'

    def __init__(self, **params):
        self.params = params

        if self.driver is None:
            raise Exception("driver not defined for %s" % self.__class__.__name__)

        self._module = self.load_module(self.driver)

    def load_module(self, driver):
        return __import__(driver)

    def connect(self):
        return self._module.connect(**self.params)

    def query(self, conn, sql_query,vars):
        cursor = conn.cursor()
        if vars is not None:
            sql_query = reparam(sql_query,vars)
            sql_query, params = self._process_query(sql_query)
        else:
            params = []
        print sql_query, params
        cursor.execute(sql_query, params)

        if cursor.description: 
            # for SELECT query, return a Result object
            return ResultSet(cursor)
        else: 
            # for other queries, return the number of rows modified
            return cursor.rowcount

    def _process_query(self, sql_query):
        """Takes the SQLQuery object and returns query string and parameters.
        """
        query = sql_query.query(self.paramstyle)
        params = sql_query.values()
        return query, params            
