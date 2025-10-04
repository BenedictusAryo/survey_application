"""
Management command to regenerate QR codes for all published forms.
This is useful after updating the SITE_URL configuration.

Usage:
    python manage.py regenerate_qr_codes
    python manage.py regenerate_qr_codes --form-id 1
"""

from django.core.management.base import BaseCommand
from forms.models import Form


class Command(BaseCommand):
    help = 'Regenerate QR codes for published forms with the correct SITE_URL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--form-id',
            type=int,
            help='Regenerate QR code for a specific form ID only',
        )

    def handle(self, *args, **options):
        form_id = options.get('form_id')
        
        if form_id:
            # Regenerate for specific form
            try:
                form = Form.objects.get(pk=form_id)
                if form.status != 'published':
                    self.stdout.write(
                        self.style.WARNING(f'Form "{form.title}" (ID: {form.pk}) is not published. Skipping.')
                    )
                    return
                
                # Delete old QR code and regenerate
                if form.qr_code:
                    form.qr_code.delete(save=False)
                form.generate_qr_code()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully regenerated QR code for form "{form.title}" (ID: {form.pk})')
                )
            except Form.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Form with ID {form_id} does not exist.')
                )
        else:
            # Regenerate for all published forms
            published_forms = Form.objects.filter(status='published')
            count = published_forms.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.WARNING('No published forms found.')
                )
                return
            
            self.stdout.write(f'Found {count} published form(s). Regenerating QR codes...')
            
            for form in published_forms:
                # Delete old QR code and regenerate
                if form.qr_code:
                    form.qr_code.delete(save=False)
                form.generate_qr_code()
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Regenerated QR code for "{form.title}" (ID: {form.pk})')
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully regenerated {count} QR code(s)!')
            )
