"""Sqlite Engine

(part of sqlpy)
"""

from __future__ import absolute_import
import sqlite3
from .base import BaseEngine

class SqliteEngine(BaseEngine):
	driver = "sqlite3"
	paramstyle = 'qmark'

