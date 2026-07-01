"""一次性脚本：从本地 MySQL 导出数据到 SQLite 文件"""
import pymysql
import sqlite3
import os

mysql_conn = pymysql.connect(
    host='localhost', user='root', password='',
    db='genshin', charset='utf8mb4',
    unix_socket='/tmp/mysql.sock',
    cursorclass=pymysql.cursors.DictCursor
)

sqlite_path = os.path.join(os.path.dirname(__file__), 'genshin.db')
if os.path.exists(sqlite_path):
    os.remove(sqlite_path)

sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_conn.row_factory = sqlite3.Row

with mysql_conn.cursor() as mc:
    mc.execute('SELECT * FROM characters')
    rows = mc.fetchall()
    columns = [d[0] for d in mc.description]

    # 建表
    col_defs = []
    for col in columns:
        if col == 'id':
            col_defs.append('id INTEGER PRIMARY KEY AUTOINCREMENT')
        else:
            col_defs.append(f'"{col}" TEXT')

    create_sql = f'CREATE TABLE characters ({", ".join(col_defs)})'
    sqlite_conn.execute(create_sql)

    # 插入数据
    placeholders = ', '.join(['?'] * len(columns))
    col_names = ', '.join([f'"{c}"' for c in columns])
    insert_sql = f'INSERT INTO characters ({col_names}) VALUES ({placeholders})'

    for row in rows:
        values = [row[col] for col in columns]
        sqlite_conn.execute(insert_sql, values)

    sqlite_conn.commit()

    count = sqlite_conn.execute('SELECT COUNT(*) as cnt FROM characters').fetchone()['cnt']
    print(f'Done: {count} characters → {sqlite_path}')

sqlite_conn.close()
mysql_conn.close()
