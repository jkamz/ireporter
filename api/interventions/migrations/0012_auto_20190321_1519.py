# Generated by Django 2.1.7 on 2019-03-21 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0011_auto_20190320_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='interventionsmodel',
            name='facebook_share_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interventionsmodel',
            name='linkedIn_share_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interventionsmodel',
            name='mail_share_url',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='interventionsmodel',
            name='twitter_share_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]