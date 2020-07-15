import discord


class Context(object):
    def __init__(self, c_prefix: str, e_prefix: str, message: discord.Message):
        self.e_prefix = e_prefix
        self.c_prefix = c_prefix
        self.message = message
        self.__content__()

    def setArgs(self, content):
        args = []
        message = ""
        found_message = False
        for word in content.split():
            if word.startswith("#"):
                found_message = True
            if found_message:
                message += word+" "
            else:
                args.append(word)
        a = []
        text = ""
        found = False
        for arg in args:
            if arg.startswith("\"") and not arg.endswith("\n"):
                found = True
            if found:
                text += arg+" "
                if arg.endswith("\"") and not arg.startswith("\""):
                    a.append(text[1:-2])
                    text = ""
                    found = False
            else:
                a.append(arg)
        if len(text) > 0:
            a = a + text.split()
        self.args = a
        self.comment = message.rstrip()[1:]

    def __content__(self):
        content: str = self.message.content
        self.isCommand = False
        self.isEvent = False
        if content.startswith(self.c_prefix):
            self.content = content[len(self.c_prefix):]
            self.isCommand = True
        elif content.startswith(self.e_prefix):
            self.content = content[len(self.e_prefix):]
            self.isEvent = True
