from django.db import models
from institutes.models import Institute
from authentication.models import User

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='teachers')
    employee_id = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    joining_date = models.DateField(auto_now_add=True)
    specialization = models.CharField(max_length=200, blank=True)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15)
    
    class Meta:
        unique_together = ['institute', 'employee_id']
        ordering = ['employee_id']
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        self.user.role = 'teacher'
        self.user.institute = self.institute
        self.user.is_approved = True
        self.user.save()
        super().save(*args, **kwargs)