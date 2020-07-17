
import sqlite3
from classes import Utils
# EXEPTIONS


class NoTableError(Exception):
    def __init__(self, table_name):
        self.table_name = table_name


class ElementAlreadyExists(Exception):
    """Exceção em casos de tentativa de criar uma barra que já existe

    """

    def __init__(self, message, name):
        self.message = message
        self.name = name

class ElementNotExists(Exception):
    """Exceção em casos de tentativa de criar uma barra que já existe

    """

    def __init__(self, message, name):
        self.message = message
        self.name = name

class TableController(object):
    def set_db(self, db: str):
        self.db = db

    def connect(self):
        self.conn = sqlite3.connect(self.db)
        self.c = self.conn.cursor()

    def exist_table(self, table_name: str):
        self.c.execute(
            f"""SELECT count(name) FROM sqlite_master
            WHERE type='table' AND name='{table_name}'""")
        if self.c.fetchone()[0] == 1:
            return True
        return False

    def create_table(self, table_name: str, columns: str):
        self.c.execute(
            f"""CREATE TABLE IF NOT EXISTS {table_name}
            (
                {columns}
            )
            """
        )
        self.conn.commit()

    def drop_table(self, table_name: str):
        if self.exist_table(table_name):
            self.c.execute(
                f"""DROP TABLE {table_name}
                """)
            return True
        raise NoTableError(table_name)

    def insert_into_table(self, table_name: str, columns: str, values: list):
        v = []
        for value in values:
            v.append(f"'{value}'")
        s_values = ", ".join(v)
        self.c.execute(
            f"""INSERT OR REPLACE INTO {table_name}
                    ({columns})
                VALUES
                    ({s_values})
            """)
        self.conn.commit()

    def get_all_from_table(self, table_name, condition=""):
        self.c.execute(f"""SELECT * FROM {table_name} {condition}""")
        return self.c.fetchall()

    def delete_from_table(self, table_name, condition):
        self.c.execute(
            f"""DELETE FROM {table_name}
            {condition}""")
        self.conn.commit()


class Element(object):
    def __init__(self, title, aliases, description):
        self.key = Utils.getKey(title)
        self.title = title
        self.aliases = aliases
        self.description = description


class ElmRef(TableController, Utils.AliaseDict):
    def __init__(
            self, db, table_name,
            elm="""key text PRIMARY KEY,
                    title text, aliases text, description text""",
            elm_input="",
            ref="",
            ref_input=""):
        self.db = db
        self.connect()
        self.table_name = table_name
        self.elm_table = table_name+"_elm"
        self.ref_table = table_name+"_ref"
        self.elm = elm
        self.ref = "key text, title text, aliases text, "+ref
        self.elm_input = elm_input
        self.rf_input = ref_input
        self.create_table(
            self.elm_table,
            self.elm)
        self.create_table(
            self.ref_table,
            self.ref)
        self.__load__()
        self.conn.close()

    def __load__(self):
        super().__init__()
        elms = self.get_all_from_table(self.elm_table)
        for key, title, aliases, description in elms:
            aliases = aliases.split('/')
            self[(key, aliases)] = Element(
                title, aliases, description)
        return self

    def update(self):
        pass


    def delete(self, title):
        key = Utils.getKey(title)
        if not self.exist(key):
            ElementNotExists("Element not exist", key)
            return False
        del self[key]
        self.delete_from_table(self.elm_table,
                               "WHERE key={key}")
        return True

    def new(self, title, aliases, description):
        key = Utils.getKey(title)
        if self.exist(key):
            raise ElementAlreadyExists("Element Already Exists, ", key)
        self.insert_into_table(
            self.elm_table,
            "key, title, aliases, description",
            [key, title, "/".join(aliases), description])
        self[(key, aliases)] = Element(
            title, aliases, description)
        return True
