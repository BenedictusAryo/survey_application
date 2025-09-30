from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, CreateView, TemplateView
from django.http import JsonResponse
from .models import Response, ResponseAnswer
from forms.models import Form

class PublicSurveyView(DetailView):
    model = Form
    template_name = 'responses/public_survey.html'
    slug_field = 'slug'
    context_object_name = 'form'
    
    def get_queryset(self):
        return Form.objects.filter(status='published')

class SurveySubmitView(CreateView):
    model = Response
    fields = []
    template_name = 'responses/submit.html'
    
    def post(self, request, *args, **kwargs):
        form = get_object_or_404(Form, slug=kwargs['slug'], status='published')
        # Handle survey submission
        return JsonResponse({'success': True})

class SurveyThankYouView(TemplateView):
    template_name = 'responses/thank_you.html'
