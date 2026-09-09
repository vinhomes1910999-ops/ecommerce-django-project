from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Khách hàng'
        ADMIN = 'admin', 'Quản trị viên'

    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)

    def __str__(self):
        return self.username
