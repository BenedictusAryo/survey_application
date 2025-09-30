"""
Test script to verify the improved question form functionality
"""
import os
import django
import sys

# Add the project directory to the path
sys.path.append('c:/Users/Benedict/Documents/survey_application')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_project.settings')
django.setup()

from forms.models import Form, FormQuestion
from accounts.models import User

def test_question_creation():
    """Test creating questions with different types"""
    print("Testing question creation functionality...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Get or create a test form
    form, created = Form.objects.get_or_create(
        title='Test Form',
        defaults={
            'description': 'Test form for question functionality',
            'owner': user,
            'slug': 'test-form'
        }
    )
    
    print(f"Using form: {form.title} (ID: {form.id})")
    
    # Test 1: Text input question (should not require options)
    text_question = FormQuestion.objects.create(
        form=form,
        text='What is your name?',
        question_type='text_input',
        order=1,
        is_required=True,
        options=[]  # Should be empty for text input
    )
    print(f"✓ Created text input question: {text_question.text}")
    print(f"  Options: {text_question.options}")
    
    # Test 2: Single select question (should have options)
    single_select_question = FormQuestion.objects.create(
        form=form,
        text='What is your favorite color?',
        question_type='single_select',
        order=2,
        is_required=False,
        options=[
            {'text': 'Red', 'value': 'red'},
            {'text': 'Blue', 'value': 'blue'},
            {'text': 'Green', 'value': 'green'}
        ]
    )
    print(f"✓ Created single select question: {single_select_question.text}")
    print(f"  Options: {single_select_question.options}")
    
    # Test 3: Multi select question (should have options)
    multi_select_question = FormQuestion.objects.create(
        form=form,
        text='Which programming languages do you know?',
        question_type='multi_select',
        order=3,
        is_required=False,
        options=[
            {'text': 'Python', 'value': 'python'},
            {'text': 'JavaScript', 'value': 'javascript'},
            {'text': 'Java', 'value': 'java'},
            {'text': 'C++', 'value': 'cpp'}
        ]
    )
    print(f"✓ Created multi select question: {multi_select_question.text}")
    print(f"  Options: {multi_select_question.options}")
    
    # Test 4: Numeric input question (should not require options)
    numeric_question = FormQuestion.objects.create(
        form=form,
        text='What is your age?',
        question_type='numeric_input',
        order=4,
        is_required=True,
        options=[]  # Should be empty for numeric input
    )
    print(f"✓ Created numeric input question: {numeric_question.text}")
    print(f"  Options: {numeric_question.options}")
    
    print(f"\nTotal questions in form: {form.questions.count()}")
    
    # Display question types that require options
    option_required_types = ['single_select', 'multi_select', 'image_select']
    print(f"\nQuestion types that require options: {option_required_types}")
    
    # Verify the logic
    for question in form.questions.all():
        requires_options = question.question_type in option_required_types
        has_options = bool(question.options)
        
        status = "✓ Correct" if (requires_options == has_options) else "✗ Issue"
        print(f"{status}: {question.question_type} - Requires options: {requires_options}, Has options: {has_options}")
    
    print("\nForm URL for testing: http://localhost:8000/forms/{}/questions/add/".format(form.id))
    print("Edit question URL example: http://localhost:8000/forms/questions/{}/edit/".format(text_question.id))

if __name__ == "__main__":
    test_question_creation()