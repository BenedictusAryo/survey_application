
from collections import Counter
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db import models, transaction
from django.views.decorators.http import require_http_methods
import json
from django.utils.text import slugify
 
from .models import Form, FormQuestion, FormMasterDataAttachment, FormSection
from .forms import FormQuestionForm, FormEditForm, FormSectionForm

class FormListView(LoginRequiredMixin, ListView):
    model = Form
    template_name = 'forms/list.html'
    context_object_name = 'forms'
    
    def get_queryset(self):
        return Form.objects.filter(owner=self.request.user)

class FormCreateView(LoginRequiredMixin, CreateView):
    model = Form
    fields = ['title', 'description']
    template_name = 'forms/create.html'
    success_url = reverse_lazy('forms:list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f'Form "{form.instance.title}" created successfully!')
        return super().form_valid(form)

class FormDetailView(LoginRequiredMixin, DetailView):
    model = Form
    template_name = 'forms/detail.html'
    context_object_name = 'form'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_obj = self.object
        
        # Get attached master data sets
        context['master_data_attachments'] = form_obj.master_data_attachments.select_related('dataset').all()
        
        # Get sections and questions organized by section
        sections = form_obj.sections.all()
        questions_without_section = form_obj.questions.filter(section__isnull=True).all()
        
        context['sections'] = sections
        context['questions_without_section'] = questions_without_section
        context['questions'] = form_obj.questions.all()
        
        # Get response count
        context['response_count'] = form_obj.responses.count()
        
        # Get collaborators
        context['collaborators'] = form_obj.editors.all()
        
        return context

class FormEditView(LoginRequiredMixin, UpdateView):
    model = Form
    form_class = FormEditForm
    template_name = 'forms/edit.html'
    context_object_name = 'form'
    
    def get_queryset(self):
        # Ensure user can only edit their own forms or forms they collaborate on
        return Form.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(editors=self.request.user)
        ).distinct()
    
    def form_valid(self, form):
        messages.success(self.request, f'Form "{form.instance.title}" updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the form. Please check the fields below.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('forms:detail', kwargs={'pk': self.object.pk})

class FormDeleteView(LoginRequiredMixin, View):
    """View to handle form deletion"""
    
    def get(self, request, pk):
        """Display the delete confirmation page"""
        form = get_object_or_404(Form, pk=pk, owner=request.user)
        
        context = {
            'form': form,
            'response_count': form.responses.count(),
            'questions': form.questions.all(),
        }
        
        return render(request, 'forms/delete_confirm.html', context)
    
    def post(self, request, pk):
        """Handle form deletion"""
        form = get_object_or_404(Form, pk=pk, owner=request.user)
        form_title = form.title
        
        # Delete the form (cascade will handle related objects)
        form.delete()
        
        messages.success(request, f'Form "{form_title}" has been deleted successfully.')
        return redirect('forms:list')

class FormQuestionEditView(LoginRequiredMixin, DetailView):
    model = Form
    template_name = 'forms/questions.html'
    context_object_name = 'form'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_obj = self.object
        
        # Get sections with their questions
        sections = form_obj.sections.prefetch_related('questions').all()
        context['sections'] = sections
        
        # Get questions without section
        questions_without_section = form_obj.questions.filter(section__isnull=True).order_by('order')
        context['questions_without_section'] = questions_without_section
        
        return context


class FormQuestionCreateView(LoginRequiredMixin, CreateView):
    model = FormQuestion
    form_class = FormQuestionForm
    template_name = 'forms/question_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the parent form instance to the form
        try:
            parent_form = Form.objects.get(pk=self.kwargs.get('pk'))
            kwargs['form_instance'] = parent_form
        except Form.DoesNotExist:
            pass
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add parent form info for the template
        try:
            parent_form = Form.objects.get(pk=self.kwargs.get('pk'))
            context['parent_form'] = parent_form
        except Form.DoesNotExist:
            pass
        return context

    def get_initial(self):
        """Pre-populate the section field if section parameter is provided"""
        initial = super().get_initial()
        section_id = self.request.GET.get('section')
        if section_id:
            try:
                section = FormSection.objects.get(pk=section_id)
                initial['section'] = section
            except FormSection.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        # Attach to parent form
        parent_form = Form.objects.get(pk=self.kwargs.get('pk'))
        form.instance.form = parent_form
        
        # Auto-assign order if not provided or is 0
        if not form.instance.order or form.instance.order == 0:
            # Get the next available order number
            max_order = parent_form.questions.aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            form.instance.order = max_order + 1
        
        # Handle options from POST data
        options = self._process_options_from_request()
        form.instance.options = options
        
        messages.success(self.request, 'Question created successfully')
        return super().form_valid(form)

    def _process_options_from_request(self):
        """Process options from the dynamic form data"""
        options = []
        option_texts = self.request.POST.getlist('option_text[]')
        option_values = self.request.POST.getlist('option_value[]')
        
        for i, text in enumerate(option_texts):
            if text.strip():  # Only add non-empty options
                value = option_values[i] if i < len(option_values) and option_values[i].strip() else text.strip()
                options.append({
                    'text': text.strip(),
                    'value': value.strip()
                })
        
        return options

    def get_success_url(self):
        return reverse_lazy('forms:questions', kwargs={'pk': self.object.form.pk})


class FormQuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = FormQuestion
    form_class = FormQuestionForm
    template_name = 'forms/question_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add parent form info for the template
        context['parent_form'] = self.object.form
        return context

    def form_valid(self, form):
        # Handle options from POST data
        options = self._process_options_from_request()
        form.instance.options = options
        
        messages.success(self.request, 'Question updated successfully')
        return super().form_valid(form)

    def _process_options_from_request(self):
        """Process options from the dynamic form data"""
        options = []
        option_texts = self.request.POST.getlist('option_text[]')
        option_values = self.request.POST.getlist('option_value[]')
        
        for i, text in enumerate(option_texts):
            if text.strip():  # Only add non-empty options
                value = option_values[i] if i < len(option_values) and option_values[i].strip() else text.strip()
                options.append({
                    'text': text.strip(),
                    'value': value.strip()
                })
        
        return options

    def get_success_url(self):
        return reverse_lazy('forms:questions', kwargs={'pk': self.object.form.pk})


class FormQuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = FormQuestion
    template_name = 'forms/question_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('forms:questions', kwargs={'pk': self.object.form.pk})


# Section Management Views
class FormSectionCreateView(LoginRequiredMixin, CreateView):
    model = FormSection
    form_class = FormSectionForm
    template_name = 'forms/section_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add parent form info for the template
        try:
            parent_form = Form.objects.get(pk=self.kwargs.get('pk'))
            context['parent_form'] = parent_form
        except Form.DoesNotExist:
            pass
        return context

    def form_valid(self, form):
        # Attach to parent form
        parent_form = Form.objects.get(pk=self.kwargs.get('pk'))
        form.instance.form = parent_form
        
        # Auto-assign order if not provided or is 0
        if not form.instance.order or form.instance.order == 0:
            # Get the next available order number
            max_order = parent_form.sections.aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            form.instance.order = max_order + 1
        
        messages.success(self.request, 'Section created successfully')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forms:questions', kwargs={'pk': self.object.form.pk})


class FormSectionUpdateView(LoginRequiredMixin, UpdateView):
    model = FormSection
    form_class = FormSectionForm
    template_name = 'forms/section_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add parent form info for the template
        context['parent_form'] = self.object.form
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Section updated successfully')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forms:questions', kwargs={'pk': self.object.form.pk})


