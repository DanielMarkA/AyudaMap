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
    latitude = models.FloatField(default=14.5995, help_text="Latitude for map pin")
    longitude = models.FloatField(default=120.9842, help_text="Longitude for map pin")
    operating_hours = models.CharField(max_length=100, default="8:00 AM - 5:00 PM")
    contact_info = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='OPERATIONAL',
        db_index=True,
        help_text="Current operating status of the relief center"
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
        ]
        verbose_name = 'Aid Resource'
        verbose_name_plural = 'Aid Resources'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) - {self.get_status_display()}"
