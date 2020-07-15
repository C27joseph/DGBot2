from unidecode import unidecode
import sqlite3

# EXEPTIONS


class NoTableError(Exception):
    def __init__(self, table_name):
        self.table_name = table_name

# FUNCTIONS


def getKey(name: str) -> (str):
    return unidecode(str.lower(name))


# CLASSES
class KSingleton(object):
    _instances: dict = {}

    def __new__(cls, master):
        key = str(master.id)
        if not (key in cls._instances):
            cls._instances[key] = super().__new__(cls)
        return cls._instances[key]


class AliaseDict(dict):
    def __init__(self, *args, **kwargs):
        self.__aliases__ = {}
        self.__backup__ = {}
        super().__init__(*args, **kwargs)

    def __setitem__(self, key_aliases, value):
        key: str = getKey(key_aliases[0])
        aliases: list = key_aliases[1]
        self.__aliases__[key] = key
        self.__backup__[key] = aliases
        for alias in aliases:
            self.__aliases__[getKey(alias)] = key
        return super().__setitem__(key, value)

    def aliases(self, name) -> (list):
        key = getKey(name)
        key = self.__aliases__[key]
        return self.__backup__[key]

    def key(self, name) -> (str):
        key: str = getKey(name)
        return self.__aliases__[key]

    def exist(self, name):
        key = getKey(name)
        return self.__aliases__.__contains__(key)

    def __getitem__(self, name):
        key: str = getKey(name)
        print("aliases, ", self.__aliases__)
        key = self.__aliases__[key]
        return super().__getitem__(key)


class TableController(object):
    def connect(self, db: str):
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()
        return self.conn, self.c

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
