# Generated by Django 3.1.1 on 2021-05-23 15:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ntc', '0003_auto_20201118_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='spyke/default.svg', upload_to='spyke/'),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_active',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
