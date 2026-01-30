from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.conf import settings
import os


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    color = models.CharField(max_length=20, default='#ffffff')
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False)
    trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.title if self.title else 'Untitled Note'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        default=None
    )

    def __str__(self):
        return f"{self.user.username}'s profile"


# Auto-create & save profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)

        # Use existing SVG avatars from static/avatars
        try:
            # Get first letter from first name, then last name, then username
            initial = (instance.first_name or instance.last_name or instance.username or 'U')[:1].upper()
            
            # Path to the pre-made SVG avatar
            svg_path = os.path.join(settings.BASE_DIR, 'static', 'avatars', f'{initial}.svg')
            
            # Read the SVG file and save it to profile_picture
            if os.path.exists(svg_path):
                with open(svg_path, 'rb') as f:
                    svg_data = f.read()
                
                filename = f"{instance.username}_avatar.svg"
                profile.profile_picture.save(filename, ContentFile(svg_data), save=True)
        except Exception as e:
            # fail silently; do not block user creation
            pass


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()