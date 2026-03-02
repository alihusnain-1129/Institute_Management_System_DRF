from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'institute', 'department', 'joining_date')
    list_filter = ('institute', 'department', 'joining_date')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'department')