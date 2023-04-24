# Generated by Django 4.2 on 2023-04-24 03:06

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', django_fsm.FSMField(default='new', max_length=50, protected=True)),
            ],
        ),
    ]
