from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offer_images/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class OfferDetail(models.Model):
    OFFER_TYPE_BASIC = 'basic'
    OFFER_TYPE_STANDARD = 'standard'
    OFFER_TYPE_PREMIUM = 'premium'
    OFFER_TYPE_CHOICES = (
        (OFFER_TYPE_BASIC, 'Basic'),
        (OFFER_TYPE_STANDARD, 'Standard'),
        (OFFER_TYPE_PREMIUM, 'Premium'),
    )

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"