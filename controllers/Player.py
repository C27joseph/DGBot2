import discord
import sqlite3
from classes import Utils
from controllers import Event


class Bar(object):
    def __init__(self, min_value: int, max_value: int, cur_value: int):
        pass


class BarElement(object):
    def __init__(self, title, aliases, description):
        self.title = title
        self.aliases = aliases
        self.description = description
        pass


class Player(object):
    def __init__(self, master, user: discord.User):
        self.master = master
        self.user = user
        self.key = str(user.id)

        self.conn, self.c = self.master.connect()
        self.__load_bar__()

        self.conn.close()

    def __load_bar__(self):
        self.c.execute(
            f"""SELECT * FROM PC_player_bar_list WHERE owner={self.key}""")
        bars = self.c.fetchall()
        self.bars = Utils.AliaseDict()
        for key, title, aliases, mv, mv, cv in bars:
            aliases = aliases.split('/')
            self.bars[(title, aliases)] = Bar(mv, mv, cv)


class Controller(Utils.TableController):
    def __init__(self, master):
        print("Player Controller -> new")
        self.master = master
        self.accepted_players = []
        self.players = {}

        self.commands = {
            "new player": self.new_player,
            "del player": self.del_player,
            "new bar": self.new_bar,
            "del bar": self.del_bar,
            "add bar": self.add_bar,
            "rmv bar": self.rmv_bar
        }
        # CREATING IF NOT EXIST TABLE
        self.connect()
        # ACCEPTED PLAYER LIST
        self.create_table(
            "PC_accepted_players",
            "key text PRIMARY KEY")
        # BAR ELEMENT LIST
        self.create_table(
            "PC_bar_elements",
            "title text PRIMARY KEY, aliases text, description text")
        # PLAYER BARS LIST
        self.create_table(
            "PC_player_bar_list",
            """key text, title text, aliases text,
            min_value integer, max_value integer, cur_value integer""")

        # LOADING EACH TABLE

        # LOADING ACCEPTED PLAYERS
        ap = self.get_all_from_table("PC_accepted_players")
        self.accepted_players = [player[0] for player in ap]

        # LOADING BAR TABLE
        self.bars = Utils.AliaseDict()
        bars = self.get_all_from_table("PC_bar_elements")
        for title, aliases, description in bars:
            aliases = aliases.split('/')
            self.bars[(title, aliases)] = BarElement(
                title, aliases, description)
        self.conn.close()

    def connect(self):
        conn, c = self.master.connect()
        self.conn: sqlite3.Connection = conn
        self.c: sqlite3.Cursor = c
        return self.conn, self.c

    def isPlayer(self, user):
        key = user.id
        return key in self.accepted_players

    def Player(self, user):
        key = str(user.id)
        if not (key in self.accepted_players):
            return None
        if not (key in self.players):
            self.players[key] = Player(self.master, user)
        return self.players[key]

    async def new_player(self, ctx: Event.Context):
        try:
            user = ctx.message.mentions[0]
            if self.isPlayer(user):
                print("Este player ja foi adicionado")
                return False
            key = str(user.id)
        except IndexError:
            print("Player não informado")
            return False
        self.connect()
        self.insert_into_table("PC_accepted_players", "key", [key])
        self.conn.close()
        self.accepted_players.append(key)
        # MENSAGEM DE SUCESSO

    async def del_player(self, ctx: Event.Context):
        user = ctx.message.mentions[0]
        if not self.isPlayer(user):
            print("Este usuario não é player")
            return False
        key = str(user.id)
        self.connect()
        self.delete_from_table("PC_accepted_players", f"WHERE key={key}")
        self.conn.close()
        self.accepted_players.remove(key)

    async def new_bar(self, ctx: Event.Context):
        try:
            title = ctx.args[0]
            if self.bars.exist(title):
                print("Barra ja existente")
                return False
            aliases = ctx.args[1:]
            description = ctx.comment
        except IndexError:
            print("argumentos mal informados")
            return False
        self.connect()
        self.insert_into_table(
            "PC_bar_elements", "title, aliases, description",
            [title, "/".join(aliases), description])
        self.conn.close()
        self.bars[(title, aliases)] = BarElement(
            title, aliases, description)
        # MENSAGEM DE SUCESSO
        print("SUCESSO!")
        return True

    async def del_bar(self, ctx: Event.Context):
        title = " ".join(ctx.args)
        if not self.bars.exist(title):
            print("Barra inexistente existente")
            return False
        title = self.bars.key(title)
        self.connect()
        self.delete_from_table("PC_bar_elements", f"WHERE title={title}")
        self.conn.close()
        pass

    async def add_bar(self, ctx: Event.Context):
        # recebendo o titulo e vendo se existe
        try:
            user = ctx.message.mentions[0]
            key = str(user.id)
            player = self.Player(user)
            if not player:
                print("User não é um jogador")
                return False
        except IndexError:
            print("User não informado, 1° Argumento")
            return False
        try:
            title = ctx.args[1]
            title = self.bars.key(title)
            aliases = self.bars.aliases(title)
        except IndexError:
            print("Titulo não informado, 2° Argumento")
            return False
        except KeyError:
            print("Barra Inexistente")
            return False
        # VERIFICAR SE O PLAYER JÁ TEM A BARRA
        if player.bars.exist(title):
            print("Player já tém esta barra")
            return False
        # recebendo o user e os valores principais
        try:
            min_value: str = ctx.args[2]
        except IndexError:
            print("Valor minimo não informado, 3° Argumento")
            return False
        try:
            max_value: str = ctx.args[3]
        except IndexError:
            print("Valor máximo não informado, 4° Argumento")
            return False
        # recebendo valores opcionais
        try:
            cur_value = ctx.args[4]
        except Exception:
            cur_value = max_value

        # conectando e adionando a database
        self.conn, self.c = self.master.connect()
        self.c.execute(
            """INSERT INTO p_bar_list
                    (owner, title, aliases, min_value, max_value, cur_value)
                VALUES(?, ?, ?, ?, ?, ?)
            """,
            [key, title, "/".join(aliases), min_value, max_value, cur_value])
        player.bars[(title, aliases)] = Bar(
            int(min_value), int(max_value), int(cur_value))
        self.conn.commit()
        self.conn.close()
        # MENSAGEM DE SUCESSO

    async def rmv_bar(self, ctx: Event.Context):
        pass
