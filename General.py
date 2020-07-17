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

        # SETTING THE COMMANDS
        self.commands = {
            "add player": self.add_player,
            "rmv player": self.rmv_player,
            "new": self.new
            # "del bar": self.del_bar,
            # "add bar": self.add_bar,
            # "rmv bar": self.rmv_bar
        }
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
            self.connect()
            elm_lib.new(title, aliases, description)
            print("SUCESSO!")
            return True
        except Database.ElementAlreadyExists:
            print("Elemento já existe")
            return False
        finally:
            self.conn.close()
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
            self.connect()
            elm_lib.delete(title)
            return True
        except KeyError:
            print("elm not exist")
            return False
        finally:
            self.conn.close()
    async def add_bar(self, ctx: Event.Context) -> (bool):
        pass
        # """[Adiciona um Elemento barra existente a um player]

        # Args:
        #     self ([type]): [description]

        # Returns:
        #     [bool]: [True se foi adicionado com sucesso]
        # """
        # # Recebendo player como primeiro argumento
        # try:
        #     player = self.get_first_player_mention(ctx)
        # except UserIsNotAPlayer:
        #     print("User não é um player.")
        #     return False
        # except IndexError:
        #     print("User não informado, 1° Argumento")
        #     return False
        # # Recebendo titulo da barra como segundo argumento
        # try:
        #     title = ctx.args[1]
        #     title = self.bars.key(title)
        #     aliases = self.bars.aliases(title)
        # except IndexError:
        #     print("Titulo não informado, 2° Argumento")
        #     return False
        # except KeyError:
        #     print("Barra Inexistente")
        #     return False
        # # VERIFICAR SE O PLAYER JÁ TEM A BARRA
        # if player.bars.exist(title):
        #     print("Player já tém esta barra")
        #     return False
        # # recebendo o user e os valores principais
        # try:
        #     min_value: str = ctx.args[2]
        # except IndexError:
        #     print("Valor minimo não informado, 3° Argumento")
        #     return False
        # try:
        #     max_value: str = ctx.args[3]
        # except IndexError:
        #     print("Valor máximo não informado, 4° Argumento")
        #     return False
        # # recebendo valores opcionais
        # try:
        #     cur_value = ctx.args[4]
        # except Exception:
        #     cur_value = max_value

        # self.connect()
        # self.insert_into_table(
        #     "PC_player_bar_list",
        #     "key, title, aliases, min_value, max_value, cur_value",
        #     [player.key, title, "/".join(aliases),
        #      min_value, max_value, cur_value])
        # self.conn.close()
        # player.bars[(title, aliases)] = Bar(
        #     int(min_value), int(max_value), int(cur_value))
        # # MENSAGEM DE SUCESSO
        # print("SUCESSO")
        # return True

    async def rmv_bar(self, ctx: Event.Context) -> (bool):
        pass
        # """Remove uma barra de algum player

        # Args:
        #     ctx (Event.Context): [Contexto local]

        # Returns:
        #     [bool]: [True se a barra foi removida com sucesso]
        # """
        # try:
        #     player = self.get_first_player_mention(ctx)
        # except UserIsNotAPlayer:
        #     print("User não é um player")
        #     return False
        # except IndexError:
        #     print("User não informado, 1° Argumento")
        #     return False
        # try:
        #     name = " ".join(ctx.args[1:])
        #     title = player.bars.key(name)
        #     del player.bars[title]
        # except IndexError:
        #     print("Titulo não informado, 2° Argumento")
        #     return False
        # except KeyError:
        #     print("Barra Inexistente")
        #     return False
        # self.connect()
        # self.delete_from_table(
        #     "PC_player_bar_list",
        #     f"WHERE key='{player.key}' AND title='{title}'")
        # self.conn.close()

        # # sucesso
        # print("SUCESSO!")
        # return True
