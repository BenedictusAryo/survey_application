from django.db import models
from django.conf import settings as django_settings
from django.utils.text import slugify
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
# ...existing code...

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
    
    # Security settings
    password = models.CharField(max_length=100, blank=True, help_text="Optional password to protect the form")
    require_captcha = models.BooleanField(default=True, help_text="Require captcha for submissions")
    
    # Settings stored as JSON
    form_settings = models.JSONField(default=dict)  # For unique_entries, enable_identity, etc.
    
    # Form image/logo
    form_image = models.ImageField(upload_to='form_images/', blank=True, null=True, help_text="Header image for the form")
    
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
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        # Use localhost for development, production domain for production
        form_url = f"http://localhost:8000/survey/{self.slug}/"
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
    # List of column names from the dataset that should be hidden when this
    # dataset is used in the context of this form. Stored as a JSON list.
    hidden_columns = models.JSONField(default=list, blank=True)
    # Column name to use for displaying records in dropdowns
    display_column = models.CharField(max_length=100, blank=True, null=True, 
                                     help_text="Column to use for displaying records in dropdowns")
    # List of column names to use as filters (in order) before showing the final selection
    filter_columns = models.JSONField(default=list, blank=True,
                                     help_text="Columns to use as cascading filters (e.g., ['Wilayah', 'Lingkungan'])")
    
    class Meta:
        ordering = ['order']
        unique_together = ['form', 'dataset']

    def get_visible_columns(self):
        """Return the dataset's columns excluding any hidden columns for this attachment."""
        hidden = set(self.hidden_columns or [])
        return [c for c in self.dataset.columns.all() if c.name not in hidden]
    
    def get_record_display_value(self, record):
        """Get the display value for a record based on the configured display column."""
        if self.display_column and self.display_column in record.data:
            return record.data[self.display_column]
        
        # Fallback: try to find a name-like column
        for column in self.dataset.columns.all():
            if 'nama' in column.name.lower() or 'name' in column.name.lower():
                if column.name in record.data:
                    return record.data[column.name]
        
        # Last resort: return record ID
        return f"Record #{record.id}"
    
    def get_filter_values(self, filter_column):
        """Get unique values for a specific filter column."""
        values = set()
        for record in self.dataset.records.all():
            if filter_column in record.data and record.data[filter_column]:
                values.add(record.data[filter_column])
        return sorted(list(values))
    
    def get_filtered_records(self, filter_values=None):
        """Get records filtered by the specified filter values."""
        records = self.dataset.records.all()
        
        if filter_values and self.filter_columns:
            for i, filter_column in enumerate(self.filter_columns):
                if i < len(filter_values) and filter_values[i]:
                    records = records.filter(
                        data__icontains={filter_column: filter_values[i]}
                    )
        
        return records


class FormSection(models.Model):
    """Sections within a form to group questions"""
    
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Description can include URLs and HTML")
    order = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='section_images/', blank=True, null=True,
                             help_text="Optional image for the section header")
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['form', 'order']
    
    def __str__(self):
        return f"{self.form.title} - Section {self.order}: {self.title}"


class FormQuestion(models.Model):
    """Questions within a form"""
    
    QUESTION_TYPES = [
        ('single_select', 'Single Select'),
        ('multi_select', 'Multi Select'),
        ('text_input', 'Text Input'),
        ('numeric_input', 'Numeric Input'),
        ('date_input', 'Date Input'),
        ('image_prompt', 'Image Prompt'),
        ('image_select', 'Image Select (choose from image options)'),
    ]
    
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions')
    section = models.ForeignKey(FormSection, on_delete=models.CASCADE, related_name='questions', 
                               blank=True, null=True, help_text="Optional section to group this question")
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    options = models.JSONField(default=list)  # For select options, can include image URLs
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    
    # Conditional logic
    logic = models.JSONField(default=dict)  # Show/hide conditions
    
    # Image for the question itself
    image = models.ImageField(upload_to='question_images/', blank=True, null=True, 
                             help_text="Image to display with the question")
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.form.title} - Q{self.order}: {self.text[:50]}"


class QuestionOption(models.Model):
    """Individual option for select questions, supporting images"""
    
    question = models.ForeignKey(FormQuestion, on_delete=models.CASCADE, related_name='option_images')
    text = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    image = models.ImageField(upload_to='option_images/', blank=True, null=True,
                             help_text="Optional image for this option")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['question', 'value']
    
    def __str__(self):
        return f"{self.question} - {self.text}"
