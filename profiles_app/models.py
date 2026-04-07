from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    USER_TYPE = (
        ('business', 'Business'),
        ('customer', 'Customer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile')
    file = models.FileField(upload_to='profile_files/', blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE)
    first_name = models.CharField(max_length=150, default='')
    last_name = models.CharField(max_length=150, default='')
    location = models.CharField(max_length=255, default='')
    telephone = models.CharField(max_length=30, default='')
    description = models.TextField(default='')
    working_hours = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=254, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} {self.user_type}"
