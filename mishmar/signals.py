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
        shifts = Shift.objects.all().filter(date=instance.date).exclude(username__username='admin')
        users = User.objects.all().exclude(username='metagber').exclude(username='admin')
        guards_sent = []
        guards_not_sent = []
        emails = []
        for user in users:
            if user.groups.filter(name="staff").exists():
                emails.append(user.email)
        for s in shifts:
            user = users.filter(id=s.username.id).first()
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
                emails,
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

@receiver(post_save, sender=OrganizationShift)
def change_weeks(sender, instance, created, **kwargs):
    if created:
        organizations = Organization.objects.all().order_by('-date')
        for org in organizations:
            weeks = Week.objects.all().filter(date=org.date)
            for w in weeks:
                for i in range(1, 8):
                    w.shifts[f'{i}@{instance.title}@{instance.id}'] = ""
                    w.save()