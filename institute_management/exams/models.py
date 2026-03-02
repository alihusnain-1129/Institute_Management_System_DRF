from django.db import models
from courses.models import Course

class Exam(models.Model):
    EXAM_TYPE_CHOICES = (
        ('midterm', 'Mid Term'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    pass_marks = models.DecimalField(max_digits=5, decimal_places=2)
    exam_date = models.DateField()
    duration_minutes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-exam_date', 'course']
    
    def __str__(self):
        return f"{self.course.course_code} - {self.title}"

class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2, blank=True)
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    entered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['exam', 'student']
        ordering = ['-entered_at']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.exam.title} - {self.marks_obtained}"
    
    def save(self, *args, **kwargs):
        # Calculate grade based on marks
        percentage = (self.marks_obtained / self.exam.total_marks) * 100
        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B'
        elif percentage >= 60:
            self.grade = 'C'
        elif percentage >= 50:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)