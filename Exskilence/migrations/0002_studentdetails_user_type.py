# Generated by Django 4.1.13 on 2024-11-04 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Exskilence', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentdetails',
            name='user_Type',
            field=models.CharField(default='SW', max_length=3),
        ),
    ]