class FormSectionDeleteView(LoginRequiredMixin, DeleteView):
    model = FormSection
    template_name = 'forms/section_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('forms:questions', kwargs={'pk': self.object.form.pk})


class FormPublishView(LoginRequiredMixin, View):
    """View to handle form publishing and unpublishing"""
    
    def get(self, request, pk):
        """Display the publish form"""
        form = get_object_or_404(Form, pk=pk, owner=request.user)
        
        context = {
            'form': form,
            'public_url': self._get_public_url(form) if form.status == 'published' else None,
        }
        
        return render(request, 'forms/publish.html', context)
    
    def post(self, request, pk):
        """Handle publish/unpublish actions"""
        form = get_object_or_404(Form, pk=pk, owner=request.user)
        action = request.POST.get('action')
        
        if action == 'publish':
            return self._publish_form(request, form)
        elif action == 'unpublish':
            return self._unpublish_form(request, form)
        elif action == 'update_settings':
            return self._update_settings(request, form)
        elif action == 'regenerate_qr':
            return self._regenerate_qr(request, form)
            
        messages.error(request, 'Invalid action.')
        return redirect('forms:publish', pk=pk)
    
    def _publish_form(self, request, form):
        """Publish the form"""
        # Check if form has questions
        if not form.questions.exists():
            messages.error(request, 'Cannot publish form without questions.')
            return redirect('forms:publish', pk=form.pk)
            
        # Update form status
        form.status = 'published'
        form.published_at = timezone.now()
        
        # Update settings from form
        password = request.POST.get('password', '').strip()
        require_captcha = request.POST.get('require_captcha') == 'on'
        
        form.password = password
        form.require_captcha = require_captcha
        
        form.save()
        
        # Generate QR code (this will be done automatically in the model's save method)
        
        messages.success(request, f'Form "{form.title}" has been published successfully!')
        return redirect('forms:publish', pk=form.pk)
    
    def _unpublish_form(self, request, form):
        """Unpublish the form"""
        form.status = 'draft'
        form.save()
        
        messages.success(request, f'Form "{form.title}" has been unpublished.')
        return redirect('forms:publish', pk=form.pk)
    
    def _update_settings(self, request, form):
        """Update form settings without changing publish status"""
        if form.status != 'published':
            messages.error(request, 'Can only update settings for published forms.')
            return redirect('forms:publish', pk=form.pk)
            
        password = request.POST.get('password', '').strip()
        require_captcha = request.POST.get('require_captcha') == 'on'
        
        form.password = password
        form.require_captcha = require_captcha
        form.save()
        
        messages.success(request, 'Form settings updated successfully!')
        return redirect('forms:publish', pk=form.pk)
    
    def _regenerate_qr(self, request, form):
        """Regenerate QR code for the form"""
        if form.status != 'published':
            messages.error(request, 'Can only regenerate QR code for published forms.')
            return redirect('forms:publish', pk=form.pk)
        
        # Delete old QR code and regenerate
        if form.qr_code:
            form.qr_code.delete(save=False)
        form.generate_qr_code()
        
        messages.success(request, 'QR code has been regenerated successfully!')
        return redirect('forms:publish', pk=form.pk)
    
    def _get_public_url(self, form):
        """Get the public URL for the form"""
        from django.urls import reverse
        # Build the absolute URL using the request object
        survey_path = reverse('responses:public_survey', kwargs={'slug': form.slug})
        return self.request.build_absolute_uri(survey_path)

