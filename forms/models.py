from django.db import models
from django.conf import settings as django_settings
from django.utils.text import slugify
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

class Form(models.Model):
    """Survey form that can be published and shared"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    owner = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_forms')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Settings stored as JSON
    form_settings = models.JSONField(default=dict)  # Renamed to avoid conflict
    
    # QR Code
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    # Collaboration
    editors = models.ManyToManyField(
        django_settings.AUTH_USER_MODEL,
        through='FormCollaboration',
        related_name='collaborative_forms'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + '-' + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
        
        # Generate QR code if published and doesn't have one
        if self.status == 'published' and not self.qr_code:
            self.generate_qr_code()
    
    def generate_qr_code(self):
        """Generate QR code for the form URL"""
        from django.urls import reverse
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        # In production, use actual domain
        form_url = f"http://survey.parokibintaro.org/survey/{self.slug}/"
        qr.add_data(form_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.slug}.png'
        
        self.qr_code.save(filename, File(buffer), save=False)
        self.save(update_fields=['qr_code'])
    
    def __str__(self):
        return self.title


class FormCollaboration(models.Model):
    """Collaboration relationship for forms"""
    
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    invited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['form', 'user']


class FormMasterDataAttachment(models.Model):
    """Attachment of master data sets to forms"""
    
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='master_data_attachments')
    dataset = models.ForeignKey('master_data.MasterDataSet', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['form', 'dataset']


class FormQuestion(models.Model):
    """Questions within a form"""
    
    QUESTION_TYPES = [
        ('single_select', 'Single Select'),
        ('multi_select', 'Multi Select'),
        ('text_input', 'Text Input'),
        ('numeric_input', 'Numeric Input'),
        ('date_input', 'Date Input'),
        ('image_prompt', 'Image Prompt'),
    ]
    
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    options = models.JSONField(default=list)  # For select options
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    
    # Conditional logic
    logic = models.JSONField(default=dict)  # Show/hide conditions
    
    # Image for image prompts
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.form.title} - Q{self.order}: {self.text[:50]}"
