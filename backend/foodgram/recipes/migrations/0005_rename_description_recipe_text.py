# Generated by Django 3.2.18 on 2023-04-23 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_favorites_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
    ]