# Generated by Django 3.1.8 on 2023-04-08 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='postal_code',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='userbankaccount',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('N/A', 'Prefer not to say')], max_length=3),
        ),
    ]