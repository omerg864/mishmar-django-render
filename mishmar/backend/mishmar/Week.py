class Week:

    def __init__(self):
        self.morning = 0
        self.afterNoon = 0
        self.night = 0
        self.satNight = 0
        self.satMorning = 0
        self.resMorning = -1
        self.resAfterNoon = -1
        self.served = 0
        self.got = 0

    def get_quality(self, shift: int):
        if shift == 0:
            return self.night
        elif shift == 1:
            return self.satMorning
        else:
            return self.satNight

    def set_quality(self, shift: int, value):
        if shift == 0:
            self.night = value
        elif shift == 1:
            self.satMorning = value
        else:
            self.satNight = value

    def count_got(self, organized, name: str, week: int):
        if week == 0:
            for i in range(5):
                if name in organized["M" + str(i)]:
                    self.got = self.got + 1
                if name in organized["A" + str(i)]:
                    self.got = self.got + 1
        else:
            for i in range(7, 12):
                if name in organized["M" + str(i)]:
                    self.got = self.got + 1
                if name in organized["A" + str(i)]:
                    self.got = self.got + 1

    def count_served(self, days, name: str, week: int):
        if week == 0:
            for i in range(5):
                if name in days["M" + str(i)]:
                    self.got = self.got + 1
                elif name in days["A" + str(i)]:
                    self.got = self.got + 1
        else:
            for i in range(7, 12):
                if name in days["M" + str(i)]:
                    self.got = self.got + 1
                elif name in days["A" + str(i)]:
                    self.got = self.got + 1