from django.contrib import admin

from offers_app.models import Offer, OfferDetail


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'user', 'created_at', 'updated_at')
	search_fields = ('title', 'user__username', 'user__email')


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
	list_display = ('id', 'offer', 'offer_type', 'price', 'delivery_time_in_days')
	list_filter = ('offer_type',)
	search_fields = ('offer__title', 'title')
