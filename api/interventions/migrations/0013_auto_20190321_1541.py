# Generated by Django 2.1.7 on 2019-03-21 15:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0012_auto_20190321_1519'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interventionsmodel',
            old_name='facebook_share_url',
            new_name='facebook',
        ),
        migrations.RenameField(
            model_name='interventionsmodel',
            old_name='linkedIn_share_url',
            new_name='linkedIn',
        ),
        migrations.RenameField(
            model_name='interventionsmodel',
            old_name='mail_share_url',
            new_name='mail',
        ),
        migrations.RenameField(
            model_name='interventionsmodel',
            old_name='twitter_share_url',
            new_name='twitter',
        ),
    ]
