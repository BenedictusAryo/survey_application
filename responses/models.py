from django.db import models
from django.conf import settings as django_settings

class Response(models.Model):
    """A response to a published form"""
    
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='responses')
    record = models.ForeignKey(
        'master_data.MasterDataRecord', 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        help_text="Associated master data record (for identity)"
    )
    
    # User info (for logged-in users)
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True
    )
    
    # Session tracking for anonymous users
    session_key = models.CharField(max_length=40, blank=True)
    
    # Status tracking
    is_complete = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # IP and user agent for tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # New identity data (when user selects "Other")
    is_new_identity = models.BooleanField(
        default=False,
        help_text="True if this response includes new identity data not in master data"
    )
    new_identity_data = models.JSONField(
        null=True, blank=True,
        help_text="New identity information when 'Other' is selected (not yet added to master data)"
    )
    new_identity_dataset_id = models.IntegerField(
        null=True, blank=True,
        help_text="ID of the dataset this new identity belongs to"
    )
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        identifier = ""
        if self.record:
            identifier = f" ({self.record})"
        elif self.user:
            identifier = f" ({self.user.username})"
        
        return f"Response to {self.form.title}{identifier}"


class ResponseAnswer(models.Model):
    """Individual answer within a response"""
    
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('forms.FormQuestion', on_delete=models.CASCADE)
    value = models.JSONField()  # Flexible storage for different answer types
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"{self.response} - {self.question.text[:30]}..."
