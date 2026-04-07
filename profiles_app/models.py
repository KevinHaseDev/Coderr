from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    TYPE_BUSINESS = 'business'
    TYPE_CUSTOMER = 'customer'
    USER_TYPE = (
        (TYPE_BUSINESS, 'Business'),
        (TYPE_CUSTOMER, 'Customer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile')
    file = models.FileField(upload_to='profile_files/', blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE)
    location = models.CharField(max_length=255, default='')
    telephone = models.CharField(max_length=30, default='')
    description = models.TextField(default='')
    working_hours = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.user_type}"
                           