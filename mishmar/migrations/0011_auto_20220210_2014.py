# Generated by Django 3.2.8 on 2022-02-10 18:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mishmar', '0010_auto_20220209_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='arming_log',
            name='data',
            field=jsonfield.fields.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='armingrequest',
            name='username',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='שם משתמש'),
        ),
    ]