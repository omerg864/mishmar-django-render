# Generated by Django 3.2.8 on 2022-02-18 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_usersettings_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersettings',
            name='nickname',
            field=models.CharField(blank=True, default='אין', max_length=20, verbose_name='כינוי'),
        ),
    ]