from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    OWNER = 'OWNER'
    STAFF = 'STAFF'
    MECHANIC = 'MECHANIC'

    ROLE_CHOICES = [
        (OWNER, 'Owner'),
        (STAFF, 'Staff'),
        (MECHANIC, 'Mechanic'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STAFF)
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_owner(self):
        return self.role == self.OWNER

    @property
    def is_staff_member(self):
        return self.role == self.STAFF

    @property
    def is_mechanic(self):
        return self.role == self.MECHANIC
