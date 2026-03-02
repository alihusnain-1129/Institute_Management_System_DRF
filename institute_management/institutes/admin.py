from django.contrib import admin
from .models import Institute

@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('name', 'email')