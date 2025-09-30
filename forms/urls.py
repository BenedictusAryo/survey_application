from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    path('', views.FormListView.as_view(), name='list'),
    path('create/', views.FormCreateView.as_view(), name='create'),
    path('<int:pk>/', views.FormDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.FormEditView.as_view(), name='edit'),
    path('<int:pk>/questions/', views.FormQuestionEditView.as_view(), name='questions'),
    path('<int:pk>/publish/', views.FormPublishView.as_view(), name='publish'),
    path('<int:pk>/responses/', views.FormResponsesView.as_view(), name='responses'),
    path('<slug:slug>/qr/', views.FormQRCodeView.as_view(), name='qr_code'),
]