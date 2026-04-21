from django.contrib import admin

from orders_app.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'title',
		'customer_user',
		'business_user',
		'status',
		'price',
		'updated_at',
	)
	list_filter = ('status', 'offer_type')
	search_fields = ('title', 'customer_user__username', 'business_user__username')
