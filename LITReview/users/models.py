from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):

    profile_photo = models.ImageField(verbose_name='photo de profil')
    groups = models.ManyToManyField(
        Group,
        related_name='followers',  # Add a unique related_name
        verbose_name='Suit'
    )

    user_permissions = models.ManyToManyField(
    Permission,
    related_name='followers',  # Add a unique related_name
    verbose_name = 'suivi par',
    )
