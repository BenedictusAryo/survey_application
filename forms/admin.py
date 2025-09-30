from django.contrib import admin
from .models import Form, FormQuestion, FormCollaboration, FormMasterDataAttachment

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'created_at', 'published_at')
    list_filter = ('status', 'created_at', 'published_at')
    search_fields = ('title', 'description', 'owner__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('qr_code', 'created_at', 'updated_at')

@admin.register(FormQuestion)
class FormQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'form', 'question_type', 'order', 'is_required')
    list_filter = ('question_type', 'is_required', 'form')
    search_fields = ('text', 'form__title')
    list_editable = ('order', 'is_required')

@admin.register(FormCollaboration)
class FormCollaborationAdmin(admin.ModelAdmin):
    list_display = ('form', 'user', 'invited_at')
    list_filter = ('invited_at',)
    search_fields = ('form__title', 'user__username')

@admin.register(FormMasterDataAttachment)
class FormMasterDataAttachmentAdmin(admin.ModelAdmin):
    list_display = ('form', 'dataset', 'order')
    list_filter = ('form', 'dataset')
    search_fields = ('form__title', 'dataset__name')
    list_editable = ('order',)
