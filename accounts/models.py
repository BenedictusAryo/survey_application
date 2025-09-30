from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Extended User model with role-based permissions"""
    
    ROLE_CHOICES = [
        ('administrator', 'Administrator'),
        ('form_creator', 'Form Creator'),
        ('editor', 'Editor'),
        ('respondent', 'Respondent'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='form_creator')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_administrator(self):
        return self.role == 'administrator'
    
    def is_form_creator(self):
        return self.role in ['administrator', 'form_creator']
    
    def is_editor(self):
        return self.role in ['administrator', 'form_creator', 'editor']
