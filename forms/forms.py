from django import forms
from django.forms import formset_factory
from .models import FormQuestion


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
        fields = ['text', 'question_type', 'order', 'is_required', 'image']
        widgets = {
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
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['text'].help_text = "The question that will be displayed to users"
        self.fields['question_type'].help_text = "Select the type of input for this question"
        self.fields['order'].help_text = "Display order (0 = first)"
        self.fields['is_required'].help_text = "Make this question mandatory"
        self.fields['image'].help_text = "Optional image to display with the question"
        
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