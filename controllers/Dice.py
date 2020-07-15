from random import randrange
import re


class Roll:
    def __init__(self,
                 nDices: int,
                 nFaces: int):
        self.nDices = nDices
        self.nFaces = nFaces
        self.total, self.dices = self.__roll__()

    def __roll__(self):
        total: int = 0
        dices: list = []
        for i in range(self.nDices):
            v = randrange(1, self.nFaces+1)
            dices.append(v)
            total += v
        return total, dices


class Controller(object):
    def __init__(self, master):
        self.master = master
        self.commands = {}
        pass

    def get_expression(
            self, args,
            dice_format="<#nDices>d<nFaces> <#dices>: <#total>",
            short_format="<#nDices>d<nFaces>: <#total>"):
        total: str = ""
        expression: str = ""
        pattern = re.compile('\d*d\d+')
        where = 0
        for arg in args:
            # INCREMENTANDO TOTAL E EXPRESSAO COM O ARGUMENTO
            total += arg+" "
            expression += arg+" "
            dices = pattern.findall(arg)
            # ACHANDO OS PADRÕES DE DADO
            if len(dices) > 6:
                dice_format = short_format
            for dice in dices:
                nDices, nFaces = dice.split('d')
                if len(nDices) == 0:
                    nDices = 1
                # ROLANDO O DADO DE CADA OCORRENCIA
                roll = Roll(int(nDices), int(nFaces))
                # SUBSTITUINDO O ORIGINAL PELO TOTAL
                total = total.replace(dice, str(roll.total), 1)
                # SUBSTITUINDO O ORIGINAL PELO TRATADO
                if roll.nDices > 10:
                    dice_format = short_format
                dicef = dice_format.replace("<#nDices>", str(roll.nDices))
                dicef = dicef.replace("<#nFaces>", str(roll.nFaces))
                dicef = dicef.replace("<#dices>", str(roll.dices))
                dicef = dicef.replace("<#total>", str(roll.total))
                expression = expression[:where] + expression[where:].replace(
                    dice, dicef, 1)
                where = where + expression[where:].find(dicef)+len(dicef)
        # CALCULANDO A EXPRESSÃO DE TOTAL ENCONTRADA
        total = eval(total)
        return total, expression
