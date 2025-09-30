from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Form, FormQuestion

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
