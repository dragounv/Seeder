# Generated by Django 2.2.20 on 2021-08-31 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvests', '0019_harvest_new_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='harvest',
            name='json_frozen',
            field=models.TextField(blank=True, null=True),
        ),
    ]
