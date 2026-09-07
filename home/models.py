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
    operating_hours = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category})"