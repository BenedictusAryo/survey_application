from django.urls import path
from . import views

app_name = 'master_data'

urlpatterns = [
    path('', views.MasterDataListView.as_view(), name='list'),
    path('create/', views.MasterDataCreateView.as_view(), name='create'),
    path('<int:pk>/', views.MasterDataDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.MasterDataEditView.as_view(), name='edit'),
    path('<int:pk>/import/', views.MasterDataImportView.as_view(), name='import'),
    path('<int:pk>/share/', views.MasterDataShareView.as_view(), name='share'),
]