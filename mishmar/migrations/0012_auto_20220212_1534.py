# Generated by Django 3.2.8 on 2022-02-12 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mishmar', '0011_auto_20220210_2014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='arming_log',
            name='gun',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='gun_case',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='hand_cuffs',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='id_num',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='keys',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='mag_case',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='name',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='num_mags',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='radio',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='radio_kit',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='shift_num',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='signature_in',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='signature_out',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='time_in',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='time_out',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='username',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='valid_in',
        ),
        migrations.RemoveField(
            model_name='arming_log',
            name='valid_out',
        ),
    ]