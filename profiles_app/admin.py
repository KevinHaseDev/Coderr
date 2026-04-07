from django.contrib import admin

from profiles_app.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'type', 'created_at')
	list_filter = ('type',)
	search_fields = ('user__username', 'user__email')

# Register your models here.
