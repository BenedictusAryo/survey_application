from django.core.management.base import BaseCommand
from forms.models import Form


class Command(BaseCommand):
    help = 'Fix question ordering for admin interface and data consistency (published forms use display sequence automatically)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--form-id',
            type=int,
            help='Fix ordering for a specific form ID only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        if options['form_id']:
            forms = Form.objects.filter(id=options['form_id'])
        else:
            forms = Form.objects.all()

        total_forms = forms.count()
        total_questions_updated = 0

        self.stdout.write(f"Processing {total_forms} form(s)...")

        for form in forms:
            questions = form.questions.order_by('id')  # Order by creation time
            questions_updated = 0
            
            self.stdout.write(f"\nForm: {form.title} (ID: {form.id})")
            self.stdout.write(f"  Questions: {questions.count()}")
            
            for i, question in enumerate(questions, 1):
                old_order = question.order
                new_order = i
                
                if old_order != new_order:
                    self.stdout.write(
                        f"  Q{question.id}: '{question.text[:50]}...' order {old_order} -> {new_order}"
                    )
                    
                    if not options['dry_run']:
                        question.order = new_order
                        question.save(update_fields=['order'])
                    
                    questions_updated += 1
                else:
                    self.stdout.write(
                        f"  Q{question.id}: '{question.text[:50]}...' order {old_order} (no change)"
                    )
            
            if questions_updated > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"  Updated {questions_updated} question(s)")
                )
                total_questions_updated += questions_updated
            else:
                self.stdout.write("  No changes needed")

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f"\nDRY RUN: {total_questions_updated} question(s) would be updated")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\nCompleted: {total_questions_updated} question(s) updated")
            )