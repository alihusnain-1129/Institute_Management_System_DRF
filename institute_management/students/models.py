from django.db import models
from institutes.models import Institute
from authentication.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='students')
    roll_number = models.CharField(max_length=50)
    enrollment_date = models.DateField(auto_now_add=True)
    date_of_birth = models.DateField()
    address = models.TextField()
    parent_name = models.CharField(max_length=255)
    parent_phone = models.CharField(max_length=15)
    
    class Meta:
        unique_together = ['institute', 'roll_number']
        ordering = ['roll_number']
    
    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        self.user.role = 'student'
        self.user.institute = self.institute
        self.user.save()
        super().save(*args, **kwargs)