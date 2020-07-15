
import os.path
import sqlite3

table_name = "pc_accepted_players"
columns = "key text PRIMARY KEY, name text, unix text"


def connect():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "private/test.db")
    with sqlite3.connect(db_path) as db:
        return db


conn = connect()
c = conn.cursor()

columns = "key, name"
_values = ["jorge", "piranha"]

def delete_from_table(table_name, condition):
    c.execute(
        f"""DELETE FROM {table_name}
            {condition}""")



insert_into_table()
create_table()
conn.commit()
conn.close()
