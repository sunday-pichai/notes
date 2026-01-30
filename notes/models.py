from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
import hashlib
import colorsys
from django.core.files.base import ContentFile
import urllib.request
import urllib.parse


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

        # If no profile picture provided, generate a colorful gradient SVG avatar
        try:
            name_seed = (instance.username or str(instance.id)).encode('utf-8')
            h = hashlib.md5(name_seed).hexdigest()

            # derive two hues from hash for gradient
            hue1 = int(h[0:6], 16) % 360
            hue2 = int(h[6:12], 16) % 360

            # convert HSL to hex RGB
            def hsl_to_hex(hue, sat=0.65, light=0.55):
                r, g, b = colorsys.hls_to_rgb(hue/360.0, light, sat)
                return '#{0:02x}{1:02x}{2:02x}'.format(int(r*255), int(g*255), int(b*255))

            color1 = hsl_to_hex(hue1)
            color2 = hsl_to_hex(hue2)

            initial = (instance.first_name or instance.username or '')[:1].upper()
            if not initial:
                initial = 'U'

            svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="{color1}" />
      <stop offset="100%" stop-color="{color2}" />
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" rx="32" fill="url(#g)" />
  <text x="50%" y="54%" text-anchor="middle" dy=".35em" font-family="Segoe UI, Roboto, Helvetica, Arial, sans-serif" font-size="96" fill="#ffffff" opacity="0.95">{initial}</text>
</svg>'''

            data = svg.encode('utf-8')
            filename = f"{instance.username}_avatar.svg"
            profile.profile_picture.save(filename, ContentFile(data), save=True)
        except Exception:
            # fail silently; do not block user creation
            pass


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()