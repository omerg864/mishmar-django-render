# Generated by Django 3.2.8 on 2022-02-20 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mishmar', '0021_organization1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mishmar.organization1'),
        ),
    ]