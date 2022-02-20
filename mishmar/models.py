from time import time
from django import forms
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import send_mail
import datetime
from jsonfield import JSONField
import collections



class Post(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now, verbose_name="תאריך")
    title = models.CharField(max_length=30, verbose_name="כותרת")
    text = models.TextField(blank=True, verbose_name="טקסט")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "פוסט"
        verbose_name_plural = "פוסטים"


class Settings(models.Model):
    submitting = models.BooleanField(default=True, verbose_name="ניתן להגיש/לשנות הגשות")
    pin_code = models.IntegerField(default=1234, verbose_name="קוד זיהוי")
    officer = models.CharField(max_length=20, verbose_name="קצין מתקן")
    city = models.CharField(max_length=100, verbose_name="עיר")
    max_seq0 = models.IntegerField(default=2, verbose_name="מספר רצפים מקסימלי לילה לצהריים")
    max_seq1 = models.IntegerField(default=2, verbose_name="מספר רצפים מקסימלי צהריים לבוקר")
    version = models.CharField(max_length=10, default="1.0", verbose_name="גרסה")
    friday_morning = models.BooleanField(default=False, verbose_name="שישי בוקר נחשב במינימום הגשות?", blank=True)
    friday_noon = models.BooleanField(default=False, verbose_name="שישי בצהריים נחשב במינימום הגשות?", blank=True)
    num_mags = models.PositiveIntegerField(default=3, verbose_name="מספר מחסניות")
    hand_cuffs = models.PositiveIntegerField(default=8, verbose_name="מספר אזיקים")
    num_mag_cases = models.PositiveIntegerField(default=8, verbose_name="מספר פונדות")
    num_gun_cases = models.PositiveIntegerField(default=8, verbose_name="מספר נרתיקים")


    def __str__(self):
        return "הגדרות"

class OrganizationShift(models.Model):
    title = models.CharField(max_length=200, verbose_name="משמרת")
    index = models.IntegerField(default=1, verbose_name="מספר משמרת")
    shift_num = models.IntegerField(default=1, verbose_name="סוג משמרת")
    sub_title = models.CharField(max_length=200, verbose_name="כותרת משמרת", blank=True, null=True)
    opening = models.BooleanField(default=False, verbose_name="פתיחה", blank=True)
    manager = models.BooleanField(default=False, verbose_name="אחמש", blank=True)
    pull = models.BooleanField(default=False, verbose_name="משיכה", blank=True)

    def __str__(self):
        return f'{self.title} - {self.sub_title} - {self.id} - {self.shift_num}'
    
    class Meta:
        verbose_name = "משמרת מבנה סידור"
        verbose_name_plural = "משמרות מבנה סידור"


class Week(models.Model):
    date = models.DateField(default=timezone.now)
    num_week = models.IntegerField(default=0, blank=False)
    shifts = JSONField()

    def __str__(self):
        return f'{self.date} שבוע {self.num_week + 1}'
    
    class Meta:
        verbose_name = "שבוע סידור"
        verbose_name_plural = "שבועות סידור"

class Organization1(models.Model):
    date = models.DateField(default=timezone.now)
    num_weeks = models.IntegerField(default=2, blank=False)
    published = models.BooleanField(default=False, verbose_name="פרסום")
    weeks_data = JSONField()

    def __str__(self):
        return f'{self.date}'

    def get_absolute_url(self):
        return reverse("organization-update", kwargs={"pk": self.pk})
    
    class Meta:
        verbose_name = "סידור עבודה"
        verbose_name_plural = "סידורי עבודה"

class Organization(models.Model):
    date = models.DateField(default=timezone.now)
    num_weeks = models.IntegerField(default=2, blank=False)
    published = models.BooleanField(default=False, verbose_name="פרסום")

    def __str__(self):
        return f'{self.date}'

    def get_absolute_url(self):
        return reverse("organization-update", kwargs={"pk": self.pk})
    
    class Meta:
        verbose_name = "סידור עבודה"
        verbose_name_plural = "סידורי עבודה"

class Shift(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization1, on_delete=models.CASCADE, blank=True, null=True)
    notes = models.TextField(max_length=200, blank=True, verbose_name="הערות")
    seq_night = models.IntegerField(default=0, verbose_name="מ\"ס רצפים לילה לצהריים")
    seq_noon = models.IntegerField(default=0, verbose_name="מ\"ס רצפים צהריים לבוקר")
    weeks_data = JSONField()

    def __str__(self):
        return f'{self.username.first_name} {self.username.last_name} ({self.username}) - {self.date}'

    def get_absolute_url(self):
        return reverse("shift-update", kwargs={"pk": self.pk})
    
    class Meta:
        verbose_name = "הגשה"
        verbose_name_plural = "הגשות"

