# Generated by Django 5.1.4 on 2025-04-28 00:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_library', '0011_alter_like_options_alter_watchedcontent_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='like',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='like',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='watchedcontent',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='watchedcontent',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='watchedcontent',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='watchedcontent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='watchlist',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='watchlist',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
