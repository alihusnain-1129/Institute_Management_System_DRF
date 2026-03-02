from django.db import models
from institutes.models import Institute
from authentication.models import User
from teachers.models import Teacher  # Import Teacher model

class Course(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='courses')
    course_code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['institute', 'course_code']
        ordering = ['course_code']
    
    def __str__(self):
        return f"{self.course_code} - {self.name}"
    
    def save(self, *args, **kwargs):
        if self.teacher and self.teacher.institute != self.institute:
            raise ValueError("Teacher must belong to the same institute")
        super().save(*args, **kwargs)

class Enrollment(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student} - {self.course}"