from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'user', 'institute', 'enrollment_date')
    list_filter = ('institute', 'enrollment_date')
    search_fields = ('roll_number', 'user__first_name', 'user__last_name')