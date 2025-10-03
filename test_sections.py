"""
Test script to verify the section functionality
"""
import os
import django
import sys

# Add the project directory to the path
sys.path.append('c:/Users/Benedict/Documents/survey_application')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_project.settings')
django.setup()

from forms.models import Form, FormSection, FormQuestion
from accounts.models import User

def test_section_functionality():
    """Test creating sections and questions with sections"""
    print("Testing section functionality...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser_sections',
        defaults={'email': 'test_sections@example.com'}
    )
    
    # Get or create a test form
    form, created = Form.objects.get_or_create(
        title='Test Form with Sections',
        defaults={
            'description': 'Test form for section functionality',
            'owner': user,
            'slug': 'test-form-sections'
        }
    )
    
    print(f"Using form: {form.title} (ID: {form.id})")
    
    # Create sections
    section1, created = FormSection.objects.get_or_create(
        form=form,
        title='Personal Information',
        defaults={
            'description': 'Please provide your basic <b>personal details</b>. Visit <a href="https://example.com">our privacy policy</a> for more info.',
            'order': 1
        }
    )
    print(f"✓ Created section 1: {section1.title}")
    
    section2, created = FormSection.objects.get_or_create(
        form=form,
        title='Preferences',
        defaults={
            'description': 'Tell us about your preferences and interests.',
            'order': 2
        }
    )
    print(f"✓ Created section 2: {section2.title}")
    
    # Create questions in sections
    question1, created = FormQuestion.objects.get_or_create(
        form=form,
        section=section1,
        text='What is your full name?',
        defaults={
            'question_type': 'text_input',
            'order': 1,
            'is_required': True,
            'options': []
        }
    )
    print(f"✓ Created question in section 1: {question1.text}")
    
    question2, created = FormQuestion.objects.get_or_create(
        form=form,
        section=section1,
        text='What is your age?',
        defaults={
            'question_type': 'numeric_input',
            'order': 2,
            'is_required': True,
            'options': []
        }
    )
    print(f"✓ Created question in section 1: {question2.text}")
    
    question3, created = FormQuestion.objects.get_or_create(
        form=form,
        section=section2,
        text='What is your favorite color?',
        defaults={
            'question_type': 'single_select',
            'order': 3,
            'is_required': False,
            'options': [
                {'text': 'Red', 'value': 'red'},
                {'text': 'Blue', 'value': 'blue'},
                {'text': 'Green', 'value': 'green'},
                {'text': 'Yellow', 'value': 'yellow'}
            ]
        }
    )
    print(f"✓ Created question in section 2: {question3.text}")
    
    # Create an ungrouped question
    question4, created = FormQuestion.objects.get_or_create(
        form=form,
        section=None,  # No section
        text='Any additional comments?',
        defaults={
            'question_type': 'text_input',
            'order': 4,
            'is_required': False,
            'options': []
        }
    )
    print(f"✓ Created ungrouped question: {question4.text}")
    
    # Display structure
    print(f"\nForm structure:")
    print(f"Form: {form.title}")
    print(f"Total sections: {form.sections.count()}")
    print(f"Total questions: {form.questions.count()}")
    
    print("\nSections:")
    for section in form.sections.all():
        print(f"  - {section.title} (Order: {section.order})")
        print(f"    Description: {section.description}")
        print(f"    Questions: {section.questions.count()}")
        for question in section.questions.all():
            print(f"      • {question.text} ({question.get_question_type_display()})")
    
    print("\nUngrouped questions:")
    ungrouped = form.questions.filter(section__isnull=True)
    for question in ungrouped:
        print(f"  • {question.text} ({question.get_question_type_display()})")
    
    print(f"\nForm management URL: http://localhost:8000/forms/{form.id}/")
    print(f"Questions management URL: http://localhost:8000/forms/{form.id}/questions/")
    
    # Try to publish the form
    if form.status != 'published':
        form.status = 'published'
        form.save()
        print(f"✓ Form published")
    
    print(f"Public form URL: http://localhost:8000/survey/{form.slug}/")
    

if __name__ == "__main__":
    test_section_functionality()