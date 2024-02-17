# Generated by Django 4.2.9 on 2024-02-17 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0007_remove_member_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='authorised_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authorised', to='members.member'),
        ),
    ]
