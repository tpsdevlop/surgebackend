# Generated by Django 4.1.13 on 2024-11-05 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Exskilence', '0002_studentdetails_user_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coursedetails',
            old_name='Discription',
            new_name='Description',
        ),
        migrations.RenameField(
            model_name='errorlogs',
            old_name='Occrued_time',
            new_name='Occurred_time',
        ),
        migrations.RenameField(
            model_name='login_data',
            old_name='User_catagory',
            new_name='User_category',
        ),
    ]
