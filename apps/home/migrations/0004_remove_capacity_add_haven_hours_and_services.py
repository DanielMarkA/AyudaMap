import re
from datetime import time
from django.db import migrations, models


TIME_RANGE_RE = re.compile(
    r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:-|to|–|—)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
    re.IGNORECASE,
)


def _to_time(hour_str, minute_str, meridiem):
    hour = int(hour_str)
    minute = int(minute_str or 0)
    if meridiem:
        mer = meridiem.lower()
        if mer == 'pm' and hour < 12:
            hour += 12
        elif mer == 'am' and hour == 12:
            hour = 0
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return time(hour, minute)
    return None


def _parse_operating_hours(raw):
    text = (raw or '').strip()
    lower = text.lower()
    if '24/7' in lower or '24 hours' in lower or '24 hrs' in lower:
        return True, None, None

    match = TIME_RANGE_RE.search(text)
    if match:
        start = _to_time(match.group(1), match.group(2), match.group(3))
        end = _to_time(match.group(4), match.group(5), match.group(6))
        if start and end and start != end:
            return False, start, end

    return False, time(8, 0), time(17, 0)


def migrate_resources_forward(apps, schema_editor):
    Resource = apps.get_model('home', 'Resource')
    ResourceStatusLog = apps.get_model('home', 'ResourceStatusLog')

    status_map = {
        'FULL_CAPACITY': 'LIMITED',
        'TEMPORARILY_CLOSED': 'CLOSED',
    }

    for resource in Resource.objects.all():
        is_24_7, opens_at, closes_at = _parse_operating_hours(getattr(resource, 'operating_hours', ''))
        resource.is_24_7 = is_24_7
        resource.opens_at = opens_at
        resource.closes_at = closes_at
        if resource.status in status_map:
            resource.status = status_map[resource.status]
        resource.save(update_fields=['is_24_7', 'opens_at', 'closes_at', 'status'])

    for old_val, new_val in status_map.items():
        ResourceStatusLog.objects.filter(previous_status=old_val).update(previous_status=new_val)
        ResourceStatusLog.objects.filter(new_status=old_val).update(new_status=new_val)


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_resource_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='is_24_7',
            field=models.BooleanField(default=False, help_text='Check if this aid haven operates 24 hours a day'),
        ),
        migrations.AddField(
            model_name='resource',
            name='opens_at',
            field=models.TimeField(blank=True, default=time(8, 0), help_text='Daily opening time (Asia/Manila)', null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='closes_at',
            field=models.TimeField(blank=True, default=time(17, 0), help_text='Daily closing time (Asia/Manila)', null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='services_offered',
            field=models.JSONField(blank=True, default=list, help_text='Available safe haven services and amenities'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='status',
            field=models.CharField(
                choices=[
                    ('OPERATIONAL', 'Operational / Open'),
                    ('LIMITED', 'Crowded / Limited'),
                    ('CLOSED', 'Closed'),
                ],
                db_index=True,
                default='OPERATIONAL',
                help_text='Current operating status of the relief center',
                max_length=30,
            ),
        ),
        migrations.RunPython(migrate_resources_forward, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='resource',
            name='capacity_total',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='capacity_available',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='operating_hours',
        ),
    ]
