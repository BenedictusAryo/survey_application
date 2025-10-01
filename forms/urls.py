from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    path('', views.FormListView.as_view(), name='list'),
    path('create/', views.FormCreateView.as_view(), name='create'),
    path('<int:pk>/', views.FormDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.FormEditView.as_view(), name='edit'),
    path('<int:pk>/questions/', views.FormQuestionEditView.as_view(), name='questions'),
    path('<int:pk>/questions/add/', views.FormQuestionCreateView.as_view(), name='question_add'),
    path('questions/<int:pk>/edit/', views.FormQuestionUpdateView.as_view(), name='question_edit'),
    path('questions/<int:pk>/delete/', views.FormQuestionDeleteView.as_view(), name='question_delete'),
    path('<int:pk>/publish/', views.FormPublishView.as_view(), name='publish'),
    path('<int:pk>/responses/', views.FormResponsesView.as_view(), name='responses'),
    path('<slug:slug>/qr/', views.FormQRCodeView.as_view(), name='qr_code'),
    
    # HTMX endpoints for master data attachment
    path('<int:pk>/master-data/available/', views.MasterDataAttachmentListView.as_view(), name='master_data_available'),
    path('<int:pk>/master-data/attach/', views.MasterDataAttachView.as_view(), name='master_data_attach'),
    path('<int:pk>/master-data/detach/<int:attachment_id>/', views.MasterDataDetachView.as_view(), name='master_data_detach'),
]