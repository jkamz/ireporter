# Generated by Django 2.1.7 on 2019-03-14 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0002_auto_20190314_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interventionsmodel',
            name='createdBy',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
