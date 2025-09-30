from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
import pandas as pd
import csv
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

    def get_context_data(self, **kwargs):
        """Add paginated records to the template context as `records_page`.

        Pagination is controlled by the `page` query parameter and shows 20
        records per page by default.
        """
        context = super().get_context_data(**kwargs)
        dataset = self.object

        records_qs = dataset.records.all().order_by('id')
        paginator = Paginator(records_qs, 20)
        page = self.request.GET.get('page')
        try:
            records_page = paginator.page(page)
        except PageNotAnInteger:
            records_page = paginator.page(1)
        except EmptyPage:
            records_page = paginator.page(paginator.num_pages)

        context['records_page'] = records_page
        return context

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
    
    def post(self, request, *args, **kwargs):
        dataset = self.get_object()
        # Ensure DetailView helpers that rely on self.object work in POST
        self.object = dataset
        
        if 'file' not in request.FILES:
            messages.error(request, 'No file uploaded.')
            return self.get(request, *args, **kwargs)
        
        file = request.FILES['file']
        has_header = request.POST.get('has_header') == 'on'
        
        try:
            # Read file based on extension
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, header=0 if has_header else None)
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file, header=0 if has_header else None)
            else:
                messages.error(request, 'Unsupported file format. Please use CSV or Excel files.')
                return self.get(request, *args, **kwargs)
            
            # Convert all data to strings to ensure JSON serializability
            df = df.astype(str)
            
            # Convert to list of dicts for preview
            preview_data = df.fillna('').to_dict('records')
            file_columns = list(df.columns)
            
            # Store in session for confirmation step
            request.session['import_preview'] = {
                'data': preview_data,
                'columns': file_columns,
                'dataset_id': dataset.id
            }
            
            context = self.get_context_data()
            context['preview_data'] = preview_data[:50]  # Limit preview
            context['file_columns'] = file_columns
            
            return self.render_to_response(context)
            
        except Exception as e:
            messages.error(request, f'Error reading file: {str(e)}')
            return self.get(request, *args, **kwargs)

def import_confirm(request, pk):
    """Confirm and execute the import"""
    if request.method != 'POST':
        return redirect('master_data:import', pk=pk)
    
    dataset = get_object_or_404(MasterDataSet, pk=pk, owner=request.user)
    
    # Get preview data from session
    import_data = request.session.get('import_preview')
    if not import_data or import_data['dataset_id'] != dataset.id:
        messages.error(request, 'Import session expired. Please upload the file again.')
        return redirect('master_data:import', pk=pk)
    
    try:
        # Get column mappings
        mappings = {}
        for key, value in request.POST.items():
            if key.startswith('mapping_') and value:
                file_col = key.replace('mapping_', '')
                if value.startswith('_create_new_'):
                    # Create new column
                    new_col_name = value.replace('_create_new_', '')
                    column, created = MasterDataColumn.objects.get_or_create(
                        dataset=dataset,
                        name=new_col_name,
                        defaults={'data_type': 'text', 'order': dataset.columns.count()}
                    )
                    mappings[file_col] = new_col_name
                else:
                    mappings[file_col] = value
        
        # Import records
        imported_count = 0
        for row_data in import_data['data']:
            # Map data according to column mappings
            mapped_data = {}
            for file_col, db_col in mappings.items():
                if file_col in row_data:
                    mapped_data[db_col] = row_data[file_col]
            
            if mapped_data:  # Only create if we have data
                MasterDataRecord.objects.create(
                    dataset=dataset,
                    data=mapped_data
                )
                imported_count += 1
        
        # Clear session
        del request.session['import_preview']
        
        messages.success(request, f'Successfully imported {imported_count} records.')
        return redirect('master_data:detail', pk=pk)
        
    except Exception as e:
        messages.error(request, f'Error during import: {str(e)}')
        return redirect('master_data:import', pk=pk)

class MasterDataShareView(LoginRequiredMixin, DetailView):
    model = MasterDataSet
    template_name = 'master_data/share.html'
    context_object_name = 'dataset'

def export_csv(request, pk):
    """Export master data as CSV"""
    dataset = get_object_or_404(MasterDataSet, pk=pk, owner=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{dataset.name}.csv"'
    
    # Get all columns
    columns = list(dataset.columns.values_list('name', flat=True))
    
    if not columns:
        # No columns defined
        writer = csv.writer(response)
        writer.writerow(['No columns defined'])
        return response
    
    writer = csv.writer(response)
    writer.writerow(columns)
    
    # Write data rows
    for record in dataset.records.all():
        row = []
        for col in columns:
            row.append(record.data.get(col, ''))
        writer.writerow(row)
    
    return response
