from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import MasterDataSet, MasterDataColumn, MasterDataRecord

class MasterDataListView(LoginRequiredMixin, ListView):
    model = MasterDataSet
    template_name = 'master_data/list.html'
    context_object_name = 'datasets'
    
    def get_queryset(self):
        return MasterDataSet.objects.filter(owner=self.request.user)

class MasterDataCreateView(LoginRequiredMixin, CreateView):
    model = MasterDataSet
    fields = ['name', 'description']
    template_name = 'master_data/create.html'
    success_url = reverse_lazy('master_data:list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f'Master data set "{form.instance.name}" created successfully!')
        return super().form_valid(form)

class MasterDataDetailView(LoginRequiredMixin, DetailView):
    model = MasterDataSet
    template_name = 'master_data/detail.html'
    context_object_name = 'dataset'

class MasterDataEditView(LoginRequiredMixin, UpdateView):
    model = MasterDataSet
    fields = ['name', 'description']
    template_name = 'master_data/edit.html'
    context_object_name = 'dataset'
    
    def get_success_url(self):
        return reverse_lazy('master_data:detail', kwargs={'pk': self.object.pk})

class MasterDataImportView(LoginRequiredMixin, DetailView):
    model = MasterDataSet
    template_name = 'master_data/import.html'
    context_object_name = 'dataset'

class MasterDataShareView(LoginRequiredMixin, DetailView):
    model = MasterDataSet
    template_name = 'master_data/share.html'
    context_object_name = 'dataset'
