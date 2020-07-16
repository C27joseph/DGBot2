import discord
import sqlite3
from typing import Union
from classes import Utils
from controllers import Event


# Ultimos testes:
# new player 100%
# del player 100%
# new bar 100%
# del bar 100%
# add bar 100%
# remove bar

# EXCEPTIONS


class UserIsNotAPlayer(Exception):
    def __init__(self, message, user):
        self.message = message
        self.user = user

# CLASSES


class Bar(object):
    def __init__(self, min_value: int, max_value: int, cur_value: int):
        self.min_value = int(min_value)
        self.max_value = int(max_value)
        self.cur_value = int(cur_value)
        self.edited = False

    def __add__(self, other):
        value = self.cur_value + other
        value = Utils.clamp(value, self.min_value, self.max_value)
        bar = Bar(self.min_value, self.max_value, value)
        bar.edited = True
        return bar

    def __sub__(self, other):
        value = self.cur_value - other
        value = Utils.clamp(value, self.min_value, self.max_value)
        bar = Bar(self.min_value, self.max_value, value)
        bar.edited = True
        return bar

    def __mul__(self, other):
        value = self.cur_value * other
        value = Utils.clamp(value, self.min_value, self.max_value)
        bar = Bar(self.min_value, self.max_value, value)
        bar.edited = True
        return bar

    def __truediv__(self, other):
        value = self.cur_value / other
        value = Utils.clamp(value, self.min_value, self.max_value)
        bar = Bar(self.min_value, self.max_value, value)
        bar.edited = True
        return bar


class BarElement(object):
    def __init__(self, title, aliases, description):
        self.title = title
        self.aliases = aliases
        self.description = description
        self.edited = False
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
            f"""SELECT * FROM PC_player_bar_list WHERE key={self.key}""")
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
            "name text PRIMARY KEY, title text, aliases text, description text"
        )
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
        for name, title, aliases, description in bars:
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
        key = str(user.id)
        return key in self.accepted_players

    def Player(self, user) -> (Union[Player, None]):
        key = str(user.id)
        if not (key in self.accepted_players):
            return None
        if not (key in self.players):
            self.players[key] = Player(self.master, user)
        return self.players[key]

    def get_first_player_mention(self, ctx: Event.Context):
        user = ctx.message.mentions[0]
        player = self.Player(user)
        if not player:
            raise UserIsNotAPlayer(
                f"User {user.name}:{user.id} is not a player", user)
        return player

    async def new_player(self, ctx: Event.Context):
        try:
            user = ctx.message.mentions[0]
            key = str(user.id)
            if self.isPlayer(user):
                print("Usuario já é um player")
                return False
        except IndexError:
            print("Player não informado")
            return False
        self.connect()
        self.insert_into_table("PC_accepted_players", "key", [key])
        self.conn.close()
        self.accepted_players.append(key)
        # MENSAGEM DE SUCESSO

    async def del_player(self, ctx: Event.Context):
        try:
            player = self.get_first_player_mention(ctx)
        except IndexError:
            print("Player não informado")
            return False
        except UserIsNotAPlayer:
            print("User não é um player")
            return False
        self.connect()
        self.delete_from_table("PC_accepted_players",
                               f"WHERE key={player.key}")
        self.conn.close()
        self.accepted_players.remove(player.key)
        print("SUCESSO")
        return True

    async def new_bar(self, ctx: Event.Context):
        try:
            title = ctx.args[0]
            if self.bars.exist(title):
                print("Barra ja existente")
                return False
            aliases = ctx.args[1:]
            description = ctx.comment
            name = Utils.getKey(title)
        except IndexError:
            print("argumentos mal informados")
            return False
        self.connect()
        self.insert_into_table(
            "PC_bar_elements",
            "name, title, aliases, description",
            [name, title, "/".join(aliases), description])
        self.conn.close()
        self.bars[(title, aliases)] = BarElement(
            title, aliases, description)
        # MENSAGEM DE SUCESSO
        print("SUCESSO!")
        return True

    async def del_bar(self, ctx: Event.Context):
        title = " ".join(ctx.args)
        if not self.bars.exist(title):
            print("Barra inexistente")
            return False
        name = self.bars.key(title)
        self.connect()
        self.delete_from_table("PC_bar_elements", f"WHERE name='{name}'")
        self.conn.close()
        del self.bars[name]
        pass

    async def add_bar(self, ctx: Event.Context):
        # Recebendo player como primeiro argumento
        try:
            player = self.get_first_player_mention(ctx)
        except UserIsNotAPlayer:
            print("User não é um player.")
            return False
        except IndexError:
            print("User não informado, 1° Argumento")
            return False
        # Recebendo titulo da barra como segundo argumento
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

        self.connect()
        self.insert_into_table(
            "PC_player_bar_list",
            "key, title, aliases, min_value, max_value, cur_value",
            [player.key, title, "/".join(aliases),
             min_value, max_value, cur_value])
        self.conn.close()
        player.bars[(title, aliases)] = Bar(
            int(min_value), int(max_value), int(cur_value))
        # MENSAGEM DE SUCESSO
        print("SUCESSO")

    async def rmv_bar(self, ctx: Event.Context):
        try:
            player = self.get_first_player_mention(ctx)
        except UserIsNotAPlayer:
            print("User não é um player")
            return False
        except IndexError:
            print("User não informado, 1° Argumento")
            return False
        try:
            name = " ".join(ctx.args[1:])
            title = player.bars.key(name)
            del player.bars[title]
        except IndexError:
            print("Titulo não informado, 2° Argumento")
            return False
        except KeyError:
            print("Barra Inexistente")
            return False
        self.connect()
        self.delete_from_table(
            "PC_player_bar_list",
            f"WHERE key='{player.key}' AND title='{title}'")
        self.conn.close()

        # sucesso
        print("SUCESSO!")
        return True
