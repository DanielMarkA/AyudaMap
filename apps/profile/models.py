from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=150, blank=True, help_text="Affiliated NGO, LGU, or Volunteer Group")
    is_volunteer = models.BooleanField(default=False, help_text="Designates whether this user is an active relief volunteer")
    profile_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return self.full_name or self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
