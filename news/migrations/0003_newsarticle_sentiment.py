# Generated by Django 5.0.3 on 2024-03-29 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_newsarticle'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='sentiment',
            field=models.TextField(default='neutral'),
        ),
    ]