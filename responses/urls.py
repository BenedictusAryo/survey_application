from django.urls import path
from . import views

app_name = 'responses'

urlpatterns = [
    path('<slug:slug>/', views.PublicSurveyView.as_view(), name='public_survey'),
    path('<slug:slug>/submit/', views.SurveySubmitView.as_view(), name='submit'),
    path('<slug:slug>/thank-you/', views.SurveyThankYouView.as_view(), name='thank_you'),
]