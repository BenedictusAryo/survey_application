from django.contrib import admin
from .models import Form, FormQuestion, FormCollaboration, FormMasterDataAttachment, QuestionOption

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'require_captcha', 'created_at', 'published_at')
    list_filter = ('status', 'require_captcha', 'created_at', 'published_at')
    search_fields = ('title', 'description', 'owner__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('qr_code', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'owner', 'status')
        }),
        ('Security Settings', {
            'fields': ('password', 'require_captcha'),
            'description': 'Configure access control and security features'
        }),
        ('Appearance', {
            'fields': ('form_image',),
            'description': 'Customize the visual appearance of your form'
        }),
        ('Advanced', {
            'fields': ('form_settings', 'qr_code'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',),
        }),
    )

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1
    fields = ('text', 'value', 'image', 'order')

@admin.register(FormQuestion)
class FormQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'form', 'question_type', 'order', 'is_required')
    list_filter = ('question_type', 'is_required', 'form')
    search_fields = ('text', 'form__title')
    list_editable = ('order', 'is_required')
    inlines = [QuestionOptionInline]
    
    fieldsets = (
        ('Question Details', {
            'fields': ('form', 'text', 'question_type', 'order', 'is_required')
        }),
        ('Options & Logic', {
            'fields': ('options', 'logic'),
            'description': 'Configure answer options and conditional logic'
        }),
        ('Media', {
            'fields': ('image',),
            'description': 'Add images to enhance your question'
        }),
    )

@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'value', 'order', 'has_image')
    list_filter = ('question__form', 'question__question_type')
    search_fields = ('text', 'value', 'question__text')
    list_editable = ('order',)
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'

@admin.register(FormCollaboration)
class FormCollaborationAdmin(admin.ModelAdmin):
    list_display = ('form', 'user', 'invited_at')
    list_filter = ('invited_at',)
    search_fields = ('form__title', 'user__username')

@admin.register(FormMasterDataAttachment)
class FormMasterDataAttachmentAdmin(admin.ModelAdmin):
    list_display = ('form', 'dataset', 'order', 'hidden_columns_display')
    list_filter = ('form', 'dataset')
    search_fields = ('form__title', 'dataset__name')
    list_editable = ('order',)

    def hidden_columns_display(self, obj):
        return ', '.join(obj.hidden_columns or [])
    hidden_columns_display.short_description = 'Hidden columns'
