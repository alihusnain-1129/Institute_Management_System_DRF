from django.contrib.auth.models import AbstractUser , UserManager
from django.db import models

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and return a superuser with super_admin role."""
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('role') != 'super_admin':
            raise ValueError('Superuser must have role=super_admin.')
        
        return self._create_user(username, email, password, **extra_fields)
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and return a regular user."""
        extra_fields.setdefault('is_approved', False)
        extra_fields.setdefault('role', 'student')
        return super().create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('institute_admin', 'Institute Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    institute = models.ForeignKey('institutes.Institute', on_delete=models.CASCADE, 
                                 null=True, blank=True, related_name='users')
    phone = models.CharField(max_length=15, blank=True)
    is_approved = models.BooleanField(default=False)

    # Use custom manager
    objects = CustomUserManager()
    
    def __str__(self):
        return f"{self.username} - {self.role}"
    
    def save(self, *args, **kwargs):
        # Auto-set role and approval for superusers
        if self.is_superuser or self.is_staff:
            self.role = 'super_admin'
            self.is_approved = True
        
        super().save(*args, **kwargs)