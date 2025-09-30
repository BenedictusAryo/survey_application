from django.contrib import admin
from .models import MasterDataSet, MasterDataColumn, MasterDataRecord, MasterDataSetShare

@admin.register(MasterDataSet)
class MasterDataSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__username')
    raw_id_fields = ('owner',)

@admin.register(MasterDataColumn)
class MasterDataColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'dataset', 'data_type', 'order', 'is_required')
    list_filter = ('data_type', 'is_required')
    search_fields = ('name', 'dataset__name')
    list_editable = ('order', 'is_required')

@admin.register(MasterDataRecord)
class MasterDataRecordAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'dataset', 'created_at')
    list_filter = ('dataset', 'created_at')
    search_fields = ('dataset__name',)

@admin.register(MasterDataSetShare)
class MasterDataSetShareAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'user', 'can_edit', 'shared_at')
    list_filter = ('can_edit', 'shared_at')
    search_fields = ('dataset__name', 'user__username')
