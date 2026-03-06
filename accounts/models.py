from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    subscribed_channels = models.ManyToManyField('self', symmetrical=False, related_name='subscribers', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username