from django.db import models

class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('MEDICAL', 'Medical Facilities'),
        ('FOOD', 'Food Assistance Center'),
        ('SHELTER', 'Shelter / Evacuation'),
        ('GOV', 'Government Service'),
        ('DONATION', 'Donation Center'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(default=14.5995, help_text="Latitude for map pin")
    longitude = models.FloatField(default=120.9842, help_text="Longitude for map pin")
    operating_hours = models.CharField(max_length=100, default="8:00 AM - 5:00 PM")
    contact_info = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
