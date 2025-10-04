"""
Management command to duplicate a form with all its related data.
Creates a copy of the form with the same owner, including sections, questions, 
options, master data attachments, and collaborations.

Usage:
    python manage.py duplicate_form --form-id 1
    python manage.py duplicate_form --form-id 1 --title "Copy of My Survey"
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.files.base import ContentFile
from forms.models import Form, FormSection, FormQuestion, QuestionOption, FormMasterDataAttachment, FormCollaboration
import uuid
import os
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Duplicate a form with all its related data (sections, questions, options, master data attachments, and collaborations)'

    def copy_image_file(self, image_field):
        """
        Create a physical copy of an image file.
        Returns the new file to be saved to an ImageField.
        """
        if not image_field or not image_field.name:
            return None
        
        try:
            # Read the original file
            image_field.open()
            file_content = image_field.read()
            image_field.close()
            
            # Get the original filename and create a new unique name
            original_name = os.path.basename(image_field.name)
            name_parts = os.path.splitext(original_name)
            new_name = f"{name_parts[0]}_copy_{uuid.uuid4().hex[:8]}{name_parts[1]}"
            
            # Create a new file object
            return ContentFile(file_content, name=new_name)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  ⚠ Could not copy image {image_field.name}: {str(e)}')
            )
            return None

    def add_arguments(self, parser):
        parser.add_argument(
            '--form-id',
            type=int,
            required=True,
            help='ID of the form to duplicate',
        )
        parser.add_argument(
            '--title',
            type=str,
            help='Title for the duplicated form (default: "Copy of [original title]")',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        form_id = options['form_id']
        new_title = options.get('title')
        
        # Get the original form
        try:
            original_form = Form.objects.get(pk=form_id)
        except Form.DoesNotExist:
            raise CommandError(f'Form with ID {form_id} does not exist.')
        
        self.stdout.write(f'Duplicating form "{original_form.title}" (ID: {original_form.pk})...')
        
        # Set the new title
        if not new_title:
            new_title = f"Copy of {original_form.title}"
        
        # Generate a unique slug that fits within 50 characters
        # Reserve 9 characters for the UUID part ("-" + 8 chars)
        base_slug = slugify(new_title)[:41]  # Max 41 chars for base
        unique_suffix = str(uuid.uuid4())[:8]
        new_slug = f"{base_slug}-{unique_suffix}"
        
        # Create a new form (duplicate)
        new_form = Form.objects.create(
            title=new_title,
            description=original_form.description,
            slug=new_slug,
            owner=original_form.owner,
            status='draft',  # Always start as draft
            password=original_form.password,
            require_captcha=original_form.require_captcha,
            form_settings=original_form.form_settings.copy() if original_form.form_settings else {},
        )
        
        # Copy form image if it exists
        if original_form.form_image:
            copied_image = self.copy_image_file(original_form.form_image)
            if copied_image:
                new_form.form_image.save(copied_image.name, copied_image, save=True)
        
        self.stdout.write(f'  ✓ Created new form "{new_form.title}" (ID: {new_form.pk})')
        
        # Copy master data attachments
        master_data_count = 0
        for attachment in original_form.master_data_attachments.all():
            FormMasterDataAttachment.objects.create(
                form=new_form,
                dataset=attachment.dataset,
                order=attachment.order,
                hidden_columns=attachment.hidden_columns.copy() if attachment.hidden_columns else [],
                display_column=attachment.display_column,
                filter_columns=attachment.filter_columns.copy() if attachment.filter_columns else [],
            )
            master_data_count += 1
        
        if master_data_count > 0:
            self.stdout.write(f'  ✓ Copied {master_data_count} master data attachment(s)')
        
        # Copy sections
        section_mapping = {}  # Map old section ID to new section
        section_count = 0
        for section in original_form.sections.all():
            new_section = FormSection.objects.create(
                form=new_form,
                title=section.title,
                description=section.description,
                order=section.order,
            )
            
            # Copy section image if it exists
            if section.image:
                copied_image = self.copy_image_file(section.image)
                if copied_image:
                    new_section.image.save(copied_image.name, copied_image, save=True)
            
            section_mapping[section.id] = new_section
            section_count += 1
        
        if section_count > 0:
            self.stdout.write(f'  ✓ Copied {section_count} section(s)')
        
        # Copy questions
        question_count = 0
        for question in original_form.questions.all():
            new_section = section_mapping.get(question.section_id) if question.section_id else None
            
            new_question = FormQuestion.objects.create(
                form=new_form,
                section=new_section,
                text=question.text,
                question_type=question.question_type,
                options=question.options.copy() if question.options else [],
                order=question.order,
                is_required=question.is_required,
                logic=question.logic.copy() if question.logic else {},
            )
            
            # Copy question image if it exists
            if question.image:
                copied_image = self.copy_image_file(question.image)
                if copied_image:
                    new_question.image.save(copied_image.name, copied_image, save=True)
            
            # Copy question options (if any)
            option_count = 0
            for option in question.option_images.all():
                new_option = QuestionOption.objects.create(
                    question=new_question,
                    text=option.text,
                    value=option.value,
                    order=option.order,
                )
                
                # Copy option image if it exists
                if option.image:
                    copied_image = self.copy_image_file(option.image)
                    if copied_image:
                        new_option.image.save(copied_image.name, copied_image, save=True)
                
                option_count += 1
            
            question_count += 1
        
        if question_count > 0:
            self.stdout.write(f'  ✓ Copied {question_count} question(s)')
        
        # Copy collaborations (editors)
        collaboration_count = 0
        for collaboration in FormCollaboration.objects.filter(form=original_form):
            FormCollaboration.objects.create(
                form=new_form,
                user=collaboration.user,
            )
            collaboration_count += 1
        
        if collaboration_count > 0:
            self.stdout.write(f'  ✓ Copied {collaboration_count} collaboration(s)')
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully duplicated form!'
                f'\n  Original: "{original_form.title}" (ID: {original_form.pk})'
                f'\n  New Copy: "{new_form.title}" (ID: {new_form.pk})'
                f'\n  Owner: {new_form.owner.username}'
                f'\n  Status: {new_form.status}'
                f'\n  URL Slug: {new_form.slug}'
            )
        )
