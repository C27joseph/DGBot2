from controllers import Event
import discord


class Message(dict):
    def __init__(self, *v, **kv):
        super().__init__(*v, **kv)
        if not self.__contains__('reactions'):
            self['reactions'] = []

    async def send(
            self, ctx: Event.Context,
            channel: discord.TextChannel = None, **kv):
        """Envia a mensagem no contexto

        Args:
            ctx (Event.Context): [Contexto local]
            channel ([discord.TextChannel], optional):
            [Canal de texto para enviar a mensagem]

        Returns:
            [type]: [description]
        """
        self.ctx = ctx
        self.__embed__(**kv)
        self.__content__(**kv)
        if not channel:
            channel = ctx.message.channel
        self.mtx = await channel.send(self['content'], embed=self['embed'])
        try:
            for reaction in self['reactions']:
                await self.mtx.add_reaction(reaction)
        except Exception:
            return
        return self.mtx

    def __embed__(self, **kv):
        if not self.__contains__('embed'):
            self['embed'] = None
            return None
        if not self['embed']:
            return None
        e = self['embed']
        embed = discord.Embed()

        if e.__contains__('footer'):
            footer = ", ".join(embed['footer'])
            embed.set_footer(
                text=footer,
                icon_url="https://i.imgur.com/l37XqXC.png")
        if e.__contains__('title'):
            embed.title = self.__msg__(e['title'], **kv)
        if e.__contains__('description'):
            embed.description = self.__msg__(e['description'], **kv)
        if e.__contains__('color'):
            embed.color = self.__msg__(e['color'], **kv)
        try:
            if e.__contains__('image') and len(e['image']) > 0:
                embed.set_image(url=embed['image'])
        except Exception:
            pass
        if e.__contains__('fields'):
            try:
                fields = e['fields']
                for field in fields:
                    name = field[0]
                    try:
                        value = field[1]
                    except Exception:
                        value = ""
                    try:
                        inline = field[2]
                    except Exception:
                        inline = True
                    embed.add_field(name=name, value=value, inline=inline)
            except Exception:
                pass
        return embed

    def __content__(self, **kv):
        if not self.__contains__('content'):
            self['content'] = ""
            return True
        try:
            return self.__msg__(self['content'], **kv)
        except Exception:
            return ""

    def __msg__(
            self, string,
            total="",
            expression="",
            title="",
            user="",
            qtd=0) -> (str):
        author = self.ctx.author.mention
        comment = self.ctx.comment
        replaces = {
            ("<#author>", str(author)),
            ("<#total>", str(total)),
            ("<#expression>", str(expression)),
            ("<#comment>", str(comment)),
            ("<#title>", str(title)),
            ("<#user>", str(user)),
            ("<#qtd>", str(qtd))
        }
        # PARA CADA DUPLA EFETUAR REPLACE
        for r, v in replaces:
            string = string.replace(r, v)
        return string
