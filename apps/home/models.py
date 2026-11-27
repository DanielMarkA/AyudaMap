from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


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
        ('FULL_CAPACITY', 'Full Capacity'),
        ('TEMPORARILY_CLOSED', 'Temporarily Closed'),
    ]

    URGENCY_CHOICES = [
        ('LOW', 'Normal / Routine'),
        ('MEDIUM', 'Moderate Need'),
        ('CRITICAL', 'Critical / Urgent'),
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
    latitude = models.FloatField(default=10.3157, help_text="Latitude for map pin")
    longitude = models.FloatField(default=123.8854, help_text="Longitude for map pin")
    operating_hours = models.CharField(max_length=100, default="8:00 AM - 5:00 PM")
    contact_info = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='OPERATIONAL',
        db_index=True,
        help_text="Current operating status of the relief center"
    )
    urgency_level = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default='LOW',
        db_index=True,
        help_text="Priority level for aid distribution or evacuation"
    )
    capacity_total = models.PositiveIntegerField(
        default=100,
        help_text="Total slots, relief packs, or beds available"
    )
    capacity_available = models.PositiveIntegerField(
        default=100,
        help_text="Remaining slots or relief packs currently available"
    )
    supplies_needed = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated list of urgent items (e.g., Water, Rice, First Aid)"
    )
    confirmations = models.PositiveIntegerField(
        default=1,
        help_text="Community verification count confirming this site is active"
    )
    is_verified = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'aid_resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude'], name='idx_resource_coords'),
            models.Index(fields=['category', 'is_verified'], name='idx_res_cat_verified'),
            models.Index(fields=['urgency_level', 'status'], name='idx_res_urgency_status'),
        ]
        verbose_name = 'Aid Resource'
        verbose_name_plural = 'Aid Resources'

    def clean(self):
        super().clean()
        if (
            self.capacity_total is not None
            and self.capacity_available is not None
            and self.capacity_available > self.capacity_total
        ):
            raise ValidationError({
                'capacity_available': 'Available capacity cannot exceed total capacity.',
            })

    @property
    def occupancy_percentage(self):
        if self.capacity_total <= 0:
            return 0
        used = max(0, self.capacity_total - self.capacity_available)
        return min(100, round((used / self.capacity_total) * 100))

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) - {self.get_status_display()}"


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
