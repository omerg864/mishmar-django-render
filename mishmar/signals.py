from django.db.models.signals import post_save
from .models import Shift1 as Shift
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from datetime import datetime
from users.models import UserSettings as USettings
import pytz
from .models import ShiftWeek, Organization, Week, OrganizationShift
import os


@receiver(post_save, sender=Shift)
def send_number_served(sender, instance, created, **kwargs):
    if created:
        lenShifts = len(Shift.objects.all().filter(date=instance.date))
        shifts = Shift.objects.all().filter(date=instance.date)
        users = User.objects.all()
        guards_sent = []
        guards_not_sent = []
        admin_user = ""
        for user in users:
            if user.is_superuser:
                admin_user = user
        for s in shifts:
            user = users.filter(username=s.username).first()
            user_settings = USettings.objects.all().filter(user=user).first()
            guards_sent.append(user_settings.nickname)
        for u in users:
            user_settings = USettings.objects.all().filter(user=u).first()
            if user_settings.nickname not in guards_sent:
                guards_not_sent.append(user_settings.nickname)
        lenUsers = len(User.objects.all())
        tz_is = pytz.timezone('Israel')
        datetime_is = datetime.now(tz_is)
        date = str(datetime_is.strftime("%d/%m/%Y %H:%M:%S"))
        print("Israel time:", datetime_is.strftime("%H:%M:%S"))
        if lenShifts == lenUsers - 1 or int(datetime_is.strftime("%H")) > 12 or lenShifts % 5 == 0:
            message = f'עד עכשיו בשעה {date} הגישו {str(lenShifts)} אנשים סידור לתאריך {instance.date.strftime("%d/%m")}' \
                      + "\n" + f'אנשים שהגישו: {guards_sent}' + "\n" + f'אנשים שלא הגישו: {guards_not_sent}'
            send_mail(
                'כמות משתמשים שהגישו סידור',
                message,
                os.environ.get("DEFAULT_FROM_EMAIL_RAMLA"),
                [admin_user.email],
                fail_silently=False,
            )
            print("sent")


@receiver(post_save, sender=Organization)
def create_weeks(sender, instance, created, **kwargs):
    if created:
        shifts_dic = {}
        shifts = OrganizationShift.objects.all()
        for s in shifts:
            for day in range(1, 8):
                shifts_dic[f'{day}@{s.title}@{s.id}'] = ""
        for i in range(instance.num_weeks):
            nw = Week(date=instance.date, num_week=i, shifts=shifts_dic)
            nw.save()
