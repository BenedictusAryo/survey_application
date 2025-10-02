from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Response, ResponseAnswer
from master_data.models import MasterDataRecord, MasterDataSet

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'form', 'user', 'is_complete', 'is_new_identity', 'new_identity_status', 'submitted_at')
    list_filter = ('is_complete', 'is_new_identity', 'submitted_at', 'form')
    search_fields = ('form__title', 'user__username')
    readonly_fields = ('submitted_at', 'updated_at', 'display_new_identity_data')
    actions = ['approve_new_identity']
    
    fieldsets = (
        ('Response Information', {
            'fields': ('form', 'user', 'record', 'is_complete', 'submitted_at', 'updated_at')
        }),
        ('New Identity Data', {
            'fields': ('is_new_identity', 'new_identity_dataset_id', 'display_new_identity_data'),
            'classes': ('collapse',),
        }),
        ('Tracking Information', {
            'fields': ('session_key', 'ip_address', 'user_agent'),
            'classes': ('collapse',),
        }),
    )
    
    def new_identity_status(self, obj):
        """Show status of new identity data"""
        if not obj.is_new_identity:
            return '-'
        if obj.record:
            return format_html('<span style="color: green;">✓ Approved</span>')
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    new_identity_status.short_description = 'Identity Status'
    
    def display_new_identity_data(self, obj):
        """Display new identity data in a readable format"""
        if not obj.is_new_identity or not obj.new_identity_data:
            return '-'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #f0f0f0;"><th style="padding: 5px; text-align: left;">Field</th><th style="padding: 5px; text-align: left;">Value</th></tr>'
        for key, value in obj.new_identity_data.items():
            html += f'<tr><td style="padding: 5px; border-top: 1px solid #ddd;"><strong>{key}</strong></td><td style="padding: 5px; border-top: 1px solid #ddd;">{value}</td></tr>'
        html += '</table>'
        
        if not obj.record:
            html += '<br><p style="color: orange;"><strong>⚠️ This identity has not been added to master data yet. Use "Approve new identity" action to add it.</strong></p>'
        else:
            html += f'<br><p style="color: green;"><strong>✓ This identity has been approved and added to master data (Record #{obj.record.id}).</strong></p>'
        
        return format_html(html)
    display_new_identity_data.short_description = 'New Identity Data'
    
    def approve_new_identity(self, request, queryset):
        """Approve and add new identity data to master data"""
        approved_count = 0
        skipped_count = 0
        
        for response in queryset:
            if not response.is_new_identity or not response.new_identity_data:
                skipped_count += 1
                continue
            
            if response.record:
                # Already approved
                skipped_count += 1
                continue
            
            try:
                # Create master data record
                dataset = MasterDataSet.objects.get(id=response.new_identity_dataset_id)
                new_record = MasterDataRecord.objects.create(
                    dataset=dataset,
                    data=response.new_identity_data
                )
                
                # Link response to the new record
                response.record = new_record
                response.save()
                
                approved_count += 1
            except Exception as e:
                messages.error(request, f'Error approving response #{response.id}: {str(e)}')
        
        if approved_count > 0:
            messages.success(request, f'Successfully approved {approved_count} new identity/identities.')
        if skipped_count > 0:
            messages.info(request, f'Skipped {skipped_count} response(s) (already approved or no new identity data).')
    
    approve_new_identity.short_description = 'Approve new identity and add to master data'

@admin.register(ResponseAnswer)
class ResponseAnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'value', 'created_at')
    list_filter = ('created_at', 'question__question_type')
    search_fields = ('response__form__title', 'question__text')
