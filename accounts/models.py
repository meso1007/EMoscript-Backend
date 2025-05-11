from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(default='じこしょうかいはまだないよ！', blank=True, null=True)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='profile_images/', default='profile_images/profile-default.png', blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    is_locked = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)



    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        related_query_name="customuser",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
        related_query_name="customuser",
    )
