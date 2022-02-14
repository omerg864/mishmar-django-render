from .Week import Week
from django.contrib.auth.models import User


class Guard:

    def __init__(self):
        self.name = ""
        self.qualityNight = 0
        self.qualitySatNight = 0
        self.qualitySatMorning = 0
        self.weeks = [Week(), Week()]
        self.authority = False

    def set_quality(self, shift, value):
        if shift == 0:
            self.qualityNight = value
        elif shift == 1:
            self.qualitySatMorning = value
        elif shift == 2:
            self.qualitySatNight = value

    def get_quality(self, shift):
        if shift == 0:
            return self.qualityNight
        elif shift == 1:
            return self.qualitySatMorning
        else:
            return self.qualitySatNight

    def __str__(self):
        temp = ""
        temp = "name: " + self.name + "  qualityNight: " + str(self.qualityNight) + "  qualitySatNight: " + str(
            self.qualitySatNight)
        temp = temp + "  qualitySatMorning: " + str(self.qualitySatMorning) + "  authority: " + str(self.authority)
        return temp
