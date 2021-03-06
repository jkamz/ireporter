# Generated by Django 2.1.7 on 2019-03-19 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interventions', '0007_auto_20190318_0742'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImagesModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/images/')),
                ('intervention', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interventions.InterventionsModel')),
            ],
        ),
    ]
