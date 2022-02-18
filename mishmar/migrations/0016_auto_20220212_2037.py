# Generated by Django 3.2.8 on 2022-02-12 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mishmar', '0015_delete_settings1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='hand_cuffs',
            field=models.PositiveIntegerField(default=8, verbose_name='מספר אזיקים'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='num_gun_cases',
            field=models.PositiveIntegerField(default=8, verbose_name='מספר נרתיקים'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='num_mag_cases',
            field=models.PositiveIntegerField(default=8, verbose_name='מספר פונדות'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='num_mags',
            field=models.PositiveIntegerField(default=3, verbose_name='מספר מחסניות'),
        ),
    ]