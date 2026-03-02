from django.contrib import admin
from .models import Exam, Result

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'exam_type', 'exam_date', 'total_marks')
    list_filter = ('exam_type', 'course__institute', 'exam_date')
    search_fields = ('title', 'course__name')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'grade', 'entered_at')
    list_filter = ('exam__course__institute', 'grade')
    search_fields = ('student__user__first_name', 'student__roll_number')