from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, CreateView, TemplateView, FormView
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from captcha.fields import CaptchaField
from captcha.models import CaptchaStore
from django import forms
import json
from .models import Response, ResponseAnswer
from forms.models import Form, FormQuestion

class PasswordForm(forms.Form):
    """Form for password protection"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input input-bordered w-full',
        'placeholder': 'Enter form password'
    }))

class SurveyResponseForm(forms.Form):
    """Dynamic form for survey responses"""
    captcha = CaptchaField()
    
    def __init__(self, *args, **kwargs):
        form_obj = kwargs.pop('form_obj', None)
        super().__init__(*args, **kwargs)
        
        if form_obj and not form_obj.require_captcha:
            del self.fields['captcha']
        
        # Add dynamic fields based on form questions
        if form_obj:
            for question in form_obj.questions.all():
                field_name = f'question_{question.id}'
                
                if question.question_type == 'text_input':
                    self.fields[field_name] = forms.CharField(
                        label=question.text,
                        required=question.is_required,
                        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
                    )
                elif question.question_type == 'numeric_input':
                    self.fields[field_name] = forms.IntegerField(
                        label=question.text,
                        required=question.is_required,
                        widget=forms.NumberInput(attrs={'class': 'input input-bordered w-full'})
                    )
                elif question.question_type == 'date_input':
                    self.fields[field_name] = forms.DateField(
                        label=question.text,
                        required=question.is_required,
                        widget=forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'})
                    )
                elif question.question_type in ['single_select', 'image_select']:
                    choices = [(opt.get('value', ''), opt.get('text', '')) for opt in question.options]
                    self.fields[field_name] = forms.ChoiceField(
                        label=question.text,
                        choices=choices,
                        required=question.is_required,
                        widget=forms.RadioSelect(attrs={'class': 'radio'})
                    )
                elif question.question_type == 'multi_select':
                    choices = [(opt.get('value', ''), opt.get('text', '')) for opt in question.options]
                    self.fields[field_name] = forms.MultipleChoiceField(
                        label=question.text,
                        choices=choices,
                        required=question.is_required,
                        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox'})
                    )

@method_decorator(ratelimit(key='ip', rate='10/m', method='GET'), name='get')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='post')
class PublicSurveyView(FormView):
    template_name = 'responses/public_survey.html'
    form_class = SurveyResponseForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['form_obj'] = self.get_form_object()
        return kwargs
    
    def get_form_object(self):
        return get_object_or_404(Form, slug=self.kwargs['slug'], status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_obj = self.get_form_object()
        
        # Check if password is required and not provided
        if form_obj.password and not self.request.session.get(f'form_access_{form_obj.slug}'):
            context['require_password'] = True
            context['password_form'] = PasswordForm()
            return context
        
        context['survey_form'] = form_obj
        context['questions'] = form_obj.questions.all()
        context['master_data_attachments'] = form_obj.master_data_attachments.all()
        return context
    
    def post(self, request, *args, **kwargs):
        form_obj = self.get_form_object()
        
        # Ensure session exists
        if not request.session.session_key:
            request.session.save()
        
        # Handle password authentication
        if 'password' in request.POST:
            password_form = PasswordForm(request.POST)
            if password_form.is_valid():
                if password_form.cleaned_data['password'] == form_obj.password:
                    request.session[f'form_access_{form_obj.slug}'] = True
                    return redirect(request.path)
                else:
                    messages.error(request, 'Incorrect password.')
            return self.get(request, *args, **kwargs)
        
        # Handle survey submission directly (bypass Django form validation for now)
        try:
            return self.handle_survey_submission(form_obj)
        except Exception as e:
            messages.error(request, f'Error submitting survey: {str(e)}')
            return self.get(request, *args, **kwargs)
    
    def handle_survey_submission(self, form_obj):
        """Handle the survey submission directly from POST data"""
        # Create response record
        response = Response.objects.create(
            form=form_obj,
            session_key=self.request.session.session_key,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            is_complete=True
        )
        
        # Save answers from POST data
        for key in self.request.POST.keys():
            if key.startswith('question_'):
                question_id = int(key.replace('question_', ''))
                try:
                    question = FormQuestion.objects.get(id=question_id)
                    # Get all values for this question (handles multi-select)
                    values = self.request.POST.getlist(key)
                    if values:
                        # Join multiple values with comma for multi-select
                        value = ', '.join(values) if len(values) > 1 else values[0]
                        ResponseAnswer.objects.create(
                            response=response,
                            question=question,
                            value=str(value) if value else ''
                        )
                except FormQuestion.DoesNotExist:
                    continue
        
        return redirect('responses:thank_you', slug=form_obj.slug)
    
    def form_valid(self, form):
        form_obj = self.get_form_object()
        
        # Ensure session exists
        if not self.request.session.session_key:
            self.request.session.save()
        
        # Create response record
        response = Response.objects.create(
            form=form_obj,
            session_key=self.request.session.session_key,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            is_complete=True
        )
        
        # Save answers
        for field_name, value in form.cleaned_data.items():
            if field_name.startswith('question_') and field_name != 'captcha':
                question_id = int(field_name.replace('question_', ''))
                try:
                    question = FormQuestion.objects.get(id=question_id)
                    # Handle multi-select values
                    if isinstance(value, list):
                        value = ', '.join(value)
                    ResponseAnswer.objects.create(
                        response=response,
                        question=question,
                        value=str(value) if value is not None else ''
                    )
                except FormQuestion.DoesNotExist:
                    continue
        
        return redirect('responses:thank_you', slug=form_obj.slug)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class SurveySubmitView(CreateView):
    model = Response
    fields = []
    template_name = 'responses/submit.html'
    
    def post(self, request, *args, **kwargs):
        # This view is currently not implemented
        # Form submission is handled by PublicSurveyView
        return JsonResponse({'success': True})

class SurveyThankYouView(TemplateView):
    template_name = 'responses/thank_you.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_obj = get_object_or_404(Form, slug=self.kwargs['slug'])
        context['survey_form'] = form_obj
        return context
