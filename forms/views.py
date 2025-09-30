
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
 
from .models import Form, FormQuestion
from .forms import FormQuestionForm

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
        
        # Get questions
        context['questions'] = form_obj.questions.all()
        
        # Get response count
        context['response_count'] = form_obj.responses.count()
        
        # Get collaborators
        context['collaborators'] = form_obj.editors.all()
        
        return context

class FormEditView(LoginRequiredMixin, UpdateView):
    model = Form
    fields = ['title', 'description']
    template_name = 'forms/edit.html'
    context_object_name = 'form'
    
    def get_success_url(self):
        return reverse_lazy('forms:detail', kwargs={'pk': self.object.pk})

class FormQuestionEditView(LoginRequiredMixin, DetailView):
    model = Form
    template_name = 'forms/questions.html'
    context_object_name = 'form'


class FormQuestionCreateView(LoginRequiredMixin, CreateView):
    model = FormQuestion
    form_class = FormQuestionForm
    template_name = 'forms/question_form.html'

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

class FormPublishView(LoginRequiredMixin, DetailView):
    model = Form
    template_name = 'forms/publish.html'
    context_object_name = 'form'

class FormResponsesView(LoginRequiredMixin, DetailView):
    model = Form
    template_name = 'forms/responses.html'
    context_object_name = 'form'

class FormQRCodeView(DetailView):
    model = Form
    template_name = 'forms/qr_code.html'
    slug_field = 'slug'
    context_object_name = 'form'
