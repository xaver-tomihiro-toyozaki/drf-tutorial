# Generated by Django 4.2 on 2023-04-24 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0003_issue_workflow'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workflow',
            old_name='issue',
            new_name='issue_id',
        ),
        migrations.AlterUniqueTogether(
            name='workflow',
            unique_together={('issue_id', 'step')},
        ),
    ]
