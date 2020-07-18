from classes import Utils
from controllers import Event, Database, Terrain
from controllers.Player import Player
from typing import Optional, Tuple
import discord


# Ultimos testes:
# new player 100%
# del player 100%
# new bar 100%
# del bar 100%
# add bar 100%
# remove bar

# EXCEPTIONS


class UserIsNotAPlayer(Exception):
    """Exceção em casos de um usuario do discord não for um player aceito

    """

    def __init__(self, message, user):
        self.message = message
        self.user = user

# CLASSES


class Controller(Database.TableController, dict):
    """Controle de player e suas funções


    Args:
        [Club]: Um objeto Club como referencia de db e strings
    """

    def __init__(self):
        super().__init__()
        print("Player Controller -> new")

        # SETTING THE PLAYER LIST AND ACCEPTEDS
        self.accepted_players = []
        self.players = {}

        self.connect()
        # ACCEPTED PLAYER TABLE
        self.create_table(
            "PC_accepted_players",
            "key text PRIMARY KEY")

        # LOADING ACCEPTED PLAYERS
        acp = self.get_all_from_table("PC_accepted_players")
        self.accepted_players = [i[0] for i in acp]

        # CREATING BAR ELEMENT
        self['bar'] = Database.ElmRef(
            self.db,
            "bar",
            ref="min_value integer, max_value integer, cur_value integer")
        # CREATING ATTRIBUTE ELEMENT
        self['attribute'] = Database.ElmRef(
            self.db,
            "attribute",
            ref="value integer")
        # close the db
        self.conn.close()

        # SETTING THE COMMANDS
        try:
            self.cmds
        except AttributeError:
            self.cmds = {}
        self.cmds['add player'] = self.add_player
        self.cmds['rmv player'] = self.rmv_player
        self.cmds['new'] = self.new_elm
        self.cmds['del'] = self.del_elm

    def isPlayer(self, user: discord.User) -> (bool):
        """ Verifica no registro se o usuario
            informado é um player já aceito

        Args:
            user ([discord.User]): Um usuario do discord

        Returns:
            [bool]: [um bool, true se for um player]
        """
        key = str(user.id)
        return key in self.accepted_players

    def Player(self, user: discord.User) -> (Optional[Player]):
        """Cria uma instancia do player referente ao ususuario informado

        Args:
            user ([discord.User]): [Usuario do discord em questão]

        Returns:
            [Player]: [O usuario referente ao user, ou None caso o player não
             tiver sido aceito]
        """
        key = str(user.id)
        if not (key in self.accepted_players):
            return None
        if not (key in self.players):
            self.players[key] = Player(self, user)
        return self.players[key]

    def get_first_player_mention(self, ctx: Event.Context):
        """Pega o primeiro usuario informado no contexto e devolve o Player referente

        Args:
            ctx (Event.Context): [Contexto Local]

        Raises:
            UserIsNotAPlayer: [Caso o user informado não seja um player aceito
            contém a mensagem e o user]

        Returns:
            [Player]: [Um Player em caso de nenhum problema]
        """
        user = ctx.message.mentions[0]
        player = self.Player(user)
        if not player:
            raise UserIsNotAPlayer(
                f"User {user.name}:{user.id} is not a player", user)
        return player

    async def add_player(self, ctx: Event.Context) -> (bool):
        """Define um User como um palyer aceito

        Args:
            ctx (Event.Context): [Contexto local]

        Returns:
            [bool]: [True para operação bem sucedida]
        """
        try:
            user = ctx.message.mentions[0]
            key = str(user.id)
        except IndexError:
            print("Player não informado")
            return False
        if self.isPlayer(user):
            print("Usuario já é um player")
            return False
        try:
            self.connect()
            self.insert_into_table("PC_accepted_players", "key", [key])
            self.accepted_players.append(key)
            print("SUCESSO!")
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.conn.close()
        # MENSAGEM DE SUCESSO

    async def rmv_player(self, ctx: Event.Context) -> (bool):
        """Remove um player dos players aceitos

        Args:
            ctx (Event.Context): [Contexto local]

        Returns:
            [bool]: [True se o player existe e foi deletado]
        """
        try:
            player = self.get_first_player_mention(ctx)
        except IndexError:
            print("Player não informado")
            return False
        except UserIsNotAPlayer:
            print("User não é um player")
            return False
        try:
            self.connect()
            self.delete_from_table("PC_accepted_players",
                                   f"WHERE key={player.key}")
            self.accepted_players.remove(player.key)
            print("SUCESSO")
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.conn.close()

    async def new_elm(self, ctx: Event.Context) -> (bool):
        """Cria uma novo elemento, um Elemento simples para Vitrine

        Args:
            ctx (Event.Context): [Contexto local]

        Returns:
            [bool]: [True se criou uma nova barra.]
        """
        # entrada
        try:
            lib = ctx.args[0]
            title = ctx.args[1]
            aliases = ctx.args[2:]
            description = ctx.comment
        except IndexError:
            print("argumentos mal informados")
            return False
        # validação
        try:
            elm_lib: Database.ElmRef = self[lib]
        except KeyError:
            print("Lib Inexistente mal informados")
            return False
        #
        try:
            elm_lib.connect()
            elm_lib.new(title, aliases, description)
            print("SUCESSO!")
            self.conn.close()
            return True
        except Database.ElementAlreadyExists:
            print("Elemento já existe")
            return False
        finally:
            elm_lib.conn.close()
            
        # MENSAGEM DE SUCESSO

    async def del_elm(self, ctx: Event.Context) -> (bool):
        """Deleta um elemento de uma vitrine existente,
        não apaga os elementos dos jogadores.

        Args:
            self ([type]): [description]
        """
        try:
            lib = ctx.args[0]
            elm = ctx.args[1:]
        except IndexError:
            print("Informe os elementos corretamente")
            return False
        try:
            elm_lib = self[lib]
        except KeyError:
            print("elm_lib does not exist")
            return False
        try:
            elm_lib.connect()
            elm_lib.delete(title)
            return True
        except Database.ElementNotExists:
            print("elm not exist")
            return False
        except KeyError:
            print("elm not exist")
            return False
        finally:
            elm_lib.conn.close()