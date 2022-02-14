from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(default="אין", max_length=20, verbose_name="כינוי")
    night = models.IntegerField(default=0, verbose_name="לילה")
    sat_night = models.IntegerField(default=0, verbose_name="שישי לילה/מוצ\"ש")
    sat_morning = models.IntegerField(default=0, verbose_name="שבת בוקר")
    sat_noon = models.IntegerField(default=0, verbose_name="שבת צהריים")
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")
    sat = models.BooleanField(default=False, verbose_name="עושה רק מוצ\"ש")
    language = models.CharField(default="hebrew", max_length=30, verbose_name="שפה")

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    class Meta:
        verbose_name = "הגדרות משתמש"
        verbose_name_plural = "הגדרות משתמשים"
