from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [
        ("superadmin", "Superadmin"),
        ("owner",      "Owner"),
        ("admin",      "Admin"),
        ("staff",      "Staff"),
        ("instructor", "Instructor"),
        ("cliente",    "Cliente"),
    ]
    email = models.EmailField(unique=True)
    role  = models.CharField(max_length=20, choices=ROLES, default="cliente")

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def is_admin_or_above(self):
        return self.role in ('superadmin', 'owner', 'admin')

    @property
    def can_manage_courses(self):
        return self.role in ('superadmin', 'owner', 'admin', 'instructor')