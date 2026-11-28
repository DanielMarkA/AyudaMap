from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_remove_capacity_add_haven_hours_and_services'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='resource',
            name='idx_res_urgency_status',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='urgency_level',
        ),
        migrations.AlterField(
            model_name='resource',
            name='supplies_needed',
            field=models.CharField(
                blank=True,
                help_text='Internal coordinator note: urgent items needed (admin only)',
                max_length=255,
            ),
        ),
    ]
