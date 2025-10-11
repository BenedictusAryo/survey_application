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
    
    def get_respondent_display(self):
        """Get the display value for the respondent based on configured display column"""
        if self.user:
            return self.user.username
        elif self.record:
            # Get the FormMasterDataAttachment for this response's record
            try:
                attachment = self.form.master_data_attachments.get(dataset=self.record.dataset)
                return attachment.get_record_display_value(self.record)
            except Exception:
                # Fallback to record's __str__ method
                return str(self.record)
        elif self.is_new_identity and self.new_identity_data:
            # For new identities, try to get the display column from the dataset attachment
            try:
                attachment = self.form.master_data_attachments.get(dataset_id=self.new_identity_dataset_id)
                if attachment.display_column and attachment.display_column in self.new_identity_data:
                    return self.new_identity_data[attachment.display_column]
            except Exception:
                pass
            # Fallback: return all values
            return ', '.join(str(v) for v in self.new_identity_data.values() if v)
        return "Anonymous"
    
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
