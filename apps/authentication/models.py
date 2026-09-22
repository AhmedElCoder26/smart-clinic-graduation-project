from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        DOCTOR = 'DOCTOR', 'Doctor'
        PATIENT = 'PATIENT', 'Patient'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='authentication_users',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='authentication_users_permissions',
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"