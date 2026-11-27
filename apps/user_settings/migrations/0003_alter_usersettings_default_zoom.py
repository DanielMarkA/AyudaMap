from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_settings', '0002_usersettings_default_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersettings',
            name='default_zoom',
            field=models.PositiveSmallIntegerField(
                default=12,
                help_text='Default map zoom level (5-18)',
                validators=[MinValueValidator(5), MaxValueValidator(18)],
            ),
        ),
    ]