class Shift1(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    notes = models.TextField(max_length=200, blank=True, verbose_name="הערות")
    seq_night = models.IntegerField(default=0, verbose_name="מ\"ס רצפים לילה לצהריים")
    seq_noon = models.IntegerField(default=0, verbose_name="מ\"ס רצפים צהריים לבוקר")

    def __str__(self):
        return f'{self.username.first_name} {self.username.last_name} ({self.username}) - {self.date}'

    def get_absolute_url(self):
        return reverse("shift-update", kwargs={"pk": self.pk})
    
    class Meta:
        verbose_name = "הגשה כללית"
        verbose_name_plural = "הגשות כלליות"


class ShiftWeek(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    num_week = models.IntegerField(default=0, blank=False)
    date = models.DateField(default=timezone.now)
    M1 = models.BooleanField(default=False, verbose_name="ראשון בוקר")
    A1 = models.BooleanField(default=False, verbose_name="ראשון צהריים")
    N1 = models.BooleanField(default=False, verbose_name="ראשון לילה")
    P1 = models.BooleanField(default=True, verbose_name="משיכה")
    R1 = models.BooleanField(default=False, verbose_name="תגבור")
    notes1 = models.CharField(max_length=100, blank=True, verbose_name="הערות")
    M2 = models.BooleanField(default=False, verbose_name="שני בוקר")
    A2 = models.BooleanField(default=False, verbose_name="שני צהריים")
    N2 = models.BooleanField(default=False, verbose_name="שני לילה")
    P2 = models.BooleanField(default=True, verbose_name="משיכה")
    R2 = models.BooleanField(default=False, verbose_name="תגבור")
    notes2 = models.CharField(max_length=100, blank=True, verbose_name="הערות")
    M3 = models.BooleanField(default=False, verbose_name="שלישי בוקר")
    A3 = models.BooleanField(default=False, verbose_name="שלישי צהריים")
    N3 = models.BooleanField(default=False, verbose_name="שלישי לילה")
    P3 = models.BooleanField(default=True, verbose_name="משיכה")
    R3 = models.BooleanField(default=False, verbose_name="תגבור")
    notes3 = models.CharField(max_length=100, blank=True, verbose_name="הערות")
    M4 = models.BooleanField(default=False, verbose_name="רביעי בוקר")
    A4 = models.BooleanField(default=False, verbose_name="רביעי צהריים")
    N4 = models.BooleanField(default=False, verbose_name="רביעי לילה")
    P4 = models.BooleanField(default=True, verbose_name="משיכה")
    R4 = models.BooleanField(default=False, verbose_name="תגבור")
    notes4 = models.CharField(max_length=100, blank=True, verbose_name="הערות")
    M5 = models.BooleanField(default=False, verbose_name="חמישי בוקר")
    A5 = models.BooleanField(default=False, verbose_name="חמישי צהריים")
    N5 = models.BooleanField(default=False, verbose_name="חמישי לילה")
    P5 = models.BooleanField(default=True, verbose_name="משיכה")
    R5 = models.BooleanField(default=False, verbose_name="תגבור")
    notes5 = models.CharField(max_length=100, blank=True, verbose_name="הערות")
    M6 = models.BooleanField(default=False, verbose_name="שישי בוקר")
    A6 = models.BooleanField(default=False, verbose_name="שישי צהריים")
    N6 = models.BooleanField(default=False, verbose_name="שישי לילה")
    P6 = models.BooleanField(default=True, verbose_name="משיכה")
    R6 = models.BooleanField(default=False, verbose_name="תגבור")
    notes6 = models.CharField(max_length=100, blank=True, verbose_name="הערות")
    M7 = models.BooleanField(default=False, verbose_name="שבצ בוקר")
    A7 = models.BooleanField(default=False, verbose_name="שבת צהריים")
    N7 = models.BooleanField(default=False, verbose_name="שבת לילה")
    P7 = models.BooleanField(default=True, verbose_name="משיכה")
    R7 = models.BooleanField(default=False, verbose_name="תגבור")
    notes7 = models.CharField(max_length=100, blank=True, verbose_name="הערות")

    def __str__(self):
        return f'{self.username.first_name} {self.username.last_name} ({self.username}) - {self.date}'
    
    class Meta:
        verbose_name = "הגשה שבועית"
        verbose_name_plural = "הגשות שבועיות"



class Event(models.Model):
    nickname = models.CharField(default="", max_length=20, verbose_name="כינוי", blank=False)
    date2 = models.DateField(default=timezone.now, verbose_name="תאריך")
    description = models.CharField(default="", max_length=50, verbose_name="תאור")

    def __str__(self):
        return f'{self.nickname} {self.date2}'

    class Meta:
        verbose_name = "אירוע"
        verbose_name_plural = "אירועים"


class IpBan(models.Model):
    ipaddress = models.GenericIPAddressField(verbose_name="כתובת IP")
    num_tries = models.IntegerField(default=0, verbose_name="מספר ניסיונות")

    def __str__(self):
        return f'{self.ipaddress} ({self.num_tries})'

    class Meta:
        verbose_name = "חסימת IP"
        verbose_name_plural = "חסימות IP"


class Gun(models.Model):
    full_name = models.CharField(verbose_name="שם מלא", max_length=50)
    short_name = models.CharField(verbose_name="שם קצר", max_length=20)

    def __str__(self):
        return self.short_name
    
    class Meta:
        verbose_name = "נשק"
        verbose_name_plural = "נשקים"

class ValidationLog(models.Model):
    date = models.DateField(verbose_name="תאריך", default=timezone.now)
    num_guns_safe_m = models.IntegerField(verbose_name="מספר נשקים בכספת בוקר", blank=True, default=0)
    num_guns_shift_m = models.IntegerField(verbose_name="מספר נשקים במשמרת בוקר", blank=True, default=0)
    time_checked_m = models.TimeField(verbose_name="שעת בדיקה בוקר", blank=True, default=timezone.now)
    name_checked_m = models.CharField(max_length=50, verbose_name="שם בודק בוקר", blank=True, default="")
    sig_m = models.TextField(verbose_name="חתימה בוקר", blank=True, null=True)
    num_guns_safe_a = models.IntegerField(verbose_name="מספר נשקים בכספת צהריים", blank=True, default=0)
    num_guns_shift_a = models.IntegerField(verbose_name="מספר נשקים במשמרת צהריים", blank=True, default=0)
    time_checked_a = models.TimeField(verbose_name="שעת בדיקה צהריים", blank=True, default=timezone.now)
    name_checked_a = models.CharField(max_length=50, verbose_name="שם בודק צהריים", blank=True, default="")
    sig_a = models.TextField(verbose_name="חתימה צהריים", blank=True, null=True)
    num_guns_safe_n = models.IntegerField(verbose_name="מספר נשקים בכספת לילה", blank=True, default=0)
    num_guns_shift_n = models.IntegerField(verbose_name="מספר נשקים במשמרת לילה", blank=True, default=0)
    time_checked_n = models.TimeField(verbose_name="שעת בדיקה לילה", blank=True, default=timezone.now)
    name_checked_n = models.CharField(max_length=50, verbose_name="שם בודק לילה", blank=True, default="")
    sig_n = models.TextField(verbose_name="חתימה לילה", blank=True, null=True)


    def __str__(self):
        return str(self.date)
    
    class Meta:
        verbose_name = "בדיקת נשקים"
        verbose_name_plural = "בדיקות נשקים"


class Arming_Log(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="תאריך", blank=False)
    data = JSONField()

    def get_absolute_url(self):
        return reverse("signature", kwargs={"pk": self.pk})

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")
    
    class Meta:
        verbose_name = "הזנה ביומן חימוש"
        verbose_name_plural = "הזנות ביומן חימוש"

class ArmingRequest(models.Model):
    log = models.ForeignKey(Arming_Log, on_delete=models.CASCADE, verbose_name="הזנה ביומן חימוש", blank=False)
    input_num = models.IntegerField(verbose_name="מספר הזנה", blank=False, default=1)
    username = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="שם משתמש", blank=False, null=True)
    id_num = models.CharField(max_length=9, verbose_name="תעודת זהות", blank=False, default="")
    shift_num = models.IntegerField(verbose_name="מספר משמרת", default=1, blank=False)
    time_in = models.TimeField(default=timezone.now, verbose_name="זמן כניסה", blank=False)
    gun = models.ForeignKey(Gun, on_delete=models.CASCADE, verbose_name="מספר נשק", blank=False)
    num_mags = models.IntegerField(default=2, verbose_name="מספר מחסניות", blank=False)
    hand_cuffs = models.IntegerField(default=6, verbose_name="אזיקים", blank=False)
    gun_case = models.IntegerField(default=6, verbose_name="פונדה", blank=False)
    mag_case = models.IntegerField(default=6, verbose_name="נרתיק", blank=False)
    keys = models.BooleanField(default=False, verbose_name="מפתחות", blank=False)
    radio = models.BooleanField(default=False, verbose_name="קשר", blank=False)
    radio_kit = models.BooleanField(default=False, verbose_name="ערכת שמע", blank=False)
    time_out = models.TimeField(verbose_name="זמן יציאה", blank=True, null=True)
    signature_in = models.TextField(verbose_name="חתימת כניסה", null=True, blank=True)
    signature_out = models.TextField(verbose_name="חתימת יציאה", null=True, blank=True)
    read = models.BooleanField(default=False, verbose_name="טופל?", blank=False)
    reason = models.TextField(verbose_name="סיבה", blank=False, default="")

    def __str__(self):

        return self.log.data[str(self.input_num)]["name"] + " " + str(self.log.date)

    class Meta:
        verbose_name = "בקשה לשינוי יומן חימוש"
        verbose_name_plural = "בקשות לשינוי יומן חימוש"