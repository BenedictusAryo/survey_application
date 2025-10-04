"""
Management command to FORCE regenerate QR codes by deleting old files first.
This ensures old cached QR codes are completely removed.

Usage:
    python manage.py force_regenerate_qr
    python manage.py force_regenerate_qr --form-id 1
"""

from django.core.management.base import BaseCommand
from forms.models import Form
import os


class Command(BaseCommand):
    help = 'Force regenerate QR codes by deleting old files first (fixes caching issues)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--form-id',
            type=int,
            help='Force regenerate QR code for a specific form ID only',
        )

    def handle(self, *args, **options):
        form_id = options.get('form_id')
        
        if form_id:
            # Force regenerate for specific form
            try:
                form = Form.objects.get(pk=form_id)
                if form.status != 'published':
                    self.stdout.write(
                        self.style.WARNING(f'Form "{form.title}" (ID: {form.pk}) is not published. Skipping.')
                    )
                    return
                
                self._force_regenerate_qr(form)
                
            except Form.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Form with ID {form_id} does not exist.')
                )
        else:
            # Force regenerate for all published forms
            published_forms = Form.objects.filter(status='published')
            count = published_forms.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.WARNING('No published forms found.')
                )
                return
            
            self.stdout.write(f'Found {count} published form(s). Force regenerating QR codes...')
            
            for form in published_forms:
                self._force_regenerate_qr(form)
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Successfully force regenerated {count} QR code(s)!')
            )

    def _force_regenerate_qr(self, form):
        """Force regenerate QR code for a single form"""
        old_qr_path = None
        
        # Get the old QR code path
        if form.qr_code and form.qr_code.name:
            old_qr_path = form.qr_code.path
            self.stdout.write(f'  • Old QR code: {form.qr_code.name}')
        
        # Delete the old QR code file from database and filesystem
        if form.qr_code:
            try:
                form.qr_code.delete(save=False)
                self.stdout.write(f'  • Deleted old QR code from database')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Could not delete from database: {e}')
                )
        
        # Double-check: delete physical file if it still exists
        if old_qr_path and os.path.exists(old_qr_path):
            try:
                os.remove(old_qr_path)
                self.stdout.write(f'  • Deleted physical file: {old_qr_path}')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Could not delete physical file: {e}')
                )
        
        # Clear the qr_code field and save
        form.qr_code = None
        form.save(update_fields=['qr_code'])
        
        # Generate new QR code
        form.generate_qr_code()
        
        # Verify the new QR code
        if form.qr_code and form.qr_code.name:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ Generated NEW QR code for "{form.title}" (ID: {form.pk})\n'
                    f'    New file: {form.qr_code.name}'
                )
            )
            
            # Show what URL is encoded
            from django.conf import settings
            from django.urls import reverse
            survey_path = reverse('responses:public_survey', kwargs={'slug': form.slug})
            form_url = f"{settings.SITE_URL}{survey_path}"
            self.stdout.write(f'    Encoded URL: {form_url}')
        else:
            self.stdout.write(
                self.style.ERROR(f'  ✗ Failed to generate QR code for "{form.title}"')
            )
