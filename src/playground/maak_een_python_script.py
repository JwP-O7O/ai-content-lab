import random


class Dobbelsteen:
    def __init__(self, zijden=6):
        self.zijden = zijden

    def roll(self):
        return random.randint(1, self.zijden)


if __name__ == "__main__":
    dobbelsteen = Dobbelsteen()
    resultaat = dobbelsteen.roll()
    print(resultaat)
