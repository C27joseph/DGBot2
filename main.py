import discord
from classes import Json
from controllers import Dice, Event
import General
import sqlite3
from typing import Tuple


class Club(General.Controller):
    def __init__(self, guild: discord.Guild):
        self.key = str(guild.id)
        self.local = "private/clubs/"
        self.guild: discord.Guild = guild
        self.db = f"{self.local}{self.key}.db"

        self.dc = Dice.Controller(self)
        super().__init__()


    def connect(self) -> (Tuple[sqlite3.Connection, sqlite3.Cursor]):
        self.conn = sqlite3.connect(self.db)
        self.c = self.conn.cursor()
        return self.conn, self.c

    async def on_message(self, ctx: Event.Context):
        if ctx.isCommand:
            ctx.player = self.Player(ctx.message.author)
            for command, function in self.cmds.items():
                if ctx.content.startswith(command):
                    ctx.setArgs(ctx.content[len(command):])
                    print(f"command: {command}, used")
                    success = await function(ctx)
                    if not success:
                        continue
                    return True
        elif ctx.isEvent:
            pass
        else:
            pass


class Client(discord.Client):
    def __init__(self):
        super().__init__()
        # READING ALL CLIENT SETTINGS
        self.tokens = Json.loadWrite(
            pathfile='private/token')
        self.command_prefixes = Json.loadWrite(
            pathfile='private/clubs/command_prefixes')
        self.event_prefixes = Json.loadWrite(
            pathfile='private/clubs/event_prefixes')
        self.languages = Json.loadWrite(
            pathfile='private/languages')
        # GETTING CONFIGURATION
        self.bot = "dev"
        self.version = "1.001"
        self.name = "DGBot"
        self.local = "private/"

        self.clubs = {}

        self.run(self.tokens[self.bot])

    def Club(self, guild) -> (Club):
        key = str(guild.id)
        if not (key in self.clubs):
            self.clubs[key] = Club(guild)
        return self.clubs[key]

    def get_command_prefix(self, guild: discord.Guild) -> (str):
        key = str(guild.id)
        try:
            return self.event_prefixes[key]
        except KeyError:
            return "/"

    def get_event_prefix(self, guild: discord.Guild) -> (str):
        key = str(guild.id)
        try:
            return self.event_prefixes[key]
        except KeyError:
            return "!"

    async def on_ready(self):
        # EVENTO DE QUANDO O BOT ESTA ATIVO
        # pega o tempo atual
        # envia informações da inicialização
        print(f"{self.name} [{self.bot}] - {self.version} init")
        # informações sobre cada guild
        for guild in self.guilds:
            print(f"\t{guild.name}:{guild.id} connected")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if not message.guild:
            return
        guild = message.guild
        # COMMAND PREFIX
        c_prefix = self.get_command_prefix(guild)
        # EVENT PREFIX
        e_prefix = self.get_event_prefix(guild)
        # instancia um club a partir da guild
        ctx = Event.Context(c_prefix, e_prefix, message)
        club = self.Club(guild)
        await club.on_message(ctx)


client = Client()
