from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Review(models.Model):
	business_user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='received_reviews',
	)
	reviewer = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='written_reviews',
	)
	rating = models.PositiveSmallIntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(5)],
	)
	description = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['business_user', 'reviewer'],
				name='unique_business_user_reviewer_review',
			),
		]

	def __str__(self):
		return f'Review #{self.pk}'
