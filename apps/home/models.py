from datetime import time
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.contrib.auth.models import User
from django.utils import timezone
from apps.locations import CITY_CHOICES


def format_time_12h(value):
    if value is None:
        return ""
    hour = value.hour % 12 or 12
    suffix = "AM" if value.hour < 12 else "PM"
    return f"{hour}:{value.minute:02d} {suffix}"


def _open_hours_q(current_time):
    return (
        Q(is_24_7=True)
        | Q(opens_at__isnull=True)
        | Q(closes_at__isnull=True)
        | (
            Q(opens_at__lt=F('closes_at'))
            & Q(opens_at__lte=current_time)
            & Q(closes_at__gt=current_time)
        )
        | (
            Q(opens_at__gt=F('closes_at'))
            & (Q(opens_at__lte=current_time) | Q(closes_at__gt=current_time))
        )
    )


class ResourceQuerySet(models.QuerySet):
    def filter_by_effective_status(self, status, now=None):
        current_time = timezone.localtime(now).time().replace(microsecond=0)
        open_q = _open_hours_q(current_time)
        if status == 'CLOSED':
            return self.filter(Q(status='CLOSED') | ~open_q)
        if status in ('OPERATIONAL', 'LIMITED'):
            return self.filter(status=status).filter(open_q)
        return self

    def currently_open(self, now=None):
        current_time = timezone.localtime(now).time().replace(microsecond=0)
        return self.filter(status__in=['OPERATIONAL', 'LIMITED']).filter(_open_hours_q(current_time))


class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('MEDICAL', 'Medical Facilities'),
        ('FOOD', 'Food Assistance Center'),
        ('SHELTER', 'Shelter / Evacuation'),
        ('GOV', 'Government Service'),
        ('DONATION', 'Donation Center'),
    ]

    STATUS_CHOICES = [
        ('OPERATIONAL', 'Operational / Open'),
        ('LIMITED', 'Crowded / Limited'),
        ('CLOSED', 'Closed'),
    ]

    SERVICE_CHOICES = [
        ('SHELTER', 'Safe Shelter'),
        ('WATER', 'Drinking Water'),
        ('FOOD', 'Hot Meals / Packs'),
        ('MEDICAL', 'First Aid / Meds'),
        ('POWER', 'Power / Charging'),
        ('WIFI', 'Wi-Fi / Signal'),
        ('PWD', 'PWD Accessible'),
        ('PET_FRIENDLY', 'Pet-Friendly'),
    ]

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_resources',
        help_text="User/Volunteer who created this aid resource entry"
    )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    city = models.CharField(
        max_length=100,
        choices=CITY_CHOICES,
        blank=True,
        default='',
        db_index=True,
        help_text="Canonical city/municipality for consistent local filtering",
    )
    latitude = models.FloatField(default=10.3157, help_text="Latitude for map pin")
    longitude = models.FloatField(default=123.8854, help_text="Longitude for map pin")
    is_24_7 = models.BooleanField(
        default=False,
        help_text="Check if this aid haven operates 24 hours a day",
    )
    opens_at = models.TimeField(
        null=True,
        blank=True,
        default=time(8, 0),
        help_text="Daily opening time (Asia/Manila)",
    )
    closes_at = models.TimeField(
        null=True,
        blank=True,
        default=time(17, 0),
        help_text="Daily closing time (Asia/Manila)",
    )
    contact_info = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='OPERATIONAL',
        db_index=True,
        help_text="Current operating status of the relief center"
    )
    services_offered = models.JSONField(
        default=list,
        blank=True,
        help_text="Available safe haven services and amenities",
    )
    supplies_needed = models.CharField(
        max_length=255,
        blank=True,
        help_text="Internal coordinator note: urgent items needed (admin only)"
    )
    confirmations = models.PositiveIntegerField(
        default=1,
        help_text="Community verification count confirming this site is active"
    )
    is_verified = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ResourceQuerySet.as_manager()

    class Meta:
        db_table = 'aid_resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude'], name='idx_resource_coords'),
            models.Index(fields=['category', 'is_verified'], name='idx_res_cat_verified'),
        ]
        verbose_name = 'Aid Resource'
        verbose_name_plural = 'Aid Resources'

    @classmethod
    def matching_service_codes(cls, query):
        q = (query or '').strip().lower()
        if not q:
            return []
        tokens = [t for t in q.split() if t]
        matches = []
        for code, label in cls.SERVICE_CHOICES:
            searchable = f"{code.lower()} {label.lower()}"
            if q in searchable or (tokens and all(tok in searchable for tok in tokens)):
                matches.append(code)
        return matches

    def clean(self):
        super().clean()
        if not self.is_24_7:
            if (self.opens_at is None) != (self.closes_at is None):
                raise ValidationError({
                    'closes_at': 'Provide both opening and closing times, or mark the hub as Open 24/7.',
                })
            if self.opens_at is not None and self.closes_at is not None and self.opens_at == self.closes_at:
                raise ValidationError({
                    'closes_at': 'Closing time must differ from opening time, or mark the hub as Open 24/7.',
                })

        valid_services = {code for code, _ in self.SERVICE_CHOICES}
        if self.services_offered:
            invalid = [s for s in self.services_offered if s not in valid_services]
            if invalid:
                raise ValidationError({
                    'services_offered': f"Invalid service option(s): {', '.join(invalid)}",
                })

    @property
    def display_location(self):
        loc = (self.location or '').strip()
        city = (self.city or '').strip()
        if not city:
            return loc
        if not loc:
            return city
        if city.lower() in loc.lower():
            return loc
        return f"{loc}, {city}"

    def is_within_operating_hours(self, now=None):
        if self.is_24_7 or self.opens_at is None or self.closes_at is None:
            return True
        current_time = timezone.localtime(now).time().replace(microsecond=0)
        if self.opens_at < self.closes_at:
            return self.opens_at <= current_time < self.closes_at
        return current_time >= self.opens_at or current_time < self.closes_at

    @property
    def is_auto_closed(self):
        return self.status != 'CLOSED' and not self.is_within_operating_hours()

    @property
    def effective_status(self):
        if self.status == 'CLOSED' or not self.is_within_operating_hours():
            return 'CLOSED'
        return self.status

    @property
    def effective_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.effective_status, self.effective_status)

    @property
    def opens_at_display(self):
        return format_time_12h(self.opens_at)

    @property
    def operating_hours_display(self):
        if self.is_24_7:
            return "24/7"
        if self.opens_at and self.closes_at:
            return f"{format_time_12h(self.opens_at)} - {format_time_12h(self.closes_at)}"
        return "Hours not specified"

    @property
    def service_labels(self):
        label_map = dict(self.SERVICE_CHOICES)
        return [label_map[code] for code in (self.services_offered or []) if code in label_map]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) - {self.effective_status_display}"


class ResourceStatusLog(models.Model):
    ACTION_CHOICES = [
        ('STATUS_UPDATE', 'Status Updated'),
        ('CONFIRM_ACTIVE', 'Confirmed Active'),
        ('SUPPLY_PLEDGE', 'Supplies / Aid Pledged'),
    ]

    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='status_logs'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resource_updates'
    )
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES, default='STATUS_UPDATE')
    previous_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30, blank=True)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'aid_resource_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.resource.name} - {self.get_action_type_display()} ({self.created_at:%Y-%m-%d %H:%M})"
