from django.db.models.signals import post_save
from .models import Shift as Shift
from .models import Organization1 as Organization
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from datetime import datetime
from users.models import UserSettings as USettings
import pytz
from .models import OrganizationShift
import os



@receiver(post_save, sender=Shift)
def send_email_served(sender, instance, created, **kwargs):
    if created:
        lenShifts = len(Shift.objects.all().filter(organization=instance.organization))
        shifts = Shift.objects.all().filter(organization=instance.organization).exclude(user__username='admin')
        users = User.objects.all().exclude(username='metagber').exclude(username='admin')
        guards_sent = []
        guards_not_sent = []
        emails = []
        for user in users:
            if user.groups.filter(name="staff").exists():
                emails.append(user.email)
        for s in shifts:
            user_settings = USettings.objects.all().filter(user=s.user).first()
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
            message = f'עד עכשיו בשעה {date} הגישו {str(lenShifts)} אנשים סידור לתאריך {instance.organization.date.strftime("%d/%m")}' \
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
def create_org_data(sender, instance, created, **kwargs):
    if created:
        shifts_dic = {}
        shifts = OrganizationShift.objects.all()
        for i in range(instance.num_weeks):
            shifts_dic[str(i)] = {}
            for s in shifts:
                for day in range(1, 8):
                    shifts_dic[str(i)][f'{day}@{s.id}'] = ""
        instance.weeks_data = shifts_dic
        instance.save()


@receiver(post_save, sender=OrganizationShift)
def change_weeks(sender, instance, created, **kwargs):
    if created:
        organizations = Organization.objects.all().order_by('-date')
        for org in organizations:
            for j in range(org.num_weeks):
                for i in range(1, 8):
                    org.weeks_data[str(j)][f'{i}@{instance.id}'] = ""
            org.save()