class FormResponsesView(LoginRequiredMixin, DetailView):
    model = Form
    template_name = 'forms/responses.html'
    context_object_name = 'form'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_obj = self.object
        
        # Get all responses for this form
        responses_qs = form_obj.responses.select_related('user', 'record').prefetch_related('answers').all()
        responses_list = list(responses_qs)
        
        context['responses'] = responses_qs
        context['complete_count'] = responses_qs.filter(is_complete=True).count()

        attachments = form_obj.master_data_attachments.select_related('dataset').all()
        context['filter_statistics'] = self._build_filter_statistics(responses_list, attachments)

        paginator = Paginator(responses_qs, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['paginated_responses'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['latest_response'] = responses_qs.first()
        
        return context

    def _build_filter_statistics(self, responses, attachments):
        stats = []
        for attachment in attachments:
            if not attachment.filter_columns:
                continue

            column_stats = []
            for column in attachment.filter_columns:
                counter = Counter()
                for response in responses:
                    value = self._extract_filter_value(response, attachment.dataset_id, column)
                    if value:
                        counter[value] += 1

                if counter:
                    sorted_values = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
                    column_stats.append({
                        'column': column,
                        'values': [
                            {'value': val, 'count': count}
                            for val, count in sorted_values
                        ]
                    })

            if column_stats:
                stats.append({
                    'attachment': attachment,
                    'columns': column_stats
                })

        return stats

    def _extract_filter_value(self, response, dataset_id, column):
        data_source = None
        if response.record and response.record.dataset_id == dataset_id:
            data_source = response.record.data
        elif response.is_new_identity and response.new_identity_dataset_id == dataset_id:
            data_source = response.new_identity_data or {}

        if not data_source:
            return None

        raw_value = data_source.get(column)
        return self._normalize_filter_value(raw_value)

    def _normalize_filter_value(self, raw_value):
        if raw_value is None:
            return None
        if isinstance(raw_value, (list, tuple)):
            normalized = ', '.join(str(v) for v in raw_value if v is not None)
        elif isinstance(raw_value, dict):
            normalized = json.dumps(raw_value, ensure_ascii=False)
        else:
            normalized = str(raw_value).strip()

        return normalized or None


def export_responses_excel(request, pk):
    """Stream form responses as CSV to avoid large memory usage on shared hosting.

    This function replaces the previous in-memory Excel generation. It streams
    CSV rows using Django's `StreamingHttpResponse`, which keeps memory usage
    low even for large response sets. The exported filename is `.csv` for
    compatibility with Excel and other spreadsheet programs.
    """
    # Permission: only owner or editors can export
    form_obj = Form.objects.filter(
        pk=pk
    ).filter(
        models.Q(owner=request.user) | models.Q(editors=request.user)
    ).first()

    if not form_obj:
        return HttpResponse('Not found or permission denied', status=403)

    # Base response columns
    base_headers = [
        'submitted_at', 'is_complete',
        'record_display', 'is_new_identity'
    ]

    # Master data attachment columns (prefixed by dataset name)
    md_attachments = form_obj.master_data_attachments.select_related('dataset').all()
    md_columns = []  # list of (attach, col, header)
    for attach in md_attachments:
        cols = attach.get_visible_columns()
        for col in cols:
            header = f"{attach.dataset.name} - {col.name}"
            md_columns.append((attach, col, header))

    # Question headers
    questions = list(form_obj.questions.all())
    question_headers = [q.text for q in questions]

    # Build full header row
    headers = base_headers + [h for (_, _, h) in md_columns] + question_headers

    # Prepare queryset with prefetched relations
    responses_qs = form_obj.responses.select_related('user', 'record').prefetch_related('answers')
    total_responses = responses_qs.count()

    import csv
    import io
    from django.http import StreamingHttpResponse
    from datetime import datetime

    def row_generator():
        buf = io.StringIO()
        writer = csv.writer(buf)

        # First write header with UTF-8 BOM for Excel compatibility
        writer.writerow(headers)
        data = buf.getvalue()
        # Use utf-8-sig (BOM) on first chunk
        yield data.encode('utf-8-sig')
        buf.seek(0)
        buf.truncate(0)

        # Iterate responses (use normal iteration so prefetch_related applies)
        for resp in responses_qs:
            row = []
            row.append(resp.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if resp.submitted_at else '')
            row.append('Yes' if resp.is_complete else 'No')

            # For record display, try attachments' display_column if available
            record_display = ''
            if resp.record:
                for attach in md_attachments:
                    if resp.record.dataset_id == attach.dataset_id:
                        record_display = attach.get_record_display_value(resp.record)
                        break
                if not record_display:
                    record_display = str(resp.record)

            row.append(record_display)
            row.append('Yes (Pending Approval)' if (resp.is_new_identity and not resp.record) else ('Yes (Approved)' if (resp.is_new_identity and resp.record) else 'No'))

            # Master data columns values
            for attach, col, header in md_columns:
                value = ''
                if resp.record and resp.record.dataset_id == attach.dataset_id:
                    try:
                        value = resp.record.data.get(col.name, '')
                    except Exception:
                        value = ''
                elif resp.is_new_identity and resp.new_identity_dataset_id == attach.dataset_id:
                    try:
                        value = resp.new_identity_data.get(col.name, '')
                    except Exception:
                        value = ''
                row.append(value)

            # Answers: build mapping question_id -> value
            answers_map = {a.question_id: a.value for a in resp.answers.all()}
            for q in questions:
                val = answers_map.get(q.id, '')
                if isinstance(val, (dict, list)):
                    try:
                        val = json.dumps(val, ensure_ascii=False)
                    except Exception:
                        val = str(val)
                row.append(val)

            writer.writerow(row)
            data = buf.getvalue()
            yield data.encode('utf-8')
            buf.seek(0)
            buf.truncate(0)

    # Build filename and response
    current_date = datetime.now().strftime('%Y-%m-%d')
    filename = f"{form_obj.slug or slugify(form_obj.title)}-responses-{current_date}.csv"
    response = StreamingHttpResponse(row_generator(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    # Expose total responses in a header so clients can verify download completeness
    response['X-Total-Responses'] = str(total_responses)

    return response

class FormQRCodeView(DetailView):
    model = Form
    template_name = 'forms/qr_code.html'
    slug_field = 'slug'
    context_object_name = 'form'
    
    def get_object(self, queryset=None):
        """Get the form object and ensure it's published"""
        obj = super().get_object(queryset)
        if obj.status != 'published':
            from django.http import Http404
            raise Http404("Form is not published")
        
        # Generate QR code if it doesn't exist
        if not obj.qr_code:
            obj.generate_qr_code()
            obj.refresh_from_db()
            
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_obj = self.object
        
        # Get the public URL using settings.SITE_URL
        from django.urls import reverse
        from django.conf import settings
        survey_path = reverse('responses:public_survey', kwargs={'slug': form_obj.slug})
        context['public_url'] = f"{settings.SITE_URL}{survey_path}"
        
        return context


# HTMX Views for Master Data Attachment
class MasterDataAttachmentListView(LoginRequiredMixin, View):
    """HTMX view to list available master data sets for attachment"""
    
    def get(self, request, pk):
        form_obj = get_object_or_404(Form, pk=pk, owner=request.user)
        
        # Get master data sets that user owns or has access to
        from master_data.models import MasterDataSet
        available_datasets = MasterDataSet.objects.filter(
            models.Q(owner=request.user) | 
            models.Q(shared_with=request.user)
        ).exclude(
            id__in=form_obj.master_data_attachments.values_list('dataset_id', flat=True)
        ).distinct()
        
        context = {
            'form': form_obj,
            'available_datasets': available_datasets
        }
        
        return render(request, 'forms/partials/master_data_attachment_list.html', context)


class MasterDataAttachView(LoginRequiredMixin, View):
    """HTMX view to attach a master data set to a form"""
    
    def post(self, request, pk):
        form_obj = get_object_or_404(Form, pk=pk, owner=request.user)
        dataset_id = request.POST.get('dataset_id')
        
        if not dataset_id:
            return JsonResponse({'error': 'Dataset ID is required'}, status=400)
        
        from master_data.models import MasterDataSet
        try:
            # Check if dataset exists and user has access
            dataset = MasterDataSet.objects.filter(
                id=dataset_id
            ).filter(
                models.Q(owner=request.user) | models.Q(shared_with=request.user)
            ).first()
            
            if not dataset:
                return JsonResponse({'error': 'Dataset not found or access denied'}, status=404)
                
        except Exception as e:
            return JsonResponse({'error': f'Error: {str(e)}'}, status=500)
        
        # Check if already attached
        if FormMasterDataAttachment.objects.filter(form=form_obj, dataset=dataset).exists():
            return JsonResponse({'error': 'Dataset is already attached to this form'}, status=400)
        
        # Create attachment
        FormMasterDataAttachment.objects.create(
            form=form_obj,
            dataset=dataset,
            order=form_obj.master_data_attachments.count()
        )
        
        # Return updated attachments list
        context = {
            'form': form_obj,
            'master_data_attachments': form_obj.master_data_attachments.select_related('dataset').all()
        }
        
        return render(request, 'forms/partials/master_data_attachments.html', context)


class MasterDataDetachView(LoginRequiredMixin, View):
    """HTMX view to detach a master data set from a form"""
    
    def delete(self, request, pk, attachment_id):
        form_obj = get_object_or_404(Form, pk=pk, owner=request.user)
        attachment = get_object_or_404(
            FormMasterDataAttachment, 
            id=attachment_id, 
            form=form_obj
        )
        
        attachment.delete()
        
        # Return updated attachments list
        context = {
            'form': form_obj,
            'master_data_attachments': form_obj.master_data_attachments.select_related('dataset').all()
        }
        
        return render(request, 'forms/partials/master_data_attachments.html', context)


class MasterDataAttachmentConfigureView(LoginRequiredMixin, View):
    """HTMX view to configure a master data attachment"""
    
    def get(self, request, pk, attachment_id):
        form_obj = get_object_or_404(Form, pk=pk, owner=request.user)
        attachment = get_object_or_404(
            FormMasterDataAttachment, 
            id=attachment_id, 
            form=form_obj
        )
        
        context = {
            'form': form_obj,
            'attachment': attachment,
            'available_columns': attachment.dataset.columns.all()
        }
        
        return render(request, 'forms/partials/attachment_configure.html', context)
    
    def post(self, request, pk, attachment_id):
        form_obj = get_object_or_404(Form, pk=pk, owner=request.user)
        attachment = get_object_or_404(
            FormMasterDataAttachment, 
            id=attachment_id, 
            form=form_obj
        )
        
        # Update the attachment configuration
        display_column = request.POST.get('display_column', '')
        hidden_columns = request.POST.getlist('hidden_columns')
        filter_columns = [col for col in request.POST.getlist('filter_columns') if col]
        
        attachment.display_column = display_column if display_column else None
        attachment.hidden_columns = hidden_columns
        attachment.filter_columns = filter_columns
        attachment.save()
        
        # Return updated attachments list
        context = {
            'form': form_obj,
            'master_data_attachments': form_obj.master_data_attachments.select_related('dataset').all()
        }
        
        return render(request, 'forms/partials/master_data_attachments.html', context)


@require_http_methods(["POST"])
def reorder_question(request, pk):
    """Reorder a question up or down"""
    question = get_object_or_404(FormQuestion, pk=pk)
    direction = request.POST.get('direction')  # 'up' or 'down'
    
    # Get all questions in the same context (same section or no section)
    if question.section:
        questions = list(question.section.questions.order_by('order', 'id'))
    else:
        questions = list(question.form.questions.filter(section__isnull=True).order_by('order', 'id'))
    
    # Find current index
    try:
        current_index = questions.index(question)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Question not found'})
    
    # Determine target index
    if direction == 'up' and current_index > 0:
        target_index = current_index - 1
    elif direction == 'down' and current_index < len(questions) - 1:
        target_index = current_index + 1
    else:
        return JsonResponse({'success': False, 'error': 'Cannot move in that direction'})
    
    # Swap orders
    with transaction.atomic():
        target_question = questions[target_index]
        question.order, target_question.order = target_question.order, question.order
        question.save(update_fields=['order'])
        target_question.save(update_fields=['order'])
    
    return JsonResponse({'success': True})


@require_http_methods(["POST"])
def reorder_section(request, pk):
    """Reorder a section up or down"""
    section = get_object_or_404(FormSection, pk=pk)
    direction = request.POST.get('direction')  # 'up' or 'down'
    
    # Get all sections for this form
    sections = list(section.form.sections.order_by('order', 'id'))
    
    # Find current index
    try:
        current_index = sections.index(section)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Section not found'})
    
    # Determine target index
    if direction == 'up' and current_index > 0:
        target_index = current_index - 1
    elif direction == 'down' and current_index < len(sections) - 1:
        target_index = current_index + 1
    else:
        return JsonResponse({'success': False, 'error': 'Cannot move in that direction'})
    
    # Swap orders
    with transaction.atomic():
        target_section = sections[target_index]
        section.order, target_section.order = target_section.order, section.order
        section.save(update_fields=['order'])
        target_section.save(update_fields=['order'])
    
    return JsonResponse({'success': True})
