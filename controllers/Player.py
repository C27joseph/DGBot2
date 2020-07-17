from classes import Utils


class Bar(object):
    """[Uma barra que armazena quantidade com valor maximoe e minimo]

        Args:
            min_value (int): [O minimo de valor que a barra pode chegar]
            max_value (int): [O valor máximo que a barra pode alcançar]
            cur_value (int): [O valor atual da barra]
    """

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


class Player(object):
    def __init__(self, club, user):
        self.club = club
        self.user = user
        self.key = str(user.id)
        super().__init__()
