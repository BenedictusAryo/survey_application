from django import forms
from django.forms import formset_factory
from .models import Form, FormQuestion, FormSection


class FormSectionForm(forms.ModelForm):
    """Form for creating/editing form sections"""
    
    class Meta:
        model = FormSection
        fields = ['title', 'description', 'order', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Section title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Section description (can include URLs and HTML)...'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'min': 0
            }),
            'image': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['title'].help_text = "Title for this section"
        self.fields['description'].help_text = "Description can include URLs and basic HTML formatting"
        self.fields['order'].help_text = "Display order (0 = first)"
        self.fields['image'].help_text = "Optional header image for the section"


class QuestionOptionForm(forms.Form):
    """Form for individual question options"""
    text = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Option text'
        })
    )
    value = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Option value (optional)'
        }),
        required=False
    )
    
    def clean_value(self):
        value = self.cleaned_data.get('value')
        text = self.cleaned_data.get('text')
        # If no value provided, use text as value
        return value if value else text


class FormQuestionForm(forms.ModelForm):
    """Enhanced form for creating/editing questions with dynamic options"""
    
    class Meta:
        model = FormQuestion
        fields = ['section', 'text', 'question_type', 'order', 'is_required', 'image']
        widgets = {
            'section': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'id': 'id_section'
            }),
            'text': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Enter your question here...'
            }),
            'question_type': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'id': 'id_question_type'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'min': 0
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'image': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        # Extract form instance if passed
        form_instance = kwargs.pop('form_instance', None)
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['section'].help_text = "Optional section to group this question"
        self.fields['text'].help_text = "The question that will be displayed to users"
        self.fields['question_type'].help_text = "Select the type of input for this question"
        self.fields['order'].help_text = "Display order (0 = first)"
        self.fields['is_required'].help_text = "Make this question mandatory"
        self.fields['image'].help_text = "Optional image to display with the question"
        
        # Make section optional
        self.fields['section'].required = False
        self.fields['section'].empty_label = "No section (ungrouped)"
        
        # Filter sections to only show those from the current form
        if form_instance:
            self.fields['section'].queryset = FormSection.objects.filter(form=form_instance).order_by('order')
        elif self.instance and self.instance.pk and self.instance.form:
            self.fields['section'].queryset = FormSection.objects.filter(form=self.instance.form).order_by('order')
        else:
            self.fields['section'].queryset = FormSection.objects.none()
        
        # If editing existing question, load options for dynamic fields
        if self.instance and self.instance.pk and self.instance.options:
            # Store options for frontend processing
            self.existing_options = self.instance.options
        else:
            self.existing_options = []

    def clean(self):
        cleaned_data = super().clean()
        
        # For now, we'll handle options processing in the view
        # since we're using dynamic JavaScript forms
        
        return cleaned_data


# Formset for dynamic options
QuestionOptionFormSet = formset_factory(
    QuestionOptionForm,
    extra=2,  # Start with 2 empty option forms
    can_delete=True,
    min_num=0,
    validate_min=False
)


class FormEditForm(forms.ModelForm):
    """Form for editing form details"""
    
    class Meta:
        model = Form
        fields = [
            'title', 'description', 'password', 'require_captcha', 
            'form_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Form title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Describe what this form is for...'
            }),
            'password': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Optional password protection',
                'type': 'password'
            }),
            'require_captcha': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'form_image': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*'
            }),
        }
    
    # Additional settings fields
    unique_entries = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        help_text="Prevent duplicate submissions from the same user"
    )
    
    enable_identity = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        help_text="Collect identity information (name, phone, etc.)"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['title'].help_text = "The title that will be displayed to users"
        self.fields['description'].help_text = "A brief description of the form's purpose"
        self.fields['password'].help_text = "Leave blank for no password protection"
        self.fields['password'].required = False
        self.fields['require_captcha'].help_text = "Helps prevent spam submissions"
        self.fields['require_captcha'].required = False  # Allow unchecking
        self.fields['form_image'].help_text = "Header image for the form (optional)"
        self.fields['form_image'].required = False
        
        # Load settings from form_settings JSON field
        if self.instance and self.instance.pk:
            if self.instance.form_settings:
                settings = self.instance.form_settings
                self.fields['unique_entries'].initial = settings.get('unique_entries', False)
                self.fields['enable_identity'].initial = settings.get('enable_identity', True)
    
    def clean_password(self):
        """Handle password field - keep existing if empty"""
        password = self.cleaned_data.get('password')
        # If password is empty and we're editing an existing form, keep the old password
        if not password and self.instance and self.instance.pk:
            return self.instance.password
        return password
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Save additional settings to form_settings JSON field
        if not instance.form_settings:
            instance.form_settings = {}
        
        instance.form_settings.update({
            'unique_entries': self.cleaned_data.get('unique_entries', False),
            'enable_identity': self.cleaned_data.get('enable_identity', True),
        })
        
        if commit:
            instance.save()
        
        return instance
        return instance