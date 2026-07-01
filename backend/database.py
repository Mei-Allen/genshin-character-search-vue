"""数据库连接配置 - MySQL 版本

连接方式：通过本地 Unix Socket（比 TCP 更快、更安全）
切换远程 MySQL：改 host/password/db 即可
"""
import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',              # Homebrew 安装的 MySQL 默认无密码
    'db': 'genshin',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor,   # 查询结果返回 dict 而非 tuple
    'unix_socket': '/tmp/mysql.sock',  # 本地 socket 连接
}


def get_db_connection():
    """获取 MySQL 数据库连接"""
    return pymysql.connect(**DB_CONFIG)
