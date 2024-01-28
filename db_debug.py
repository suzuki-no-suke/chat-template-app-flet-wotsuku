import os
import pprint
from dotenv import load_dotenv

from sqlalchemy import inspect, text

from src.orm.base import SQLFactory

load_dotenv()

db = SQLFactory.default_env()

def list_tables():
    inspector = inspect(db.get_engine())

    all_names = []
    for table_name in inspector.get_table_names():
        all_names.append(table_name)
        print(f"Table: {table_name}")
        for column in inspector.get_columns(table_name):
            print(f"- Column: {column['name']}")
    return all_names

def show_table_contents():
    # テーブル一覧を取得
    tables = list_tables()
    table_contents = {}
    for table in tables:
        # テーブルの中身を取得
        with db.get_engine().connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table}"))
            table_contents[table] = [pprint.pformat(row) for row in result]
    return str(table_contents)

if __name__ == '__main__':
    pprint.pprint(show_table_contents())

