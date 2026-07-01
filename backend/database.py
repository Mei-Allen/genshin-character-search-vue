"""数据库连接 - 自动适配本地/生产环境

对外接口兼容 pymysql，内部用 sqlite3，main.py 不需要任何改动。
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'genshin.db')


class FakeCursor:
    """模拟 pymysql DictCursor —— 实际用 sqlite3.Row """

    def __init__(self, conn):
        self._conn = conn
        self._real_cursor = None
        self.rowcount = 0
        self.lastrowid = 0

    def execute(self, sql, params=None):
        # pymysql 的 %s → sqlite3 的 ?
        sql = sql.replace('%s', '?')
        self._real_cursor = self._conn.cursor()
        if params:
            self._real_cursor.execute(sql, params)
        else:
            self._real_cursor.execute(sql)
        self.rowcount = self._real_cursor.rowcount
        self.lastrowid = self._real_cursor.lastrowid
        return self

    def fetchone(self):
        row = self._real_cursor.fetchone()
        if row is None:
            return None
        return {k: row[k] for k in row.keys()}

    def fetchall(self):
        return [{k: row[k] for k in row.keys()} for row in self._real_cursor.fetchall()]

    def __iter__(self):
        return iter(self.fetchall())

    def close(self):
        if self._real_cursor:
            self._real_cursor.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class FakeConnection:
    """模拟 pymysql Connection"""

    def __init__(self, db_path):
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")

    def cursor(self):
        return FakeCursor(self._conn)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db_connection():
    """返回模拟 pymysql 连接的对象"""
    return FakeConnection(DB_PATH)
