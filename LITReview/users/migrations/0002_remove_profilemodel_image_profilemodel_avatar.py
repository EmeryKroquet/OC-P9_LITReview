# Generated by Django 4.2.2 on 2023-07-14 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilemodel',
            name='image',
        ),
        migrations.AddField(
            model_name='profilemodel',
            name='avatar',
            field=models.ImageField(default='default.jpg', upload_to='profile_avatars'),
        ),
    ]
